odoo.define('viin_loyalty_pos.models', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    var _super_orderline = models.Orderline;
    var utils = require('web.utils');
    var core = require('web.core');
    var round_pr = utils.round_precision;
    var _t = core._t;

    models.load_fields('res.partner', 'loyalty_points');

    models.load_models([
        {
            model: 'loyalty.program',
            condition: function (self) { return !!self.config.loyalty_id[0]; },
            fields: ['name', 'pp_currency', 'pp_product', 'pp_order', 'rounding'],
            domain: function (self) { return [['id', '=', self.config.loyalty_id[0]]]; },
            loaded: function (self, loyalties) {
                self.loyalty = loyalties[0];
            },
        }, {
            model: 'loyalty.rule',
            condition: function (self) { return !!self.loyalty; },
            fields: ['name', 'rule_type', 'product_id', 'pos_category_id', 'cumulative', 'pp_product', 'pp_currency'],
            domain: function (self) { return [['loyalty_program_id', '=', self.loyalty.id]]; },
            loaded: function (self, rules) {

                self.loyalty.rules = rules;
                self.loyalty.rules_by_product_id = {};
                self.loyalty.rules_by_category_id = {};

                for (var i = 0; i < rules.length; i++) {
                    var rule = rules[i];
                    if (rule.rule_type === 'product') {
                        if (!self.loyalty.rules_by_product_id[rule.product_id[0]]) {
                            self.loyalty.rules_by_product_id[rule.product_id[0]] = [rule];
                        } else if (rule.cumulative) {
                            self.loyalty.rules_by_product_id[rule.product_id[0]].unshift(rule);
                        } else {
                            self.loyalty.rules_by_product_id[rule.product_id[0]].push(rule);
                        }
                    } else if (rule.rule_type === 'pos_category') {
                        if (!self.loyalty.rules_by_category_id[rule.pos_category_id[0]]) {
                            self.loyalty.rules_by_category_id[rule.pos_category_id[0]] = [rule];
                        } else if (rule.cumulative) {
                            self.loyalty.rules_by_category_id[rule.pos_category_id[0]].unshift(rule);
                        } else {
                            self.loyalty.rules_by_category_id[rule.pos_category_id[0]].push(rule);
                        }
                    }
                }
            },
        }, {
            model: 'loyalty.reward',
            condition: function (self) { return !!self.loyalty; },
            fields: ['name', 'reward_type', 'minimum_points', 'gift_product_id', 'point_cost', 'discount_product_id', 'discount'],
            domain: function (self) { return [['loyalty_program_id', '=', self.loyalty.id]]; },
            loaded: function (self, rewards) {
                self.loyalty.rewards = rewards;
                self.loyalty.rewards_by_id = {};
                for (var i = 0; i < rewards.length; i++) {
                    self.loyalty.rewards_by_id[rewards[i].id] = rewards[i];
                }
            },
        },
    ], { 'after': 'product.product' });

    models.Orderline = models.Orderline.extend({
        get_reward: function () {
            return this.pos.loyalty.rewards_by_id[this.reward_id];
        },
        set_reward: function (reward) {
            this.reward_id = reward.id;
        },
        get_won_points: function () {
            if (!this.pos.loyalty || !this.order.get_client()) {
                return 0;
            }
            var rounding = this.pos.loyalty.rounding;
            var product_sold = 0;
            var total_sold = 0;
            var total_points = 0;

            var product = this.get_product();
            var rules = this.pos.loyalty.rules_by_product_id[product.id] || [];
            var overriden = false;

            if (this.get_reward()) {  // Reward products are ignored
                return 0;
            }

            for (var j = 0; j < rules.length; j++) {
                var rule = rules[j];
                total_points += round_pr(this.get_quantity() * rule.pp_product, rounding);
                total_points += round_pr(this.get_price_without_tax() * rule.pp_currency, rounding);
                // if affected by a non cumulative rule, skip the others. (non cumulative rules are put
                // at the beginning of the list when they are loaded )
                if (!rule.cumulative) {
                    overriden = true;
                    break;
                }
            }

            // Test the category rules
            if (product.pos_categ_id) {
                var category = this.pos.db.get_category_by_id(product.pos_categ_id[0]);
                while (category && !overriden) {
                    var rules = this.pos.loyalty.rules_by_category_id[category.id] || [];
                    for (var j = 0; j < rules.length; j++) {
                        var rule = rules[j];
                        total_points += round_pr(this.get_quantity() * rule.pp_product, rounding);
                        total_points += round_pr(this.get_price_without_tax() * rule.pp_currency, rounding);
                        if (!rule.cumulative) {
                            overriden = true;
                            break;
                        }
                    }
                    var _category = category;
                    category = this.pos.db.get_category_by_id(this.pos.db.get_category_parent_id(category.id));
                    if (_category === category) {
                        break;
                    }
                }
            }

            if (!overriden) {
                product_sold = this.get_quantity();
                total_sold = this.get_price_without_tax();
            }

            total_points += round_pr(total_sold * this.pos.loyalty.pp_currency, rounding);
            total_points += round_pr(product_sold * this.pos.loyalty.pp_product, rounding);
            return total_points;

        },
        /* The total number of points spent on rewards */
        get_spent_points: function () {
            if (!this.pos.loyalty || !this.order.get_client()) {
                return 0;
            } else {
                var rounding = this.pos.loyalty.rounding;
                var points = 0;

                var reward = this.get_reward();
                if (reward) {
                    if (reward.reward_type === 'gift') {
                        points += round_pr(this.get_quantity() * reward.point_cost, rounding);
                    } else if (reward.reward_type === 'discount') {
                        points += round_pr(this.get_display_price() * reward.point_cost, rounding);
                    }
                }
                return points;
            }
        },

        /* The total number of points lost or won after the order is validated */
        get_new_points: function () {
            if (!this.pos.loyalty || !this.order.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_won_points() + this.get_spent_points(), this.pos.loyalty.rounding);
            }
        },
        export_as_JSON: function () {
            var json = _super_orderline.prototype.export_as_JSON.apply(this, arguments);
            json.reward_id = this.reward_id;
            json.loyalty_points = this.get_new_points();
            if (this.pos.loyalty) {
                json.loyalty_program_id = this.pos.loyalty.id;
            }
            return json;
        },
        init_from_JSON: function (json) {
            _super_orderline.prototype.init_from_JSON.apply(this, arguments);
            this.reward_id = json.reward_id;
        },
    })
    var _super = models.Order;
    models.Order = models.Order.extend({

        /* The total of points won, excluding the points spent on rewards */
        get_won_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            }

            var orderLines = this.get_orderlines();
            var total_points = 0;
            var rounding = this.pos.loyalty.rounding;

            for (var i = 0; i < orderLines.length; i++) {
                var line = orderLines[i];
                total_points += line.get_won_points();
            }
            total_points += round_pr(this.pos.loyalty.pp_order, rounding);

            return total_points;
        },

        /* The total number of points spent on rewards */
        get_spent_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                var lines = this.get_orderlines();
                var points = 0;

                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i]
                    points += line.get_spent_points();
                }

                return points;
            }
        },

        /* The total number of points lost or won after the order is validated */
        get_new_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_won_points() + this.get_spent_points(), this.pos.loyalty.rounding);
            }
        },

        /* The total number of points that the customer will have after this order is validated */
        get_new_total_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_client().loyalty_points + this.get_new_points(), this.pos.loyalty.rounding);
            }
        },

        /* The number of loyalty points currently owned by the customer */
        get_current_points: function () {
            return this.get_client() ? this.get_client().loyalty_points : 0;
        },

        /* The total number of points spendable on rewards */
        get_spendable_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_client().loyalty_points + this.get_spent_points(), this.pos.loyalty.rounding);
            }
        },

        /* The list of rewards that the current customer can get */
        get_available_rewards: function () {
            var client = this.get_client();
            if (!client) {
                return [];
            }

            var rewards = [];
            for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
                var reward = this.pos.loyalty.rewards[i];
                if (reward.minimum_points > this.get_spendable_points()) {
                    continue;
                } else if (reward.reward_type === 'gift' && reward.point_cost > this.get_spendable_points()) {
                    continue;
                }
                rewards.push(reward);
            }
            return rewards;
        },

        // finalize: function () {
        //     var client = this.get_client();
        //     if (client) {
        //         client.loyalty_points = this.get_new_total_points();
        //         // The client list screen has a cache to avoid re-rendering
        //         // the client lines, and so the point updates may not be visible ...
        //         // We need a better GUI framework !
        //         debugger
        //         this.pos.gui.screen_instances.clientlist.partner_cache.clear_node(client.id);
        //     }
        //     _super.prototype.finalize.apply(this, arguments);
        // },

        export_for_printing: function () {
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            if (this.pos.loyalty && this.get_client()) {
                json.loyalty = {
                    rounding: this.pos.loyalty.rounding || 1,
                    name: this.pos.loyalty.name,
                    client: this.get_client().name,
                    points_won: this.get_won_points(),
                    points_spent: this.get_spent_points(),
                    points_total: this.get_new_total_points(),
                };
            }
            return json;
        },

        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.loyalty_points = this.get_new_points();
            return json;
        },
    });
});


