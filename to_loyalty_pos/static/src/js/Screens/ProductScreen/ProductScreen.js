odoo.define('to_loyalty_pos.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;
    var round_pr = utils.round_precision;

    const LoyaltyProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                useListener('click-rewards', this._onClickRewards);
            }
            get applyLoyaltyProgram() {
                return this.env.pos.config.loyalty_id;
            }
            get hasCustomer() {
                if (this.client) {
                    return true;
                } else {
                    return false;
                }
            }
            get hasRewards() {
                var rewards = this.currentOrder.get_available_rewards();
                return rewards.length > 0;
            }
            async _onClickRewards() {
                if (!this.hasCustomer) {
                    return;
                }
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
                var rewards = this.currentOrder.get_available_rewards();
                if (rewards.length === 0) {
                    await this.showPopup('ErrorPopup', {
                        title: _t('No Rewards Available'),
                        body: _t('There are no rewards available for this customer as part of the loyalty program'),
                    });
                } else if (rewards.length === 1 && this.env.pos.loyalty.rewards.length === 1) {
                    this.apply_reward(rewards[0]);
                    return;
                } else {
                    const selectionList = rewards.map((reward) => ({
                        id: reward.id,
                        label: reward.name,
                        isSelected: false,
                        item: reward,
                    }));
                    const { confirmed, payload: rewardSelected } = await this.showPopup('SelectionPopup', {
                        title: _t('Please select a reward'),
                        list: selectionList,
                        cancelText: _t('Cancel')
                    });
                    if (confirmed) {
                        await this.apply_reward(rewardSelected);
                    }
                }
            }
            async apply_reward(reward) {
                if (!this.hasCustomer) {
                    return;
                }
                var order_total, spendable;
                var lrounding, crounding;
                let price = 0;
                let product_id = 0;
                if (reward.reward_type === 'gift') {
                    product_id = reward.gift_product_id[0]
                } else if (reward.reward_type === 'discount') {
                    product_id = reward.discount_product_id[0]
                    lrounding = this.env.pos.loyalty.rounding;
                    crounding = this.env.pos.currency.rounding;
                    spendable = this.currentOrder.get_spendable_points();
                    order_total = this.currentOrder.get_total_without_tax();
                    price = round_pr(order_total * (reward.discount / 100), crounding);

                    if (round_pr(price * reward.point_cost, lrounding) > spendable) {
                        price = round_pr(Math.floor(spendable / reward.point_cost), crounding);
                    }
                }
                const product = this.env.pos.db.get_product_by_id(product_id)
                if (!product || !product.available_in_pos) {
                    await this.showPopup('ErrorPopup', {
                        title: _t('Reward product is not available in POS'),
                        body: _t('Reward product is not available in PoS. Please get one configured or select another reward!'),
                    });
                    return;
                }
                this.currentOrder.add_product(product, {
                    price: price,
                    quantity: -1,
                    merge: false,
                    extras: { reward_id: reward.id },
                });
            }
        };

    Registries.Component.extend(ProductScreen, LoyaltyProductScreen);

    return ProductScreen;
});
