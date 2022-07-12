odoo.define('to_sale_subscription.sale_subscription_portal_form', function (require) {
    'use strict';

    require('web.dom_ready');

    if(!$('.js_website_subscription').length) {
        return $.Deferred().reject("DOM does not contain '.js_surveyresult'");
    }

    $('.js_subscription_submit').off('click').on('click', function () {
        var $button = $(this);
        $button.attr('disabled', true)
            .prepend('<i class="fa fa-refresh fa-spin"/>');
        $button.closest('form').submit();
    });
});
