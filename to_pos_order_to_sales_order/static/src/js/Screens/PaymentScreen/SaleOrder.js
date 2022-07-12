odoo.define('to_pos_order_to_sales_order.SaleOrder', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');

    class SaleOrder extends PaymentScreen {

		async createSaleOrder() {
	        var order = this.env.pos.get_order();
	        order = order.export_as_JSON();

			// Check customer
			if (!order.partner_id){
				const { confirmed } = await this.showPopup(
					'ConfirmPopup',
					{
		                title: this.env._t('Please select the Customer'),
		                body: this.env._t('You need to select the customer before you can create an sales order.'),
                        confirmText: this.env._t('Ok'),
                        cancelText: this.env._t('Cancel'),
            		});
	            if (confirmed) {
	                this.selectClient();
	            }
				return;
	        } else if (this.currentOrder.get_orderlines().length === 0) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Empty Order'),
                    body: this.env._t(
                        'There must be at least one product in your order before you can create an sales order.'
                    ),
                    confirmText: this.env._t('Ok'),
                    cancelText: this.env._t('Cancel'),
                });
                return false;
            } else {
		        var fields = {};
		        fields.pricelist_id = order.pricelist_id;
		        fields.pos_config_id = this.env.pos.config_id;
		        fields.session_id = order.pos_session_id;
		        fields.user_id = order.user_id;
		        fields.creation_date = order.creation_date;
		        fields.partner_id = order.partner_id;
		        fields.fiscal_position_id = order.fiscal_position_id;
		        fields.lines = order.lines;

				var self = this;
		        return this.rpc({
		            model: 'sale.order',
		            method: 'create_from_ui',
		            args: [fields]
		        }).then(
					function(order_id){
		            	self.go_to_sale_order_view(order_id);
		        	}).catch();
			}
		}

		async go_to_sale_order_view(order_id) {
			var self = this;
			const { confirmed } = await this.showPopup(
					'ConfirmPopup',
					{
		                title: this.env._t('Visit Order page'),
		                body: this.env._t('Do you want to view this order in order page?'),
                        confirmText: this.env._t('Ok'),
                        cancelText: this.env._t('Cancel'),
            		});
            if (confirmed) {
                self.currentOrder.finalize();
            	window.location = window.location.origin + '/web#id='+ order_id +'&view_type=form&model=sale.order';
	        } else {
                self.currentOrder.finalize();
                if (self.env.pos.config.module_pos_restaurant) {
                    window.location.reload();
                }
                self.showScreen('ProductScreen');
	        }
		}

	}
	SaleOrder.template = 'SaleOrder';
    Registries.Component.add(SaleOrder);
    return SaleOrder;
});
