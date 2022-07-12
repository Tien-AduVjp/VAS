from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class StockAllocationRequest(models.Model):
    _name = 'stock.allocation.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Stock Allocation Request'
    _order = 'scheduled_date asc, id desc'

    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    def _default_approval_user(self):
        return self.env.ref('stock.group_stock_manager').users[0] or False

    def _default_approval_user_domain(self):
        return [('id', 'in', self.env.ref('stock.group_stock_manager').users.ids)]

    name = fields.Char(string='Name', required=True, index=True, copy=False, default='New')
    warehouse_id = fields.Many2one('stock.warehouse', string='Source Warehouse', tracking=True, default=_default_warehouse_id,
                                   required=True, readonly=False, states={'waiting': [('readonly', True)],
                                                                          'approved': [('readonly', True)],
                                                                          'refused': [('readonly', True)],
                                                                          'done': [('readonly', True)],
                                                                          'cancelled': [('readonly', True)]},
                                   help="The warehouse for which the allocation is.")
    line_ids = fields.One2many('stock.allocation.request.line', 'request_id', string='Stock Allocation Request Lines',
                                     readonly=False, states={'approved': [('readonly', True)],
                                                             'refused': [('readonly', True)],
                                                             'done': [('readonly', True)],
                                                             'cancelled': [('readonly', True)]})
    note = fields.Text(string='Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True, copy=False, index=True)
    scheduled_date = fields.Date(string='Scheduled Date', default=fields.date.today(), required=True, tracking=True,
                                 readonly=False, states={'waiting': [('readonly', True)],
                                                         'approved': [('readonly', True)],
                                                         'refused': [('readonly', True)],
                                                         'done': [('readonly', True)],
                                                         'cancelled': [('readonly', True)]})
    approval_date = fields.Date(string='Approval Date', readonly=True, help="The date on which the request is approved.")
    responsible_id = fields.Many2one('res.users', string='Approval User', default=_default_approval_user, domain=_default_approval_user_domain,
                                     tracking=True,
                                     help="The user who will be responsible for approving/refusing the request.")

    procurement_group_ids = fields.One2many('procurement.group', 'stock_allocation_request_id', string='Procurement Group', store=True)
    procurement_groups_count = fields.Integer(string='Procurement Groups Count', compute='_compute_procurement_groups_count')

    picking_ids = fields.Many2many('stock.picking', 'stock_allocation_request_stock_picking_rel', 'request_id', 'picking_id', string='Transfers',
                                   compute='_compute_picking_ids', store=True)
    pickings_count = fields.Integer(string='Pickings Count', compute="_compute_pickings_count")

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

    # Used to search on request
    product_id = fields.Many2one('product.product', 'Product', related='line_ids.product_id', readonly=False)

    def _check_done(self):
        for r in self.filtered(lambda r: r.state == 'approved'):
            if r.picking_ids.filtered(lambda p: p.state != 'done'):
                continue
            else:
                r.action_done()

    def _compute_procurement_groups_count(self):
        data = self.env['procurement.group'].read_group(
            [('stock_allocation_request_id', 'in', self.ids)], ['stock_allocation_request_id'], ['stock_allocation_request_id'])
        mapped_data = dict([(dict_data['stock_allocation_request_id'][0], dict_data['stock_allocation_request_id_count']) for dict_data in data])
        for r in self:
            r.procurement_groups_count = mapped_data.get(r.id, 0)

    @api.depends('procurement_group_ids', 'state')
    def _compute_picking_ids(self):
        all_picking_ids = self._get_stock_pickings()
        for r in self:
            picking_ids = all_picking_ids.filtered(lambda p: p.group_id.id in r.procurement_group_ids.ids)
            if r.state == 'approved' and picking_ids:
                r.picking_ids = [(6, 0, picking_ids.ids)]
            else:
                r.picking_ids = [(3, item.id) for item in r.picking_ids] if r.picking_ids else False

    def _compute_pickings_count(self):
        for r in self:
            r.pickings_count = len(r.picking_ids)

    @api.constrains('responsible_id')
    def _check_responsible_id(self):
        approval_group_id = self.env.ref('stock.group_stock_manager')
        for r in self:
            if r.responsible_id and not r.responsible_id.has_group('stock.group_stock_manager'):
                raise ValidationError(_("%s is not the user who has proper access rights to approve the stock allocation request %s."
                                        " She or he must has %s access rights to do so.")
                                        % (r.responsible_id.name, r.name, approval_group_id.name))

    def _prepare_stock_pickings_search_domain(self):
        """
        For potential inheritance
        """
        return [('group_id', 'in', self.mapped('procurement_group_ids').ids)]

    def _get_stock_pickings(self):
        return self.env['stock.picking'].search(self._prepare_stock_pickings_search_domain())

    def _notify_manager(self):
        current_user = self.env.user
        for r in self.filtered(lambda record: record.responsible_id and record.responsible_id != current_user):
            email_template_id = self.env.ref('to_stock_product_allocation.email_template_submit_notification')
            r.message_post_with_template(email_template_id.id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.allocation.request') or '/'
        return super(StockAllocationRequest, self).create(vals_list)

    def _get_non_zero_qty_lines(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return self.mapped('line_ids').filtered(lambda l: not float_is_zero(l.quantity, precision_digits=precision))

    def _prepare_procurement_group_data(self, partner_id):
        return {
            'partner_id': partner_id.id,
            'name': self.name,
            'stock_allocation_request_id': self.id,
            }

    def action_draft(self):
        for r in self:
            if r.state not in ('refused', 'cancelled'):
                raise ValidationError(_("You cannot set the stock allocation request %s to Draft state while it is neither Refused nor Cancelled!")
                                      % r.name)
        return self.write({'state':'draft'})

    def action_confirm(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot submit a stock allocation request that is not in Draft state."))
            if not r._get_non_zero_qty_lines():
                raise ValidationError(_("You must have at least one non-zero quantity line to submit for approval."
                                        " Submitting a zero-quanity line does not make sense."))
        self.write({'state':'waiting'})
        if(self.env.user.has_group('stock.group_stock_manager')):
            self.action_approve()
        else:
            self._notify_manager()

    def action_approve(self):
        ProcurementGroup = self.env['procurement.group']
        for r in self:
            if r.state not in ('refused', 'waiting'):
                raise ValidationError(_("You cannot approve a Stock Allocation Request whose state is neither Refused nor Waiting Approval"))

            # we will work on non-zero quantity lines only
            line_ids = r._get_non_zero_qty_lines()

            # if we have responsible user on the request, create a single procurement group only
            if r.responsible_id:
                procurement_group_id = ProcurementGroup.create(r._prepare_procurement_group_data(r.responsible_id.partner_id))
                line_ids.write({'procurement_group_id': procurement_group_id.id})

            # Otherwise, we create procurement groups for each product's responsible user
            else:
                for partner_id in line_ids.mapped('product_id.responsible_id.partner_id'):
                    partner_line_ids = line_ids.filtered(lambda l: l.product_id.responsible_id.partner_id == partner_id)
                    procurement_group_id = ProcurementGroup.create(r._prepare_procurement_group_data(partner_id))
                    partner_line_ids.write({'procurement_group_id': procurement_group_id.id})
                    line_ids -= partner_line_ids

                # the remaining lines whose product has no value in the field responsible_id.
                # this is mostly for the database having something wrong because the responsible_id
                # should always have data when it is a required field
                if line_ids:
                    approval_user = self._default_approval_user()
                    procurement_group_id = ProcurementGroup.create(r._prepare_procurement_group_data(approval_user.partner_id))
                    line_ids.write({'procurement_group_id': procurement_group_id.id})

            line_ids.launch_allocation()

        self.write({
            'state':'approved',
            'responsible_id':self.env.user.id,
            'approval_date': fields.Date.today()
            })

    def action_refuse(self):
        for r in self:
            if r.state != 'waiting':
                raise ValidationError(_("You cannot refuse a Stock Allocation Request that is not in Waiting Approval state."))
        return self.write({'state':'refused'})

    def action_done(self):
        for r in self:
            if r.state != 'approved':
                raise ValidationError(_("You cannot set the stock allocation request %s as Done while its state is not Approved!")
                                      % r.name)
            if r.mapped('picking_ids').filtered(lambda p: p.state not in ('done', 'cancel')):
                raise ValidationError(_("You cannot done a Stock Allocation Request which has not done transfers."))
        return self.write({'state':'done'})

    def action_cancel(self):
        for r in self:
            if r.state not in ('refused', 'waiting', 'approved'):
                raise ValidationError(_("You cannot cancel a Stock Allocation Request whose state is neither Refused nor Waiting Approval nor Approved!"))
        if self.mapped('picking_ids').filtered(lambda p: p.state == 'done'):
            raise ValidationError(_("You cannot cancel a Stock Allocation Request which has done Transfers."))
        self.mapped('picking_ids').filtered(lambda p: p.state != 'done').action_cancel()
        self.write({'state':'cancelled'})

    def action_view_procurement_groups(self):
        self.ensure_one()

        action = self.env.ref('to_stock_product_allocation.action_procurement_group_view')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        if self.procurement_groups_count > 1:
            result['domain'] = "[('stock_allocation_request_id', '=', %s)]" % self.id
        elif self.procurement_groups_count == 1:
            res = self.env.ref('stock.procurement_group_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.procurement_group_ids.id
        return result

    def action_view_stock_pickings(self):
        self.ensure_one()

        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        if self.pickings_count > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.picking_ids.ids
        elif self.pickings_count == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.picking_ids.id
        return result

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise ValidationError(_("You cannot delete the stock allocation request %s while it is not in Draft state.") % r.name)

            if self.env.user != r.create_uid and not self.env.user.has_group('stock.group_stock_manager'):
                raise ValidationError(_("You are not allowed to delete the stock allocation request %s."
                                        " You must be either the user who has created the request"
                                        " or the one who has %s access rights to do so")
                                        % (r.name, self.env.ref('stock.group_stock_manager').display_name))
        return super(StockAllocationRequest, self).unlink()
