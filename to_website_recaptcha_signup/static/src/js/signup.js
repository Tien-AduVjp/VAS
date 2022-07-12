odoo.define('to_website_recaptcha.signup', function (require) {
    'use strict';

    const { registry } = require('web.public.widget');

    registry.SignUpForm.include({
        _onSubmit: function(event) {
            const inputs =  $(event.currentTarget).find('.form-control');
            let valid = true;
            _.each(inputs, input => {
                if (!input.checkValidity()) {
                    valid = false;
                    $(input).addClass('is-invalid');
                } else {
                    $(input).removeClass('is-invalid');
                }
            });
            if (!valid) {
                event.preventDefault();
                return;
            }
            return this._super(...arguments);
        }
    })
});
