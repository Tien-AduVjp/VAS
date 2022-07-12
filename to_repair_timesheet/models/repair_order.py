from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_is_zero


class Repair(models.Model):
    _inherit = 'repair.order'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, help="The analytic account related to a repair order.", copy=False)
    timesheet_ids = fields.Many2many('account.analytic.line', compute='_compute_timesheet_ids', string='Timesheet activities associated to this sale')
    timesheet_count = fields.Float(string='Timesheet activities', compute='_compute_timesheet_ids', groups="hr_timesheet.group_hr_timesheet_user")

    tasks_ids = fields.Many2many('project.task', compute='_compute_tasks_ids', string='Tasks associated to this sale')
    tasks_count = fields.Integer(string='Tasks', compute='_compute_tasks_ids', groups="project.group_project_user")

    project_project_id = fields.Many2one('project.project', compute='_compute_project_project_id', string='Project associated to this sale')
    project_ids = fields.Many2many('project.project', compute="_compute_project_ids", string='Projects', copy=False, groups="project.group_project_user", help="Projects used in this sales order.")

    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True, compute_sudo=True)
    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", readonly=True, copy=False, compute_sudo=True)
    invoice_status = fields.Selection([
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_get_invoiced', store=True, readonly=True)
    create_invoice = fields.Boolean(string='To Create Invoices', default=True)

    @api.depends('fees_lines.invoice_lines', 'fees_lines.invoice_status', 'operations.invoice_line_id', 'operations.invoice_status')
    def _get_invoiced(self):
        for r in self:
            invoice_ids = r.fees_lines.invoice_lines.move_id.filtered(lambda r: r.move_type in ['out_invoice', 'out_refund'])
            invoice_ids |= r.operations.invoice_line_id.move_id.filtered(lambda r: r.move_type in ['out_invoice', 'out_refund'])
            refunds = invoice_ids.search([('invoice_origin', 'like', r.name), ('company_id', '=', r.company_id.id)]).filtered(lambda r: r.move_type in ['out_invoice', 'out_refund'])
            invoice_ids |= refunds.filtered(lambda refund: r.name in [origin.strip() for origin in refund.invoice_origin.split(',')])
            # Search for refunds as well
            refund_ids = self.env['account.move'].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search([('move_type', '=', 'out_refund'), ('invoice_origin', '=', inv.name), ('invoice_origin', '!=', False), ('journal_id', '=', inv.journal_id.id)])
            # Ignore the status of the deposit product
            deposit_product_id = self.env['repair.advance.payment.inv']._default_product_id()
            line_invoice_status = [line.invoice_status for line in r.fees_lines if line.product_id != deposit_product_id] + [line.invoice_status for line in r.operations.filtered(lambda x: x.type == 'add' and x.product_id != deposit_product_id)]

            if r.state in ('draft', 'cancel'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            else:
                invoice_status = 'no'

            r.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
                'invoice_status': invoice_status
            })

    def _create_analytic_account(self, prefix=None):
        AnalyticAccount = self.env['account.analytic.account'].sudo()
        for r in self:
            name = r.name
            if prefix:
                name = prefix + ": " + r.name
            analytic = AnalyticAccount.create(self._prepare_analytic_account(name))
            r.analytic_account_id = analytic

    def _prepare_analytic_account(self, name):
        self.ensure_one()
        res = {
            'name': name,
            'code': self.name,
            'company_id': self.env.company.id,
            'partner_id': self.partner_id.id
        }
        return res

    def _prepare_timesheet(self, repair_fee, invoice_line):
        """
            A service product that has tracking_policy = 'delivered_timesheet' (Timesheet on task)

            Invoicing a repair fee with such service product of "timesheet" tracking policy must
                link the created invoice line to the timesheet of the task
            in other words:
                timesheet.timesheet_invoice_id: invoice_line.move_id.id

            It is primary used when an invoiced timesheet is being editting or deleting.
            The timesheet will be check if it is already linked to an invoice line or not.
        """
        invoice_line_condition = (
            invoice_line.move_id.move_type == 'out_invoice' and
            invoice_line.move_id.state == 'draft' and
            repair_fee.product_id.service_type == 'timesheet' and
            invoice_line.repair_fee_line_ids.product_id.invoice_policy == 'delivery'
        )
        if invoice_line_condition:
            domain = [
                ('task_id', '=', repair_fee.task_id.id),
                ('timesheet_invoice_id', '=', False),
                ('project_id', '!=', False)
            ]
            timesheets = self.env['account.analytic.line'].search(domain).sudo()

            return timesheets
        else:
            return self.env['account.analytic.line']

    @api.depends('analytic_account_id.line_ids')
    def _compute_timesheet_ids(self):
        for r in self:
            if r.analytic_account_id:
                r.timesheet_ids = self.env['account.analytic.line'].search(
                    [('ro_line', 'in', r.fees_lines.ids),
                        ('amount', '<=', 0.0),
                        ('project_id', '!=', False)])
            else:
                r.timesheet_ids = []
            r.timesheet_count = len(r.timesheet_ids)

    @api.depends('fees_lines.product_id.project_id')
    def _compute_tasks_ids(self):
        tasks = self.env['project.task'].search([('repair_fee_line_id', 'in', self.fees_lines.ids)])
        for r in self:
            r.tasks_ids = tasks.filtered(lambda t: t.repair_fee_line_id.id in r.fees_lines.ids)
            r.tasks_count = len(r.tasks_ids)

    @api.depends('analytic_account_id.project_ids')
    def _compute_project_project_id(self):
        for r in self:
            r.project_project_id = self.env['project.project'].search([('analytic_account_id', '=', r.analytic_account_id.id)], limit=1)

    @api.depends('fees_lines.product_id', 'project_project_id')
    def _compute_project_ids(self):
        for r in self:
            r.project_ids = r.fees_lines.mapped('product_id.project_id') | r.project_project_id

    def action_repair_confirm(self):
        """ On SO confirmation, some lines should generate a task or a project. """
        result = super(Repair, self).action_repair_confirm()

        # create an analytic account if at least an expense product
        # This behavior is done completely following the behavior of confirming an sales order
        for order in self:
            if any([expense_policy not in [False, 'no'] for expense_policy in order.fees_lines.mapped('product_id.expense_policy')]):
                if not order.analytic_account_id:
                    order._create_analytic_account(prefix=order.product_id.default_code or None)

            fees_lines = order.mapped('fees_lines')
            if fees_lines:
                fees_lines._timesheet_service_generation()
            order.write({'state': 'confirmed'})

        return result

    def action_view_task(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')
        action['context'] = {'group_by':'stage_id'}
        if len(self.tasks_ids) > 1:
            action['domain'] = "[('id','in',%s)]" % self.tasks_ids.ids
        elif len(self.tasks_ids) == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = self.tasks_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_project_ids(self):
        self.ensure_one()
        if len(self.project_ids) == 1:
            if self.env.user.has_group("hr_timesheet.group_hr_timesheet_user"):
                action = self.project_ids.action_view_timesheet_plan()
            else:
                action = self.env['ir.actions.act_window']._for_xml_id("project.act_project_project_2_project_task_all")
                action['context'] = safe_eval(action.get('context', '{}'), {'active_id': self.project_ids.id, 'active_ids': self.project_ids.ids})
        else:
            view_form_id = self.env.ref('project.edit_project').id
            view_kanban_id = self.env.ref('project.view_project_kanban').id
            action = {
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.project_ids.ids)],
                'views': [(view_kanban_id, 'kanban'), (view_form_id, 'form')],
                'view_mode': 'kanban,form',
                'name': _('Projects'),
                'res_model': 'project.project',
            }
        return action

    def action_view_timesheet(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.act_hr_timesheet_line')
        list_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_tree').id
        form_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_form').id
        action['views'] = [[list_view_id, 'tree'], [form_view_id, 'form']]
        if self.timesheet_count > 0:
            action['domain'] = "[('id','in',%s)]" % self.timesheet_ids.ids
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _prepare_invoice(self):
        self.ensure_one()
        # Fallback on the user company as the 'company_id' is not required.
        company = self.company_id or self.env.company
        journal = self.env['account.move'].with_company(company).with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'invoice_origin': self.name,
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'narration': self.internal_notes,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'repair_ids': [(4, self.id)],
        }
        return invoice_vals

    def action_invoice_create(self, group=False, final=False):
        partners = self.mapped('partner_id')

        invoices = []
        for p in partners:
            repair_orders = self.filtered(lambda ro: ro.partner_id.id == p.id)
            invoices_p = repair_orders.action_invoice_create_same_partner(group=group, final=final)
            invoices.extend(invoices_p)

        return invoices

    def action_invoice_create_same_partner(self, group=False, final=False):
        """
            Create the invoice associated to the RO.
            :param group: if True, invoices are grouped by RO id. If False, invoices are grouped by
                            (partner_invoice_id, currency)
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices

            Cases:

            repair order 1:
                partner A
                repair lines:
                    repair line oA_1
                    repair line oA_2
                repair fees:
                    repair fee fA_1
                    repair fee fA_2

            repair order 2:
                partner B
                repair lines:
                    repair line oB_1
                    repair line oB_2
                repair fees:
                    repair fee fB_1
                    repair fee fB_2

            repair order 3:
                partner B
                repair lines:
                    repair line oB_1
                    repair line oB_33
                repair fees:
                    repair fee fB_1
                    repair fee fB_33
        """

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        invoices = {}
        references = {}
        invoice_lines_from_fees = []
        invoice_lines_from_operations = []

        # --- PART 1: ---
        #     Create invoice

        for r in self:
            if not r.create_invoice:
                raise UserError(_("The invoicing feature on this repair order has been deactivated. "
                              "Please check the option 'Create Invoices' in the creation form. "
                              "You need to tick on it to turn on activate the feature."))

            group_key = group and r.partner_invoice_id.id or r.id

            # Add invoice line for fees
            # Using sorted function, we put all the fee lines that are invoiceable before the rest
            # So all invoiceable fee lines will be looped through first.
            for uninvoiced_fee_line in r.fees_lines.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(uninvoiced_fee_line.qty_to_invoice, precision_digits=precision):
                    continue

                # Create invoice only ONCE per order if possible
                invoice = invoices.get(group_key, False)
                if not invoice:
                    inv_data = r._prepare_invoice()
                    invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create(inv_data)
                    invoices[group_key] = invoice
                    references[invoice] = r

                feeline = uninvoiced_fee_line._prepare_invoice_lines_from_fees(invoices[group_key].id, 1)

                qty_to_invoice_is_positive = uninvoiced_fee_line.qty_to_invoice > 0
                qty_to_invoice_is_negative = uninvoiced_fee_line.qty_to_invoice < 0

                if qty_to_invoice_is_positive or qty_to_invoice_is_negative and final:
                    feeline = uninvoiced_fee_line._prepare_invoice_lines_from_fees(
                        invoices[group_key].id,
                        uninvoiced_fee_line.qty_to_invoice
                    )

                invoice_lines_from_fees.extend(feeline)

            # add invoice line for operations
            for operation in r.operations.filtered(lambda x: not x.invoice_line_id):
                if operation.type == 'add':
                    if operation.product_id.property_account_income_id:
                        account_id = operation.product_id.property_account_income_id.id
                    elif operation.product_id.categ_id.property_account_income_categ_id:
                        account_id = operation.product_id.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('No account defined for product "%s".') % operation.product_id.name)

                    # Create invoice only ONCE per order if possible
                    invoice = invoices.get(group_key, False)
                    if not invoice:
                        inv_data = r._prepare_invoice()
                        invoice = self.env['account.move'].with_context(default_move_type='out_invoice').create(inv_data)
                        invoices[group_key] = invoice
                        references[invoice] = r

                    balance = -(operation.product_uom_qty * operation.price_unit)

                    invoice_lines_from_operations.append(
                        {
                            'move_id': invoice.id,
                            'name': operation.name,
                            'account_id': account_id,
                            'quantity': operation.product_uom_qty,
                            'tax_ids': [(6, 0, [x.id for x in operation.tax_id])],
                            'product_uom_id': operation.product_uom.id,
                            'price_unit': operation.price_unit,
                            'price_subtotal': operation.product_uom_qty * operation.price_unit,
                            'product_id': operation.product_id and operation.product_id.id or False,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'repair_line_ids': [(4, operation.id)],
                        }
                    )

                    operation.write({'invoiced': True})

            if references.get(invoices.get(group_key)):
                if r not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= r

        # --- PART 2: ---
        #     Check if no invoice is created then raise an error and terminate the function

        if not invoices:
            raise UserError(_("There is no invoiceable line."))

        # --- PART 3: ---
        #     Update the related fields with corresponding values that are retrieved from the previous parts

        invoice_lines = invoice_lines_from_operations + invoice_lines_from_fees
        for k_e_y in invoices:
            if len(self) == 1:
                # one repair order at a time for both cases group = True or group = False
                # just assign all invoice lines to this one invoice
                invoices[group_key].write({'invoice_line_ids': [(0, 0, line) for line in invoice_lines]})
            else:
                if group:
                    # if group = True and multi repair orders and same partner
                    # Assign all invoice lines to this one invoice
                    invoices[k_e_y].write({'invoice_line_ids': [(0, 0, line) for line in invoice_lines]})
                else:
                    # If group = False and multi repair orders and different partner
                    # There will be 2 invoices created
                    # => Assign only invoice lines to the corresponding invoice, one by one
                    # Fx. invoice A has only invoice_lines A and B
                    #     invoice B has only invoice_lines C and D
                    for inv_line_dict_obj in invoice_lines:
                        if inv_line_dict_obj['move_id'] == invoices[k_e_y].id:
                            invoices[k_e_y].write({'invoice_line_ids': [(0, 0, inv_line_dict_obj)]})

        # Update field 'invoice_line_id' on each being-updated repair fee
        newly_created_invoice_lines = self.env['account.move.line']
        for invoice in invoices.values():
            newly_created_invoice_lines |= invoice.invoice_line_ids

        for repair_fee in self.fees_lines:
            invoice_line_for_repair_fee = newly_created_invoice_lines.filtered(lambda inv_line: inv_line.repair_fee_line_ids[:1].id == repair_fee.id)
            if invoice_line_for_repair_fee:
                repair_fee.write({
                    'invoice_line_id': invoice_line_for_repair_fee.id,
                    'invoiced': True,
                })
                # Find and link the timesheet to the created invoice if possible
                timesheets = self._prepare_timesheet(repair_fee, invoice_line_for_repair_fee)
                if timesheets:
                    timesheets.write({
                        'timesheet_invoice_id': invoice_line_for_repair_fee.move_id.id
                    })

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.move_type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'invoice_origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)

        return [inv.id for inv in invoices.values()]
