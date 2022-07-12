from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context


class StockAllocationRequestLine(models.Model):
    _name = 'stock.allocation.request.line'
    _description = 'Stock Allocation Request Line'

    request_id = fields.Many2one('stock.allocation.request', string='Allocation Request', required=True, ondelete='cascade')
    state = fields.Selection(related='request_id.state',default='draft', store=True, index=True, readonly=False)
    product_id = fields.Many2one('product.product', string='Product', required=True, domain="[('type','!=','service')]")
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0.0, required=True)
    description = fields.Text(string='Description')
    procurement_group_id = fields.Many2one('procurement.group', string='Procurment Group', readonly=True,
                                          help="Technical field to store the procurement group generated automatically during allocation request approval.")
    warehouse_id = fields.Many2one('stock.warehouse', string="Destination Warehouse", required=True)


    @api.constrains('warehouse_id')
    def _check_warehouse_id(self):
        for r in self:
            if r.warehouse_id == r.request_id.warehouse_id:
                raise ValidationError(_("Source and Destination Warehouse cannot be the same : %s") %r.warehouse_id.name)
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = {}
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            res['domain'] = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        return res

    def launch_allocation(self):
        ProcurementGroup = self.env['procurement.group']
        for r in self:
            # convert the quantity into one in the product's default UoM
            uom_id = r.product_id.uom_id
            quantity = r.uom_id._compute_quantity(r.quantity, uom_id)

            try:
                ProcurementGroup.with_context(clean_context(r.env.context)).run([self.env['procurement.group'].Procurement(
                        r.product_id,
                        quantity,
                        uom_id,
                        r.warehouse_id.lot_stock_id,            # Location Destination
                        _("Stock Allocation Request"),          # Name of Procurement
                        r.request_id.name,                      # Origin
                        r.warehouse_id.company_id,
                        r._prepare_run_values()                 # Values
                        )])
            except UserError as error:
                raise UserError(error)

    def _prepare_run_values(self):
        if not self.procurement_group_id:
            raise ValidationError(_("The procurement group not found for the allocation request line %s") % self.display_name)
        return {
            'warehouse_id': self.warehouse_id,
            'route_ids': self._get_supply_route(self.request_id.warehouse_id, self.warehouse_id),
            'group_id': self.procurement_group_id,
            'date_planned': self.request_id.scheduled_date,
        }

    def _get_supply_route(self, from_wh, to_wh):
        Route = self.env['stock.location.route']
        route = Route.search([
                        ('supplied_wh_id', '=', to_wh.id),
                        ('supplier_wh_id', '=', from_wh.id),
                        ('active', '=', True)
                    ])
        if not route:
            to_wh.create_resupply_routes(from_wh)
        if from_wh not in to_wh.resupply_wh_ids:
            to_wh.resupply_wh_ids = [(4, from_wh.id)]
        route = Route.search([
                        ('supplied_wh_id', '=', to_wh.id),
                        ('supplier_wh_id', '=', from_wh.id),
                        ('active', '=', True)
                    ])
        return route

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.product_id.display_name, r.request_id.name)))
        return result

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot remove a line while its corresponding request is not in draft state."))
        return super(StockAllocationRequestLine, self).unlink()
