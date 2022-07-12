odoo.define('to_product_return_reason_pos.models', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    var _super_order_line = models.Orderline;

    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_order_line.prototype.initialize.apply(this, arguments);
            this.return_reason_id = options.return_reason_id;
            this.return_reason_orther = options.return_reason_orther;
        },
        init_from_JSON: function (json) {
            _super_order_line.prototype.init_from_JSON.apply(this, arguments);
            this.return_reason_id = json.return_reason_id;
            this.return_reason_orther = json.return_reason_orther;
        },
        export_as_JSON: function () {
            var json = _super_order_line.prototype.export_as_JSON.apply(this, arguments);
            json.return_reason_id = this.return_reason_id;
            json.return_reason_orther = this.return_reason_orther;
            return json;
        },
    })
    models.load_models({
        model: 'product.return.reason',
        fields: ['name', 'description'],
        domain: [['active', '=', true]],
        loaded: function (self, return_reasons) {
            return_reasons.unshift({
                'name': 'None',
                'id': '',
            })
            if (self.config.allow_to_create_new_reason) {
                return_reasons.push({
                    'name': 'Other',
                    'id': -1,
                })
            }
            self.return_reasons = return_reasons;
        }
    }, { 'after': 'product.product' });

    return models;
});
