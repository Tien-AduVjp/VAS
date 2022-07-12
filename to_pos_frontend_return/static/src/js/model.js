odoo.define('viin_loyalty_pos.models', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    var _super_order = models.Order;
    var _super_order_line = models.Orderline;

    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.prototype.initialize.apply(this, arguments);
            this.refund_original_order_id = false;
        },
        init_from_JSON: function (json) {
            _super_order.prototype.init_from_JSON.apply(this, arguments);
            this.refund_original_order_id = json.refund_original_order_id;
        },
        export_as_JSON: function () {
            var json = _super_order.prototype.export_as_JSON.apply(this, arguments);
            json.refund_original_order_id = this.refund_original_order_id;
            return json;
        },
    }),
        models.Orderline = models.Orderline.extend({
            initialize: function (attr, options) {
                _super_order_line.prototype.initialize.apply(this, arguments);
                this.refund_original_line_id = options.refund_original_line_id;
            },
            init_from_JSON: function (json) {
                _super_order_line.prototype.init_from_JSON.apply(this, arguments);
                this.refund_original_line_id = json.refund_original_line_id;
            },
            export_as_JSON: function () {
                var json = _super_order_line.prototype.export_as_JSON.apply(this, arguments);
                json.refund_original_line_id = this.refund_original_line_id;
                return json;
            },
        })
});
