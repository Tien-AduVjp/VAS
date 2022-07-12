
function add_customer(customer) {
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
function add_product_to_order(product_name) {
    return [
        {
            content: 'buy ' + product_name,
            trigger: '.product-list .product-name:contains("' + product_name + '")',
        }, {
            content: 'the ' + product_name + ' have been added to the order',
            trigger: '.order .product-name:contains("' + product_name + '")',
            run: function () { }, // it's a check
        }
    ];
}

function goto_payment_screen_and_select_payment_method() {
    return [{
        content: "go to payment screen",
        trigger: '.button.pay',
    }, {
        content: "pay with bank",
        trigger: '.paymentmethod:contains("Bank")',
    }];
}

function validate_order() {
    return [{
        content: "validate the order",
        trigger: '.button.next:visible',
    }, {
        content: "verify that the order is being sent to the backend",
        trigger: ".js_connecting:visible",
    }, {
        content: "verify that the order has been successfully sent to the backend",
        trigger: ".js_connected:visible",
    }];
}
function goto_manageorder(customer) {
    return [{
        content: "Go to manager order",
        trigger: '.manageorder-button',
    }, {
        content: "select order",
        trigger: '.order-list .order-list-contents .order-line:contains("' + customer + '")',
    }];
}
function check_return(can_create) {
    return [{
        content: "Click button return",
        trigger: '.button.return',
    }, {
        content: "Select return",
        trigger: '.order-line-return-reason',
        run: function () {
            $('.order-line-return-reason').focus()
            if (can_create) {
                if ($('.other_reason').css('display') == 'none') {
                    throw new Error("User can't create return reason" + $('.other_reason').css('display'));
                }
            }
            else {
                if ($('.other_reason').css('display') != 'none') {
                    throw new Error("User can create return reason" + $('.other_reason') .css('display'));
                }
            }
        }
    }];
}

odoo.define('point_of_sale.tour.not_allow_create_new_reason', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
        content: 'waiting for loading to finish',
        trigger: 'body:has(.loader:hidden)',
        run: function () { }, // it's a check
    }, { // Leave category displayed by default
        content: "click category switch",
        trigger: ".js-category-switch",
        run: 'click',
    }];
    steps = steps.concat(add_customer('Gemini Furniture'));
    steps = steps.concat(add_product_to_order('Office Chair'));
    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(validate_order());
    steps = steps.concat(goto_manageorder('Gemini Furniture'));
    steps = steps.concat(check_return(false));
    Tour.register('not_allow_create_new_reason', { test: true, url: '/pos/web' }, steps);
});
odoo.define('point_of_sale.tour.allow_create_new_reason', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
        content: 'waiting for loading to finish',
        trigger: 'body:has(.loader:hidden)',
        run: function () { }, // it's a check
    }, { // Leave category displayed by default
        content: "click category switch",
        trigger: ".js-category-switch",
        run: 'click',
    }];
    steps = steps.concat(add_customer('Gemini Furniture'));
    steps = steps.concat(add_product_to_order('Office Chair'));
    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(validate_order());
    steps = steps.concat(goto_manageorder('Gemini Furniture'));
    steps = steps.concat(check_return(true));
    Tour.register('allow_create_new_reason', { test: true, url: '/pos/web' }, steps);
});
