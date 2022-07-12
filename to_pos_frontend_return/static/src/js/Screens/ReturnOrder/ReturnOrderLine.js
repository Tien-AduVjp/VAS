odoo.define('to_pos_frontend_return.ReturnOrderLine', function (require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');


    class ReturnOrderLine extends PosComponent {
        updateQuantity(event) {
            this.trigger('update-order-line', { key: 'quantity', value: event.target.value, index: this.props.index });
        }
        get product() {
            return this.props.line.product;
        }
        get productDisplayName() {
            return this.product.display_name;
        }
        get productId() {
            return this.product.id;
        }
        get quantity() {
            return this.props.line.quantity ? this.props.line.quantity : '';
        }
        get priceUnit() {
            return this.env.pos.format_currency_no_symbol(this.props.line.price);
        }
        get discount() {
            return this.props.line.discount;
        }
        get taxName() {
            var taxes = this.props.line.get_taxes();
            return taxes.map(tax => {
                return tax.name;
            });
        }
        get subtotalWithoutTax() {
            return this.env.pos.formatFixed(this.props.line.get_price_without_tax());
        }
        get subtotal() {
            return this.env.pos.formatFixed(this.props.line.get_price_with_tax());
        }
    }
    ReturnOrderLine.template = 'ReturnOrderLine';

    Registries.Component.add(ReturnOrderLine);

    return ReturnOrderLine;
});
