odoo.define('to_account_asset.AccountAssetAssetFormView', function(require) {
"use strict";

var FormRenderer = require('web.FormRenderer');
var FormView = require('web.FormView');
var core = require('web.core');
var viewRegistry = require('web.view_registry');

var _t = core._t;

var AccountAssetAssetFormRenderer = FormRenderer.extend({
    events: _.extend({}, FormRenderer.prototype.events, {
        'click .add_original_move_lines': '_onAddOriginalMoveLines',
    }),
    /*
	 * Open the m2o item selection from another button
	 */
    _onAddOriginalMoveLines: function(ev) {
        _.find(this.allFieldWidgets[this.state.id], x => x['name'] == 'original_move_line_ids').onAddRecordOpenDialog();
    },
});

var AccountAssetAssetFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Renderer: AccountAssetAssetFormRenderer,
    }),
});

viewRegistry.add("account_asset_form", AccountAssetAssetFormView);
return AccountAssetAssetFormView;

});
