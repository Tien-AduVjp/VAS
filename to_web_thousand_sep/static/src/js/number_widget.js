odoo.define('to_web_thousand_sep.basic_fields', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var utils = require('to_web_thousand_sep.utils');

    basic_fields.FieldMonetary.include({
        _onInput: function () {
            this._super();
            $(this.$input).val(function (index, value) {
                return utils.formatFormula(value)
            });
        }
    });

    basic_fields.FieldFloat.include({
        _onInput: function () {
            this._super();
            if (this.formatType === "float_time") {
                return;
            }
            $(this.$input).val(function (index, value) {
                return utils.formatFormula(value);
            });
        }
    });
});