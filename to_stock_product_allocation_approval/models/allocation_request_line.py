from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context

from odoo.addons.to_approvals.models.abstract_approval_request_line import STATUS


class StockAllocationRequestLine(models.Model):
    _name = 'stock.allocation.request.line'
    _description = 'Stock Allocation Request Line'
    _inherit = 'abstract.approval.request.line'

    line_state = fields.Selection(STATUS, default='draft', store=True, compute='_compute_line_state', string='Status')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain="[('type','!=','service')]")
    category_uom_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True, compute='_compute_uom_id', readonly=False, store=True,
                             domain="[('category_id', '=', category_uom_id)]")
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0.0, required=True)
    description = fields.Text(string='Description')
    procurement_group_id = fields.Many2one('procurement.group', string='Procurment Group', readonly=True,
                                           help="Technical field to store the procurement group generated automatically during allocation request approval.")
    warehouse_source_id = fields.Many2one('stock.warehouse', related='approval_id.warehouse_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Destination Warehouse', required=True,
                                   domain="[('id', '!=', warehouse_source_id), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', related='approval_id.company_id', store=True)

    approval_state_exception = fields.Boolean(string='Approval Status Exception', readonly=True,
                                     help="This field indicates the status of this plan is an exception of its approval request."
                                     " For example: when a plan of a requests' is cancelled/refused while others are not, the plan"
                                     " will be marked as `Approval Status Exception`.")

    @api.constrains('warehouse_id')
    def _check_warehouse_id(self):
        for r in self:
            if r.warehouse_id == r.approval_id.warehouse_id:
                raise ValidationError(_("Source and Destination Warehouse cannot be the same : %s") % r.warehouse_id.name)

    @api.depends('product_id')
    def _compute_uom_id(self):
        for r in self:
            if r.product_id:
                r.uom_id = r.product_id.uom_id
            else:
                r.uom_id = r.uom_id

    def _get_state_field(self):
        return 'line_state'

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
                        r.warehouse_id.lot_stock_id,  # Location Destination
                        _("Stock Allocation Request"),  # Name of Procurement
                        r.approval_id.name,  # Origin
                        r.warehouse_id.company_id,
                        r._prepare_run_values()  # Values
                        )])
            except UserError as error:
                raise UserError(error)

    def _prepare_run_values(self):
        self.ensure_one()
        if not self.procurement_group_id:
            raise ValidationError(_("The procurement group not found for the allocation request line %s") % self.display_name)
        return {
            'warehouse_id': self.warehouse_id,
            'route_ids': self._get_supply_route(self.approval_id.warehouse_id, self.warehouse_id),
            'group_id': self.procurement_group_id,
            'date_planned': self.approval_id.scheduled_date,
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

    def action_cancel(self):
        super(StockAllocationRequestLine, self).action_cancel()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})
    def action_refuse(self):
        super(StockAllocationRequestLine, self).action_refuse()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})

    @api.depends('approval_id.state', 'approval_state_exception')
    def _compute_line_state(self):
        for r in self:
            if not r.approval_id:
                r.line_state = False
            else:
                if not r.approval_state_exception:
                    r.line_state = r.approval_id.state
                else:
                    r.line_state = r._origin.line_state or r.line_state

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.product_id.display_name, r.approval_id.name)))
        return result
