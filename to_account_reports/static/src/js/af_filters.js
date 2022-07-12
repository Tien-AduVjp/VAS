odoo.define('to_account_reports.AFFilters', function (require) {
"use strict";

var SFMMixin = require('web.StandaloneFieldManagerMixin');
var relational_fields = require('web.relational_fields');
var Widget = require('web.Widget');

var Many2ManyFilters = Widget.extend(SFMMixin, {
    init: function (parent, fields) {
        this._super.apply(this, arguments);
        SFMMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },
    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            defs.push(self._makeM2MWidget(field, fieldName));
        });
        return Promise.all(defs);
    },
    start: function () {
        var self = this;
        _.each(this.fields, function (field, fieldName) {
            self.$el.append($('<p/>', {style: 'font-weight:bold;'}).text(field.label));
            self.widgets[fieldName].appendTo(self.$el);
        });
        return this._super.apply(this, arguments);
    },
    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
				no_create: true,
                no_create_edit: true,
            }
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            type: 'many2many',
            value: fieldInfo.value,
        }], options).then(function (recordID) {
            self.widgets[fieldName] = new relational_fields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
	_confirmChange: function () {
        var self = this;
        var result = SFMMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            data[fieldName] = self.widgets[fieldName].value.res_ids;
        });
        this.trigger_up('value_changed', data);
        return result;
    },
});

return Many2ManyFilters;
});
