from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context


class ProcurementApprovalLine(models.Model):
    _name = 'procurement.request.line'
    _description = 'Procurement request line'
    
    approval_request_id = fields.Many2one('approval.request', string='Approval request', required=True, ondelete='cascade')
    state = fields.Selection(related='approval_request_id.state', store=True, index=True)
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0.0, required=True)
    description = fields.Text(string='Description', required=True)
    type = fields.Selection(string='Type', related='product_id.type', readonly=True)
    route_ids = fields.Many2many('stock.location.route', string='Preferred Routes',
                                     help="This is to override the routes set on the product."
                                     " If no route selected, the routes specified for the product will be used.")
    procurement_group_id = fields.Many2one('procurement.group', string='Procurment Group', readonly=True,
                                           help=_("Technical field to store the procurement group generated automatically during procurement request approval."))    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', tracking=True, readonly=False, states={'confirm': [('readonly', True)],
                                                                                                                 'validate1': [('readonly', True)],
                                                                                                                 'validate': [('readonly', True)],
                                                                                                                 'done': [('readonly', True)],
                                                                                                                 'refuse': [('readonly', True)],
                                                                                                                 'cancel': [('readonly', True)]},
                                   help="The warehouse for which the procurement is.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = {}
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            if not self.description:
                self.description = self.product_id.description
            res['domain'] = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
            if self.type == 'product':
                self.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        return res

    def launch_procurement(self):
        ProcurementGroup = self.env['procurement.group']
        for r in self:
            # convert the quantity into one in the product's default UoM
            uom_id = r.product_id.uom_id
            quantity = r.uom_id._compute_quantity(r.quantity, uom_id)

            try:
                ProcurementGroup.with_context(clean_context(r.env.context)).run([
                    self.env['procurement.group'].Procurement(
                        r.product_id,
                        quantity,
                        uom_id,
                        r.warehouse_id.lot_stock_id,  # Location Destination
                        _("Procurement Request"),  # Name of Procurement
                        r.approval_request_id.name,  # Origin
                        r.warehouse_id.company_id,
                        r._prepare_run_values(),  # Values
                    )
                ])
                
            except UserError as error:
                raise UserError(error)

    def _prepare_run_values(self):
        self.ensure_one()
        if not self.procurement_group_id:
            raise ValidationError(_("The procurement group not found for the procurement request line %s")% self.display_name)
        return {
            'warehouse_id': self.warehouse_id,
            'route_ids': self.route_ids,
            'group_id': self.procurement_group_id,
            'date_planned': self.approval_request_id.date,
        }

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.product_id.display_name, r.approval_request_id.name)))
        return result

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot remove a line while its corresponding request is not in draft state."))
        return super(ProcurementApprovalLine, self).unlink()
