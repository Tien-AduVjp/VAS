import threading

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    warehouse_id = fields.Many2one('stock.warehouse', string='Source Warehouse', tracking=True, default=_default_warehouse_id,
                                   states={'confirm': [('readonly', True)],
                                           'validate': [('readonly', True)],
                                           'refuse': [('readonly', True)],
                                           'done': [('readonly', True)],
                                           'cancel': [('readonly', True)]}, help="The warehouse for which the allocation is.")
    allocation_request_line_ids = fields.One2many('stock.allocation.request.line', 'approval_id', string='Stock Allocation Request Lines',
                                                  groups='stock.group_stock_user',
                                                  states={'validate': [('readonly', True)],
                                                          'refuse': [('readonly', True)],
                                                          'done': [('readonly', True)],
                                                          'cancel': [('readonly', True)]})
    scheduled_date = fields.Date(string='Scheduled Date', default=fields.date.today(), tracking=True,
                                 states={'confirm': [('readonly', True)],
                                         'validate': [('readonly', True)],
                                         'refuse': [('readonly', True)],
                                         'done': [('readonly', True)],
                                         'cancel': [('readonly', True)]})

    procurement_group_ids = fields.One2many('procurement.group', 'approval_id', string='Procurement Group', store=True)
    # TODOs: handle to avoid conflict with module to_procurement_approval:
    # picking_ids = fields.One2many...
    # pickings_count = fields.Integer
    pickings_id = fields.Many2many('stock.picking', 'stock_allocation_request_stock_picking_rel', 'approval_id', 'picking_id', string='Allocation Transfers',
                                   compute='_compute_pickings_id', groups='stock.group_stock_user', store=True)
    picking_count = fields.Integer(string='Pickings Count', compute='_compute_picking_count', groups='stock.group_stock_user')

    @api.constrains('warehouse_id')
    def _check_warehouse_id(self):
        self.sudo().allocation_request_line_ids._check_warehouse_id()

    def _check_done(self):
        for r in self.filtered(lambda r: r.state == 'validate'):
            if r.pickings_id.filtered(lambda p: p.state != 'done'):
                continue
            else:
                r.action_done()

    def _compute_procurement_groups_count(self):
        data = self.env['procurement.group'].read_group(
            [('approval_id', 'in', self.ids)], ['approval_id'], ['approval_id'])
        mapped_data = dict([(dict_data['approval_id'][0], dict_data['approval_id_count']) for dict_data in data])
        for r in self:
            r.procurement_groups_count = mapped_data.get(r.id, 0)

    @api.depends('procurement_group_ids.stock_move_ids', 'state')
    def _compute_pickings_id(self):
        all_pickings = self._get_stock_pickings()
        for r in self:
            pickings = all_pickings.filtered(lambda p: p.group_id in r.procurement_group_ids)
            if r.state == 'validate' and pickings:
                r.pickings_id = [(6, 0, pickings.ids)]
            else:
                r.pickings_id = [(3, item.id) for item in r.pickings_id] if r.pickings_id else False

    def _compute_picking_count(self):
        for r in self:
            r.picking_count = len(r.pickings_id)

    def _prepare_stock_pickings_search_domain(self):
        """
        For potential inheritance
        """
        return [('group_id', 'in', self.procurement_group_ids.ids)]

    def _get_stock_pickings(self):
        return self.env['stock.picking'].search(self._prepare_stock_pickings_search_domain())

    def _get_non_zero_qty_lines(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return self.sudo().allocation_request_line_ids.filtered(lambda l: not float_is_zero(l.quantity, precision_digits=precision))

    def _prepare_procurement_group_data(self, partner_id):
        return {
            'partner_id': partner_id.id,
            'name': self.name,
            'approval_id': self.id,
            }

    def action_confirm(self):
        for r in self:
            if r.approval_type_id.type == 'stock_allocation' and not r._get_non_zero_qty_lines():
                raise ValidationError(_("You must have at least one non-zero quantity line to submit for approval."
                                        " Submitting a zero-quanity line does not make sense."))
        return super(ApprovalRequest, self).action_confirm()

    def action_validate(self):
        res = super(ApprovalRequest, self).action_validate()
        ProcurementGroup = self.env['procurement.group']
        for r in self.filtered(lambda request: request.state == 'validate' and request.type == 'stock_allocation'):
            # if we have responsible user on the request, create a single procurement group only
            procurement_group_id = ProcurementGroup.create(r._prepare_procurement_group_data(r.env.user.partner_id))

            # we will work on non-zero quantity lines only
            line_ids = r._get_non_zero_qty_lines().filtered(lambda line: line.line_state == 'validate')
            line_ids.write({'procurement_group_id': procurement_group_id.id})
            line_ids.launch_allocation()
        return res

    def action_done(self):
        for r in self:
            if r.type == 'stock_allocation':
                for picking in r.pickings_id:
                    if picking.state not in ('done', 'cancel'):
                        raise ValidationError(_("You cannot done a Stock Allocation Request which has not done transfers."))
        return super(ApprovalRequest, self).action_done()

    def action_refuse(self):
        pickings = self.env['stock.picking']
        for r in self:
            if r.type == 'stock_allocation':
                for picking in r.pickings_id:
                    if picking.state == 'done':
                        raise ValidationError(_("You cannot refuse a Stock Allocation Request which has done Transfers."))
                    else:
                        pickings |= picking
        if pickings:
            pickings.action_cancel()
        return super(ApprovalRequest, self).action_refuse()

    def action_cancel(self):
        pickings = self.env['stock.picking']
        for r in self:
            if r.type == 'stock_allocation':
                for picking in r.pickings_id:
                    if picking.state == 'done':
                        raise ValidationError(_("You cannot cancel a Stock Allocation Request which has done Transfers."))
                    else:
                        pickings |= picking
        if pickings:
            pickings.action_cancel()
        return super(ApprovalRequest, self).action_cancel()

    def action_view_procurement_groups(self):
        self.ensure_one()

        action = self.env['ir.actions.act_window']._for_xml_id('to_stock_product_allocation_approval.action_procurement_group_view')

        # get rid off the default context
        action['context'] = {}
        if len(self.procurement_group_ids) == 1:
            res = self.env.ref('stock.procurement_group_form_view', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.procurement_group_ids.id
        else:
            action['domain'] = [('id', 'in', self.procurement_group_ids.ids)]
        return action

    def action_view_stock_pickings(self):
        self.ensure_one()

        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')

        # get rid off the default context
        action['context'] = {}

        if self.picking_count > 1:
            action['domain'] = "[('id', 'in', %s)]" % self.pickings_id.ids
        elif self.picking_count == 1:
            res = self.env.ref('stock.view_picking_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.pickings_id.id
        return action
