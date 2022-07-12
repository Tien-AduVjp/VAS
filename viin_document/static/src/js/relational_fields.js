odoo.define('viin_document.relational_fields', function(require){
    "use strict";

    var relational_fields = require('web.relational_fields');
    var registry = require('web.field_registry');

    var DocumentActionFieldMany2ManyTags = relational_fields.FieldMany2ManyTags.extend({
        tag_template: "DocumentActionFieldMany2ManyTag",
        events:{
            'click .action-handler': '_onActionHandler'
        },

        /**
         * @private
         * @param {MouseEvent} event
         */
         _onActionHandler: function (event) {
            event.preventDefault();
            event.stopPropagation();
            let self = this
            this._rpc({
            	route: '/document/handle_action',
            	params: {
	            	document_ids: [this.res_id],
	            	action_id:$(event.target).data('action-id')
	            }
            }).then(function(result){
            	if(result && result.documents){
            		self.trigger_up('reload');
            	}
            })
        },
    })

    registry.add('document_action_many2many_tags', DocumentActionFieldMany2ManyTags)

})
