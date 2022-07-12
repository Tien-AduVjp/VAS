from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context


class ReplenishmentRequestLine(models.Model):
    _name = 'replenishment.request.line'
    _description = 'Replenishment Request Line'

    request_id = fields.Many2one('replenishment.request', string='Replenishment Request', required=True, ondelete='cascade')
    state = fields.Selection(related='request_id.state', store=True, index=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, domain="[('type','!=','service')]")
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0.0, required=True)
    description = fields.Text(string='Description')
    route_ids = fields.Many2many('stock.location.route', string='Preferred Routes',
                                 help="This is to override the routes set on the product."
                                 " If no route selected, the routes specified for the product will be used.")
    procurement_group_id = fields.Many2one('procurement.group', string='Procurment Group', readonly=True,
                                          help="Technical field to store the procurement group generated automatically during replenishment request approval.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = {}
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            res['domain'] = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        return res

    def launch_replenishment(self):
        ProcurementGroup = self.env['procurement.group'].sudo()
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
                        r.request_id.warehouse_id.lot_stock_id,  # Location Destination
                        _("Replenishment Request"),  # Name of Procurement
                        r.request_id.name,  # Origin
                        r.request_id.warehouse_id.company_id,
                        r._prepare_run_values(),  # Values
                    )
                ])
                
            except UserError as error:
                raise UserError(error)

    def _prepare_run_values(self):
        if not self.procurement_group_id:
            raise ValidationError(_("The procurement group not found for the replenishment request line %s") % self.display_name)
        return {
            'warehouse_id': self.request_id.warehouse_id,
            'route_ids': self.route_ids,
            'group_id': self.procurement_group_id,
            'date_planned': self.request_id.scheduled_date,
        }

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.product_id.display_name, r.request_id.name)))
        return result

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot remove a line while its corresponding request is not in draft state."))
        return super(ReplenishmentRequestLine, self).unlink()
