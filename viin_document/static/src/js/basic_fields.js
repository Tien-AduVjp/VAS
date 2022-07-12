odoo.define('viin_document.basic_fields', function(require){
    "use strict";

    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    var session = require('web.session');

    var FlexibleBinaryField = basic_fields.AbstractFieldBinary.extend({
        init: function () {
            this._super.apply(this, arguments);
            let image_pattern = new RegExp('image.*(gif|jpeg|jpg|png)')
            let pdf_patterm = new RegExp('application/pdf')
            if(pdf_patterm.test(this.recordData.mimetype)){
                this._init_field_pdf_viewer(basic_fields.FieldPdfViewer.prototype)
            }
            else if(image_pattern.test(this.recordData.mimetype)){
                this._init_field_binary_image(basic_fields.FieldBinaryImage.prototype)
            }
            else{
                this._init_field_binary_file(basic_fields.FieldBinaryFile.prototype)
            }
        },

        /**
         * @private
         * Default of file binary if FieldBinaryFile widget.
         */
        _init_field_binary_file: function(widget){
            this.filename_value = this.recordData[this.attrs.filename];
            this.description = widget.description
            this.template = widget.template
            this.events = widget.events
            this.supportedFieldTypes = widget.supportedFieldTypes
            this._renderReadonly = widget._renderReadonly
            this._renderEdit = widget._renderEdit
            this.set_filename = widget.set_filename
            this.on_save_as = widget.on_save_as
        },

        /**
         * @private
         * Use widget FieldPdfViewer for file type PDF
         */
        _init_field_pdf_viewer: function(widget){
            this.PDFViewerApplication = false;
            this.description = widget.description
            this.supportedFieldTypes = widget.supportedFieldTypes,
            this.template = widget.template
            this.accepted_file_extensions = widget.accepted_file_extensions
            this._disableButtons = widget._disableButtons
            this._getURI = widget._getURI
            this._render = widget._render
            this.on_file_change = widget.on_file_change
            this.on_save_as = widget.on_save_as
        },

        /**
         * @private
         * Use widget FieldBinaryImage for file type image (jpg, jpeg, png...)
         */
        _init_field_binary_image: function(widget){
            this.description = widget.description
            this.fieldDependencies = widget.fieldDependencies
            this.template = widget.template
            this.placeholder = widget.placeholder
            this.events = widget.events
            this.supportedFieldTypes = widget.supportedFieldTypes
            this.file_type_magic_word = widget.file_type_magic_word
            this.accepted_file_extensions = widget.accepted_file_extensions
            this._render = widget._render
            this._renderReadonly = widget._renderReadonly
            this._getImageUrl = function (model, res_id, field, _) {
                return session.url('/web/image', {
                    model: model,
                    id: JSON.stringify(res_id),
                    field: field,
                    unique: new Date().getTime(),
                });
            }
        }
    })

    registry.add('flexible_binary', FlexibleBinaryField)

})
