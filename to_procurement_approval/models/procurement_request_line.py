from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context

from odoo.addons.to_approvals.models.abstract_approval_request_line import STATUS


class ProcurementApprovalLine(models.Model):
    _name = 'procurement.request.line'
    _description = 'Procurement request line'
    _inherit = 'abstract.approval.request.line'

    state = fields.Selection(STATUS, default='draft', store=True, compute='_compute_state', string='Status')
    approval_id = fields.Many2one('approval.request', string='Approval request', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('purchase_ok', '=', True)])
    category_uom_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True, compute='_compute_product_info', store=True, readonly=False,
                             domain="[('category_id', '=', category_uom_id)]")
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0.0, required=True)
    description = fields.Text(string='Description', compute='_compute_product_info', store=True, readonly=False)
    type = fields.Selection(string='Type', related='product_id.type')
    route_ids = fields.Many2many('stock.location.route', string='Preferred Routes',
                                     help="This is to override the routes set on the product."
                                     " If no route selected, the routes specified for the product will be used.")
    procurement_group_id = fields.Many2one('procurement.group', string='Procurment Group', readonly=True,
                                           help=_("Technical field to store the procurement group generated automatically during procurement request approval."))
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=False, help="The warehouse for which the procurement is.")
    approval_state_exception = fields.Boolean(string='Approval Status Exception', readonly=True,
                                     help="This field indicates the status of this plan is an exception of its approval request."
                                     " For example: when a plan of a requests' is cancelled/refused while others are not, the plan"
                                     " will be marked as `Approval Status Exception`.")

    def _get_state_field(self):
        return 'state'

    @api.depends('product_id')
    def _compute_product_info(self):
        warehouses = self.env['stock.warehouse'].search([('company_id', 'in', self.approval_id.company_id.ids)])
        for r in self:
            r.uom_id = r.product_id.uom_id
            r.description = r.product_id.description
            if r.type == 'product' and not r.warehouse_id:
                r.warehouse_id = warehouses.filtered(lambda wh: wh.company_id == r.approval_id.company_id)[:1]
            else:
                r.warehouse_id = r.warehouse_id

    def launch_procurement(self):
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
                        r.warehouse_id.lot_stock_id,  # Location Destination
                        _("Procurement Request"),  # Name of Procurement
                        r.approval_id.name,  # Origin
                        r.warehouse_id.company_id,
                        r._prepare_run_values(),  # Values
                    )
                ])

            except UserError as error:
                raise UserError(error)

    def _prepare_run_values(self):
        self.ensure_one()
        if not self.procurement_group_id:
            raise ValidationError(_("The procurement group not found for the procurement request line %s") % self.display_name)
        return {
            'warehouse_id': self.warehouse_id,
            'route_ids': self.route_ids,
            'group_id': self.procurement_group_id,
            'date_planned': self.approval_id.date,
        }

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.product_id.display_name, r.approval_id.name)))
        return result

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot remove a line while its corresponding request is not in draft state."))
        return super(ProcurementApprovalLine, self).unlink()

    def action_cancel(self):
        super(ProcurementApprovalLine, self).action_cancel()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})

    def action_refuse(self):
        super(ProcurementApprovalLine, self).action_refuse()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})

    @api.depends('approval_id.state', 'approval_state_exception')
    def _compute_state(self):
        for r in self:
            if not r.approval_id:
                r.state = False
            else:
                if not r.approval_state_exception:
                    r.state = r.approval_id.state
                else:
                    r.state = r._origin.state or r.state
