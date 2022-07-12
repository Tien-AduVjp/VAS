from odoo import api, fields, models


class DocumentTemplatePreview(models.TransientModel):
    _inherit = "document.template"
    _name = "document_template.preview"
    _description = "Document Template Preview"

    @api.model
    def _get_records(self):
        """ Return Records of particular Document Template's Model """
        template_id = self._context.get('template_id')
        default_res_id = self._context.get('default_res_id')
        if not template_id:
            return []
        template = self.env['document.template'].browse(int(template_id))
        records = self.env[template.model_id.model].search([], limit=10)
        records |= records.browse(default_res_id)
        return records.name_get()

    @api.model
    def default_get(self, fields):
        result = super(DocumentTemplatePreview, self).default_get(fields)

        if 'res_id' in fields and not result.get('res_id'):
            records = self._get_records()
            result['res_id'] = records and records[0][0] or False  # select first record as a Default
        if self._context.get('template_id') and 'model_id' in fields and not result.get('model_id'):
            result['model_id'] = self.env['document.template'].browse(self._context['template_id']).model_id.id
        return result

    res_id = fields.Selection(_get_records, 'Sample Document')

    @api.onchange('res_id')
    def on_change_res_id(self):
        doc_values = {}
        if self.res_id and self._context.get('template_id'):
            template = self.env['document.template'].browse(self._context['template_id'])
            self.name = template.name
            doc_values = template.generate_document(self.res_id)
        for field in ['content_html']:
            setattr(self, field, doc_values.get(field, False))
