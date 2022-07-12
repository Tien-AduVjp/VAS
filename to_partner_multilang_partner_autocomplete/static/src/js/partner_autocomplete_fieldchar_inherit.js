odoo.define('to_partner_multilang_partner_autocomplete.FieldAutocomplete', function (require) {
'use strict';

var core = require('web.core');
var _t = core._t;

var FieldAutocomplete = require('partner.autocomplete.fieldchar');

FieldAutocomplete.include({
	_renderEdit: function () {
        this._super(...arguments);
        this.$el.append(this._renderTranslateButton());
        this.$el.addClass('d-inline-flex');
    },
    _renderTranslateButton: function () {
        if (_t.database.multi_lang && this.field.translate && this.res_id) {
            return $('<button>', {
                    type: 'button',
                    'class': 'o_field_translate fa fa-globe btn btn-link',
                })
                .on('click', this._onTranslate.bind(this));
        }
        return $();
    },
})

});
