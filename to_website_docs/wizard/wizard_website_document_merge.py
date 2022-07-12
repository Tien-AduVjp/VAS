from odoo import models, fields, api


class WizardWebsiteDocumentMerge(models.TransientModel):
    _name = 'wizard.website.document.merge'
    _description = 'Website Document Merging Wizard'

    @api.model
    def _default_documents(self):
        active_ids = self._context.get('active_ids', [])
        return self.env['website.document'].search([('id', 'in', active_ids)])

    document_ids = fields.Many2many('website.document', string='Selected Documents', default=_default_documents)

    source_document_id = fields.Many2one('website.document', string='Source Document', required=True, ondelete='cascade')
    destination_document_id = fields.Many2one('website.document', string='Destination Document', required=True, ondelete='cascade')
    update_name = fields.Boolean(string='Update Name', help="If checked, the name of the destination document"
                                 " will be updated with the name of the source document.")

    @api.onchange('document_ids')
    def _onchange_document_ids(self):
        c = len(self.document_ids)
        if c >= 2:
            self.update({
                'source_document_id': self.document_ids[0].id,
                'destination_document_id': self.document_ids[1].id
                })
        elif c == 1:
            self.source_document_id = self.document_ids

    def action_merge(self):
        self.ensure_one()
        self.source_document_id.with_context(update_dest_doc_name=self.update_name).merge(self.destination_document_id)

