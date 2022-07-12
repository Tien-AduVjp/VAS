odoo.define('viin_document.DocumentModel', function (require) {
    "use strict";

    const DocumentModel = {

        /**
         * @override
         */
        _searchReadUngroupedList: function (list) {
            let res = this._super.apply(this, arguments);
            let domain = list.domain.filter(d => d.length === 3 && d[0] === 'workspace_id' && d[1] === 'child_of');
            let workspace_id = domain.length ? domain[0][2] : null;
            this.active_workspace_id = workspace_id;
            this.trigger_up('search_workspace_document', { workspace_id });
            return res
        }
    }

    return DocumentModel
})
