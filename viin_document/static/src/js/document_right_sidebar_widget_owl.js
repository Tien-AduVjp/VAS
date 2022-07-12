odoo.define('viin_document.DocumentRightSideBarWidgetOwl', function (require) {
    "use strict";

    const { Component, useState } = owl;
	const relationalFields = require('web.relational_fields');
    const FieldMany2One = relationalFields.FieldMany2One;
    const DocumentTagWidgetOwl = require('viin_document.DocumentTagWidgetOwl');
    const session = require('web.session');

    const DocumentOwnerMany2One = FieldMany2One.extend({
        _onFieldChanged: function(ev){
            ev.stopPropagation();
            if (ev.data.dataPointID === 'owner_id') {
                this.trigger_up('change_owner_id', {owner_id: ev.data.changes.owner_id.id});
            } else if (ev.data.dataPointID === 'workspace_id') {
                this.trigger_up('change_workspace_id', {workspace_id: ev.data.changes.workspace_id.id});
            }
        }
    })

    class DocumentRightSideBarWidgetOwl extends Component {
        constructor() {
            super(...arguments)
            this.regexWebimage = new RegExp('image.*(gif|jpeg|jpg|png)');
            this.regexPreviewable = new RegExp('(image|video|application/pdf|text)');
            this.selected_docs = () => sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];

            this.state = useState({
                previewDocuments: this.selected_docs().slice(0, 4),
                countSelectedDocument: this.selected_docs().length,
                actions:[],
                displayNameDoc: null,
                isMountedM2OOwner: false,
                isMountedM2OWorkspace: false
            })
        }

        willStart() {
            const isDocManager = session.user_has_group('viin_document.document_group_manager')
                                .then(hasGroup => this.isDocManager = hasGroup);

            return Promise.all([super.willStart(...arguments), isDocManager])
        }

        /**
         * @override
         */
        patched(){
            this._createFieldWidget()
        }

        updatePreviewDocuments() {
            let selected_document = this.selected_docs()
            this.state.previewDocuments = selected_document.slice(0, 4);
            this.state.countSelectedDocument = selected_document.length;
            this.state.displayNameDoc = selected_document.length == 1 ? selected_document[0].display_name : null
            this.state.actions = this._getListAction()
            this.parent.trigger_up('render_chatter');
        }

        _createFieldWidget(){
            let selected_document = this.selected_docs()
            let doc_users = selected_document.map(d => {
                return d.owner_id
            })
            let doc_workspaces = selected_document.map(d => {
                return d.workspace_id
            })
            let users = _.unique(doc_users, u => {
                return u.id
            })
            let workspace = _.unique(doc_workspaces, w => {
                return w.id
            })
            var value_owner, value_workspace  = null
            value_owner = users.length === 1 ?  users[0].display_name : null
            value_workspace = workspace.length === 1 ? workspace[0].display_name : null
            this.fieldM2OUser = this._createMany2One('owner_id', 'res.users', value_owner, null, null)
            this.fieldM2OUser.appendTo($('.v_document_owner_field').empty()).then(function(){
                if(users.length > 1) {
                    $('.v_document_owner_field input[type="text"]').attr('placeholder', "Multiple value")
                }
            })
            this.fieldM2OWorkspace = this._createMany2One('workspace_id', 'document.workspace', value_workspace, null, null)
            this.fieldM2OWorkspace.appendTo($('.v_document_workspace_field').empty()).then(function(){
                if (workspace.length > 1) {
                    $('.v_document_workspace_field input[type="text"]').attr('placeholder', "Multiple value")
                }
            })
        }

        _onChangeDocumentName(ev){
            this.parent.trigger_up('change_doc_name', {name: ev.target.value});
        }

        _onDownloadDocument(ev){
            let selected_docs = this.selected_docs();
            let doc_ids = selected_docs.map(d => {
                return d.doc_id
            })
            if(doc_ids.length > 1){
                window.location = `/document/download?model=${this.parent.modelName}&ids=${doc_ids.toString()}&download=true`;
            }
            else if(doc_ids.length ===1){
                if(selected_docs[0].url){
                    window.open(selected_docs[0].url, '_blank')
                }else{
                    window.location = `/web/content/${this.parent.modelName}/${doc_ids[0]}/datas?download=true`;
                }
            }
        }

        _onShareDocument(ev){
            this.parent.trigger('open_wizard')
        }

        _onPreviewDocument(ev){
            ev.stopPropagation()
            let doc_id = parseInt($(ev.target).closest('.v_thumb_preview').attr('data-doc-id'))
            let doc_mimetype = $(ev.target).closest('.v_thumb_preview').attr('data-doc-mimetype')
            let self = this
            if (this.regexPreviewable.test(doc_mimetype) || $(ev.target).attr('data-ytb-video-id')){
                this.rpc({
                    route: '/document/record',
                    params: {
                        document_id: doc_id
                    },
                }).then(function(result){
                    self.parent.trigger_up('kanban_image_clicked', {
                        recordList: result,
                        recordID: doc_id
                    });
                })
            }
        }

        _onHandleAction(ev){
            ev.stopPropagation()
            this.parent.trigger('handle_document_action',{action_id: $(ev.target).attr('data-action-id')})
        }

        _getListAction(){
            let docs_actions = this.selected_docs().map(d => {
                return d.action_ids
            })
            let common_action_ids = _.intersection(...docs_actions.map( doc_actions => { return doc_actions.map(a => { return a.id }) }))
            let common_actions = [].concat(...docs_actions).filter( t => { return common_action_ids.includes(t.id) })
            return _.unique(common_actions, (t => {return t.id} ))
        }

        _createMany2One(name, model, value, domain, context) {
            /**
			 * Copyright Odoo CE (mrp)
			 * https://github.com/odoo/odoo/blob/14.0/addons/lunch/static/src/js/lunch_widget.js#L92-L119
			 */
            var fields = {};
            fields[name] = {type: 'many2one', relation: model, string: name};
            var data = {};
            data[name] = {data: {display_name: value}};

            var record = {
                id: name,
                fields: fields,
                fieldsInfo: {
                    default: fields,
                },
                data: data,
                getDomain: domain || function () { return {}; },
                getContext: context || function () { return {}; },
            };
            var options = {
                mode: 'edit',
                noOpen: true,
                attrs: {
                    can_create: false
                }
            };
            return new DocumentOwnerMany2One(this.parent, name, record, options)
        }

        _onToggleChatter(ev) {
            this.parent.trigger_up('toggle_chatter');
        }
    }

    DocumentRightSideBarWidgetOwl.components = { DocumentTagWidgetOwl }

    /**
    * Multiple select records
    */
    Object.assign(DocumentRightSideBarWidgetOwl, {
        template: "DocumentRightSideBarWidget"
    });

    return DocumentRightSideBarWidgetOwl
})
