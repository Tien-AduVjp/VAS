odoo.define('to_website_recaptcha.recaptcha', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.form_recaptcha = sAnimation.Class.extend({
        selector: '.o_website_recaptcha',
        captcha_languages: [
            "ar", "af", "am", "hy", "az", "eu", "bn", "bg", "ca", "zh-HK",
            "zh-CN", "zh-TW", "hr", "cs", "da", "nl", "en-GB", "en", "et",
            "fil", "fi", "fr", "fr-CA", "gl", "ka", "de", "de-AT", "de-CH",
            "el", "gu", "iw", "hi", "hu", "is", "id", "it", "ja", "kn", "ko",
            "lo", "lv", "lt", "ms", "ml", "mr", "mn", "no", "fa", "pl", "pt",
            "pt-BR", "pt-PT", "ro", "ru", "sr", "si", "sk", "sl", "es",
            "es-419", "sw", "sv", "ta", "te", "th", "tr", "uk", "ur", "vi",
            "zu",
        ],
        recaptcha_js_url: "https://www.google.com/recaptcha/api.js",
        start: function () {
            var self = this;
            this._super();
            this.$captcha_el = self.$el;
            this.version = self.$el.attr('data-recaptcha-version') || 'v2';
            this.handle_captcha();
        },
        handle_captcha: function () {
            var self = this;
            // remove all recaptcha element before generating to avoid duplicate
            if (self.version === 'v2') {
                this.$captcha_el.empty()
            }
            return ajax.post('/website/recaptcha/', {'version': self.version}).then(
                function (result) {
                    var data = JSON.parse(result);
                    if (self.version === 'v2') {
                        self.$captcha_el.append(self._get_captcha_elem(data));
                    } else {
                        self.$captcha_el.addClass('g-recaptcha');
                        self.$captcha_el.attr('data-sitekey', data.site_key)
                    }
                    if (self.$captcha_el.length) {
                        $.getScript(self._get_captcha_script_url(data));
                    }
                }
            );
        },
        _get_captcha_elem: function (data) {
            return $('<div/>', {
                'class': 'g-recaptcha',
                'data-sitekey': data.site_key,
            });
        },
        _get_captcha_script_url: function () {
            var lang = $("html").attr("lang").replace("_", "-");
            if (this.version === 'v2' && this.captcha_languages.includes(lang)) {
                return this.recaptcha_js_url + "?hl=" + lang;
            }
            if (this.version === 'v2' && this.captcha_languages.includes(lang.slice(0, 2))) {
                return this.recaptcha_js_url + "?hl=" + lang.slice(0, 2);
            }
            return this.recaptcha_js_url;
        },
    });
});
