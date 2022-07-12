odoo.define('to_website_recaptcha.recaptcha', function (require) {
    'use strict';

    const { ReCaptcha } = require('google_recaptcha.ReCaptchaV3');
    const { Component, tags } = owl;
    const { useState } = owl.hooks;
    const { xml } = tags;

    class FormRecaptcha extends Component {
        constructor() {
            super(...arguments);
            this.recaptcha = new ReCaptcha();
            this.state = useState({
                tokenValue: ''
            })
        }

        async willStart() {
            this.recaptcha.loadLibs();
            const tokenObj = await this.recaptcha.getToken('website_recaptcha');
            this.state.tokenValue = tokenObj.token;
            return super.willStart(...arguments);
        }
    }

    FormRecaptcha.template = xml`<input name="recaptcha_token_response" t-att-value="state.tokenValue" hidden="hidden"/>`

    owl.utils.whenReady(async () => {
        const recaptchaEl = document.querySelector('.o_website_recaptcha');
        if (recaptchaEl) {
            owl.mount(FormRecaptcha, { target: recaptchaEl });
        }
    });

    return FormRecaptcha;
});
