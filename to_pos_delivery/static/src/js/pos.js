odoo.define('to_pos_delivery.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
	const models = require('point_of_sale.models');

	const {useState} = owl

	models.load_models([
	    {
	        model: 'delivery.carrier',
	        fields: ['name','delivery_type'],
	        loaded: function(self,deliveries){
	            self.deliveries = deliveries;
	        },
	    },
	    {
	        model: 'pos.session',
	        fields: ['update_stock_at_closing'],
	        domain: function(self){
            var domain = [
	                ['state','in',['opening_control','opened']],
	                ['rescue', '=', false],
	            ];
	            if (self.config_id) domain.push(['config_id', '=', self.config_id]);
	            return domain;
        	},
	        loaded: function(self, pos_sessions){
	            self.update_stock_at_closing = pos_sessions[0].update_stock_at_closing;
	        },
	    },
	],{'after': 'product.product'});

	const super_model = models.Order.prototype;

	models.Order = models.Order.extend({
	    set_to_delivery: function(to_delivery){
			    this.assert_editable();
			    this.to_delivery = to_delivery;
		},

	    is_to_delivery: function(){
	    	if (this.to_delivery === undefined){
	    		this.to_delivery = false;
	    	}
	        return this.to_delivery;
	    },

		export_as_JSON: function () {
	        const json = super_model.export_as_JSON.apply(this, arguments);
	        if (this.is_to_delivery()) {
	            json.to_delivery = this.to_delivery;
				json.delivery_date = this.delivery_date;
				json.carrier_id = this.carrier_id;
	        }
	        return json;
	    },
	});

    const DeliveryPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
			state = useState({to_delivery: false, inputDate: null, inputTime: null, carrier_id: false});

			willPatch() {
				this.currentOrder.set_to_delivery(this.state.to_delivery);
				this.currentOrder.delivery_date = this.state.inputDate + ' ' + this.state.inputTime + ':' + '00';
                this.currentOrder.carrier_id = this.state.carrier_id
            }

            onChangeDeliveryMethod(event) {
                this.state.carrier_id = parseInt(event.target.value) || false;
            }

			onChangeDate(event) {
				this.state.inputDate = event.target.value

			}

			onChangeTime(event) {
				this.state.inputTime = event.target.value

			}

            toggleToDelivery() {
	            // click_delivery
				var dt = new Date();
				var year = dt.getFullYear();
	            var month = dt.getMonth()+1;
	            var day = dt.getDate();
	            var hour = dt.getHours();
	            var minute = dt.getMinutes();
	            month = (month<10 ? '0' : '') + month;
	            day = (day<10 ? '0' : '') + day;
	            hour = (hour<10 ? '0' : '') + hour;
	            minute = (minute<10 ? '0' : '') + minute;
				var date = year + '-' + month + '-' + day
				var time = hour + ':' + minute
				const a = this.state.to_delivery
				this.state.to_delivery = !a
				this.state.inputDate = date
				this.state.inputTime = time
	        }

			async _isOrderValid(isForceValidate) {
	            if (this.currentOrder.is_to_delivery() && !this.currentOrder.get_client()) {
	                const { confirmed } = await this.showPopup('ConfirmPopup', {
	                    title: this.env._t('Please select the Customer'),
	                    body: this.env._t(
	                        'You need to select the customer before you can schedule to delivery.'
	                    ),
	                });
	                if (confirmed) {
	                    this.selectClient();
	                }
	                return false;
	            }
                return super._isOrderValid(...arguments);
			}

        };

    Registries.Component.extend(PaymentScreen, DeliveryPaymentScreen);

    return PaymentScreen;
});
