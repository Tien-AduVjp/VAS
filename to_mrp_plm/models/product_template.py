from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    eco_inprogress = fields.Boolean(string='ECO in progress?', compute='_compute_eco_data')
    eco_inprogress_count = fields.Integer(string='# ECOs in progress', compute='_compute_eco_data')
    attachment_count = fields.Integer(string='# Attachments', compute='_compute_attachments')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'product.template')], string='Attachments')

    def _compute_eco_data(self):
        eco_data = self.env['mrp.eco'].sudo().read_group([
            ('product_tmpl_id', 'in', self.ids),
            ('state', '=', 'progress')],
            ['product_tmpl_id'], ['product_tmpl_id'])
        result = dict((data['product_tmpl_id'][0], data['product_tmpl_id_count']) for data in eco_data)
        for r in self:
            r.eco_inprogress_count = result.get(r.id, 0)
            r.eco_inprogress = bool(r.eco_inprogress_count)

    def _compute_attachments(self):
        for r in self:
            r.attachment_count = len(r.attachment_ids | r.product_variant_ids.attachment_ids)

    def action_view_attachments(self):
        self.ensure_one()
        domain = [
            '|',
            '&', ('res_model', '=', 'product.product'), ('res_id', 'in', self.product_variant_ids.ids),
            '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.id)]
        attachment_view = self.env.ref('mrp.view_document_file_kanban_mrp')
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'mrp.document',
            'type': 'ir.actions.act_window',
            'view_id': attachment_view.id,
            'views': [(attachment_view.id, 'kanban'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Click to upload files to your product.
                    </p><p>
                        Use this feature to store any files, like drawings or specifications.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % ('product.template', self.id)
        }
