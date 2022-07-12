function add_customer_order(customer) {
	return [
		{
			content: 'click set customer',
			trigger: '.button.set-customer',
		},
		{
			content: 'select ' + customer,
			trigger: '.client-list .client-list-contents .client-line:contains("' + customer + '")',
		},
		{
			content: 'set customer',
			trigger: '.button.next:visible',
		},
	];
}

function add_products_to_order(product_name) {
	return [
		{
			content: 'buy ' + product_name,
			trigger: '.product-list .product-name:contains("' + product_name + '")',
		}, {
			content: 'the ' + product_name + ' have been added to the order',
			trigger: '.order .product-name:contains("' + product_name + '")',
			run: function() { },
		}
	];
}

function goto_payment_screen_and_select_payments_method(voucher_type) {
	return [{
		content: "go to payment screen",
		trigger: '.button.pay',
	}, {
		content: "pay with cash",
		trigger: '.paymentmethod:contains("Cash")',
	},
	{
		content: "fill serial of voucher",
		trigger: '.modal-dialog:not(.oe hidden) .popup-textinput input',
		run:function(){
			$('.modal-dialog:not(.oe hidden) .popup-textinput input').val(voucher_type)
		}
	},
	{
		content: "Click confirm",
		trigger: '.button.confirm',
	}];
}

function finish_orders() {
	return [{
		content: "validate the order",
		trigger: '.button.next:visible',
	}, {
		content: "next order",
		trigger: '.button.next:visible',
	}];
}

function check_voucher(message) {
	return [{
		content: "Check voucher in stock",
		trigger: '.modal-dialog:contains(' + message + ')',
	}];
}

odoo.define('point_of_sale.tour.promotion_voucher_pos_actived', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('voucher_actived'));
	steps = steps.concat(finish_orders());

	Tour.register('promotion_voucher_pos_actived', { test: true, url: '/pos/web' }, steps);
});

odoo.define('point_of_sale.tour.promotion_voucher_pos_expired', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('voucher_expired'));
	steps = steps.concat(check_voucher('This Voucher is already expired.'));

	Tour.register('promotion_voucher_pos_expired', { test: true, url: '/pos/web' }, steps);
});

odoo.define('point_of_sale.tour.promotion_voucher_pos_used', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('voucher_used'));
	steps = steps.concat(check_voucher('This Voucher has been used.'));

	Tour.register('promotion_voucher_pos_used', { test: true, url: '/pos/web' }, steps);
});

odoo.define('point_of_sale.tour.promotion_voucher_pos_inactived', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('voucher_inactived'));
	steps = steps.concat(check_voucher('This Voucher is still in your stock. Hence, it cannot be used..'));

	Tour.register('promotion_voucher_pos_inactived', { test: true, url: '/pos/web' }, steps);
});

odoo.define('point_of_sale.tour.promotion_voucher_pos_incorect', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('12345678'));
	steps = steps.concat(check_voucher('This Voucher code is incorrect.'));

	Tour.register('promotion_voucher_pos_incorect', { test: true, url: '/pos/web' }, steps);
});

odoo.define('point_of_sale.tour.promotion_voucher_pos_actived_used', function(require) {
	"use strict";
	var Tour = require("web_tour.tour");
	var steps = [{
		content: 'waiting for loading to finish',
		trigger: 'body:has(.loader:hidden)',
		run: function() { },
	}, {
		content: "click category switch",
		trigger: ".js-category-switch",
		run: 'click',
	}];
	steps = steps.concat(add_customer_order('Gemini Furniture'));
	steps = steps.concat(add_products_to_order('product_1'));

	steps = steps.concat(goto_payment_screen_and_select_payments_method('voucher_used_100'));
	steps = steps.concat(finish_orders());

	Tour.register('promotion_voucher_pos_actived_used', { test: true, url: '/pos/web' }, steps);
});
