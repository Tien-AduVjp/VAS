
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
            run: function () {}, // it's a check
        }
    ];
}
function add_gift_to_order(reward) {
    return [
        {
            content: 'Click reward',
            trigger: '.control-button',
        },
        {
            content: 'Select reward',
            trigger: '.popup-selection .selection .selection-item:contains("'+reward+'")',
        },
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

function finish_order() {
    return [{
        content: "validate the order",
        trigger: '.button.next:visible',
    }, {
        content: "verify that the order is being sent to the backend",
        trigger: ".js_connecting:visible",
        run: function () {}, // it's a check
    }, {
        content: "verify that the order has been successfully sent to the backend",
        trigger: ".js_connected:visible",
        run: function () {}, // it's a check
    }, {
        content: "next order",
        trigger: '.button.next:visible',
    }, { // Leave category displayed by default
        content: "click category switch",
        trigger: ".js-category-switch",
        run: 'click',
    }];
}

odoo.define('point_of_sale.tour.loyalty_pos_tour_product_1', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
            content: 'waiting for loading to finish',
            trigger: 'body:has(.loader:hidden)',
            run: function () {}, // it's a check
        }, { // Leave category displayed by default
            content: "click category switch",
            trigger: ".js-category-switch",
            run: 'click',
        }];
    steps = steps.concat(add_customer('Gemini Furniture'));
    steps = steps.concat(add_product_to_order('product_1'));
    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(finish_order());
    Tour.register('loyalty_pos_tour_product_1', { test: true, url: '/pos/web' }, steps);
});
odoo.define('point_of_sale.tour.loyalty_pos_tour_product_3', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
            content: 'waiting for loading to finish',
            trigger: 'body:has(.loader:hidden)',
            run: function () {}, // it's a check
        }, { // Leave category displayed by default
            content: "click category switch",
            trigger: ".js-category-switch",
            run: 'click',
        }];
    steps = steps.concat(add_customer('Gemini Furniture'));
    steps = steps.concat(add_product_to_order('product_3'));
    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(finish_order());
    Tour.register('loyalty_pos_tour_product_3', { test: true, url: '/pos/web' }, steps);
});
odoo.define('point_of_sale.tour.loyalty_pos_tour_spent_points_gift', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
            content: 'waiting for loading to finish',
            trigger: 'body:has(.loader:hidden)',
            run: function () {}, // it's a check
        }, { // Leave category displayed by default
            content: "click category switch",
            trigger: ".js-category-switch",
            run: 'click',
        }];
    steps = steps.concat(add_customer('Wood Corner'));
    steps = steps.concat(add_product_to_order('product_1'));
    steps = steps.concat(add_gift_to_order('loyalty_reward_1'));

    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(finish_order());
    Tour.register('loyalty_pos_tour_spent_points_gift', { test: true, url: '/pos/web' }, steps);
});
odoo.define('point_of_sale.tour.loyalty_pos_tour_spent_points_discount', function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var steps = [{
            content: 'waiting for loading to finish',
            trigger: 'body:has(.loader:hidden)',
            run: function () {}, // it's a check
        }, { // Leave category displayed by default
            content: "click category switch",
            trigger: ".js-category-switch",
            run: 'click',
        }];
    steps = steps.concat(add_customer('Deco Addict'));
    steps = steps.concat(add_product_to_order('product_1'));
    steps = steps.concat(add_gift_to_order('loyalty_reward_2'));

    steps = steps.concat(goto_payment_screen_and_select_payment_method());
    steps = steps.concat(finish_order());
    Tour.register('loyalty_pos_tour_spent_points_discount', { test: true, url: '/pos/web' }, steps);
});
