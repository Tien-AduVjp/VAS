odoo.define('viin_document.DocumentTagWidgetOwl', function(require) {
    "use strict";

    const { Component, useState } = owl;
    const relationalFields = require('web.relational_fields');
    const FieldMany2One = relationalFields.FieldMany2One;

    const DocumentTagMany2One = FieldMany2One.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.tagWidget = arguments[4]
        },
        _onFieldChanged: function(ev){
            ev.stopPropagation();
            this.tagWidget._addTag(ev.data.changes.tag_ids)
        }
    })

    class DocumentTagWidgetOwl extends Component {
        constructor(...args) {
            super(...args)
            this.parent = args[0]
            this.state = useState({
                tags:null
            })
        }

        /**
         * @override
         */
        async willStart() {
            this._updateTag()
        }

        /**
         * @override
         */
        mounted() {
            this.fieldM2OTag = this._createMany2One('tag_ids', 'document.tag', null, null, null)
            this.fieldM2OTag.appendTo($('.v_input_document_tag').empty()).then( function () {
                $('.v_input_document_tag input[type="text"]').attr('placeholder', 'Add a tag');
            })
        }

        /**
         * @override
         */
        willUpdateProps() {
            this._updateTag()
        }

        /**
         * @private
         * Update tags when change selected documents.
         * Tags was showed is common tags of all selected documents.
         */
        _updateTag(){
            let selected_docs = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
            let docs_tags = selected_docs.map(d => {
                return d.tag_ids
            })
            let common_tag_ids = _.intersection(...docs_tags.map( doc_tags => { return doc_tags.map(t => { return t.id }) }))
            let common_tags = [].concat(...docs_tags).filter( t => { return common_tag_ids.includes(t.id) })
            this.state.tags= _.unique(common_tags, (t => {return t.id} ))
        }

        /**
         * @private
         * Add new tag for selected documents.
         */
        _addTag(tag) {
            let selected_docs = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
            let doc_ids = selected_docs.map(d => {
                return d.doc_id
            })
            let tags = JSON.parse(JSON.stringify(this.state.tags))
            let index = _.findIndex(tags, t => {
                return t.id === tag.id
            })
            if (index === -1) {
                let self = this
                this.rpc({
                    route: '/document/update',
                    params: {
                        data:{
                            document_ids: doc_ids,
                            fields: ['tag_ids'],
                            value:{
                                tag_ids: {
                                    id: tag.id,
                                    action:'ADD_NEW'
                                }
                            }
                        }
                    },
                }).then(function (result) {
                    if(result != false){
                        self.parent.parent.trigger_up('update_tag',{ doc_ids: result })
                    }
                });
            }
        }

        /**
         * @private
         * Remove tag from selected documents
         */
        _removeTag(ev) {
            let self = this
            let selected_docs = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
            let doc_ids = selected_docs.map(d => {
                return d.doc_id
            })
            let tag_id = parseInt($(ev.target).attr('data-tag-id'))
            this.rpc({
                route: '/document/update',
                params: {
                    data:{
                        document_ids: doc_ids,
                        fields: ['tag_ids'],
                        value:{
                            tag_ids: {
                                id: tag_id,
                                action:'REMOVE'
                            }
                        }
                    }
                },
            }).then(function (result) {
                if(result){
                    self.parent.parent.trigger_up('update_tag',{ doc_ids: result })
                }
            });
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
                getDomain: domain || function () { return []; },
                getContext: context || function () { return {}; },
            };
            var options = {
                mode: 'edit',
                noOpen: true,
                attrs: {
                    can_create: true,
                    can_write: true,
                }
            };
            let res = new DocumentTagMany2One(this.parent.parent, name, record, options, this)
            res = Object.assign(res,{
                nodeOptions: {
                    no_quick_create: true
                },
                string: 'Tag'
            })
            return res
        }
    }

    Object.assign(DocumentTagWidgetOwl, {
        template: "DocumentTagWidget"
    });


    return DocumentTagWidgetOwl
})
