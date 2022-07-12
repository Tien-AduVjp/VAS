from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BalanceCarryForward(models.Model):
    _name = 'balance.carry.forward'
    _description = 'Balance Carry Forward'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", readonly=True, default='/')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('posted', 'Posted'),
            ('cancelled', 'Cancelled')
        ], string="Status", default='draft', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True,
                                 help="Leave this empty so that the rule is applicable to all the available companies.",
                                 readonly=False, states={'confirmed': [('readonly', True)],
                                                         'posted': [('readonly', True)],
                                                         'cancelled': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', string="Journal", required=True, store=True,
                                 domain="[('company_id','=',company_id)]", compute='_compute_journal',
                                 readonly=False, states={'confirmed': [('readonly', True)],
                                                         'posted': [('readonly', True)],
                                                         'cancelled': [('readonly', True)]})
    date = fields.Date(string='Date', required=True, default=fields.Date.today,
                       help="Accounting Date for this operation",
                       readonly=False, states={'confirmed': [('readonly', True)],
                                               'posted': [('readonly', True)],
                                               'cancelled': [('readonly', True)]})
    forward_rule_ids = fields.Many2many('balance.carry.forward.rule', string='Forward Rules',
                                         compute='_compute_forward_rules', store=True,
                                         readonly=False, states={'confirmed': [('readonly', True)],
                                                                 'posted': [('readonly', True)],
                                                                 'cancelled': [('readonly', True)]})
    forward_rule_line_ids = fields.One2many('balance.carry.forward.rule.line', 'forward_id', string='Forward Rules Lines',
                                            compute='_compute_forward_rule_lines', store=True)

    aml_ids = fields.One2many('account.move.line', 'balance_carry_forward_id', string='Journal Items', readonly=True)
    aml_count = fields.Integer(string='Journal Items Count', compute='_compute_aml_count')
    account_move_ids = fields.Many2many('account.move', 'account_move_balance_carry_forward_rel', 'balance_carry_forward_id', 'account_move_id',
                                        string='Journal Entries', compute='_compute_account_moves', store=True)
    account_moves_count = fields.Integer(string='Journal Entries Count', compute='_compute_account_moves_count')

    @api.depends('company_id')
    def _compute_journal(self):
        for r in self:
            r.journal_id = r.company_id.balance_carry_forward_journal_id or False

    @api.depends('date', 'company_id')
    def _compute_forward_rules(self):
        for r in self:
            if r.date and r.company_id:
                domain = [('company_id', '=', r.company_id.id)]
                if not r.date.month == int(r.company_id.fiscalyear_last_month):
                    domain += [('profit_loss', '=', False)]
                r.forward_rule_ids = r.env['balance.carry.forward.rule'].search(domain)
            else:
                r.forward_rule_ids = False

    def _get_source_account_move_lines_domain(self):
        rules = self.forward_rule_ids._origin or self.forward_rule_ids
        return [
            ('account_id', 'in', rules.source_account_ids.ids),
            ('date', '<=', max(self.mapped('date'))),
            ('parent_state', '=', 'posted'),
            ('forward_aml_id', '=', False),
            #  ('forwarded_from_aml_ids', '=', False),
            ('company_id', 'in', self.company_id.ids)
            ]

    @api.depends('forward_rule_ids', 'date', 'company_id')
    def _compute_forward_rule_lines(self):
        self.flush()

        query = self.env['account.move.line']._where_calc(self._get_source_account_move_lines_domain())
        from_clause, where_clause, where_clause_params = query.get_sql()
        # equal as ('forwarded_from_aml_ids', '=', False)
        # Todos: consider on Odoo master / 16+ to using ORM,
        # because Odoo promised to handle on Odoo 16
        where_clause += "AND (SELECT COUNT(*) FROM account_move_line aml WHERE account_move_line.id = aml.forward_aml_id LIMIT 1) = 0"
        query = "SELECT id, account_id, date, company_id FROM " + from_clause + " WHERE " + where_clause
        self.env.cr.execute(query, where_clause_params)

        all_source_aml = self.env.cr.dictfetchall()
        for r in self:
            forward_rule_lines_cmd = [(2, rule_line.id) for rule_line in r.forward_rule_line_ids._origin or r.forward_rule_line_ids]
            if r.date:
                for rule in r.forward_rule_ids._origin or r.forward_rule_ids:
                    for src_account in rule.source_account_ids:
                        source_aml_ids = [vals['id'] for vals in all_source_aml
                                          if vals['account_id'] == src_account.id \
                                          and vals['date'] <= r.date \
                                          and vals['company_id'] == r.company_id.id]
                        vals = rule._prepare_rule_line_vals(source_aml_ids, src_account.id)
                        forward_rule_lines_cmd.append((0, 0, vals))
            r.forward_rule_line_ids = forward_rule_lines_cmd

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('balance.carry.forward')
        records = super(BalanceCarryForward, self).create(vals_list)
        records.mapped('forward_rule_line_ids')._map_succeeding_rule_lines()
        return records

    def write(self, vals):
        res = super(BalanceCarryForward, self).write(vals)
        if 'forward_rule_line_ids' in vals:
            self.mapped('forward_rule_line_ids')._map_succeeding_rule_lines()
        return res

    def action_confirm(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You may not be able to confirm the closing document '%s' while its state is not Draft.")
                                % (r.name,))
            account_move_ids = r.forward_rule_line_ids._generate_account_moves()
            if not account_move_ids:
                raise UserError(_("There is no balance for forwarding in the document '%s'. You may need to change the Date to a later one")
                                % (r.name,))
        self.write({'state':'confirmed'})

    def action_post(self):
        for r in self:
            if r.state != 'confirmed':
                raise UserError(_("You may not be able to post the closing document '%s' while its state is not Confirmed.")
                                % (r.name,))
            r.account_move_ids.filtered(lambda m: m.state != 'posted')._post(soft=False)

            # for displaying on chatter
            links = []
            for m in r.account_move_ids:
                links.append(
                    '<a href=# data-oe-model=account.move data-oe-id={id}>{name}</a>'.format(
                        id=m.id,
                        name=m.name
                        )
                    )
            r.message_post(
                body=_("The following Journal Entries has been posted: %s") % ', '.join(links)
                )
        self.write({'state':'posted'})

    def action_cancel(self):
        moves = self.mapped('account_move_ids')
        if moves:
            moves.button_cancel()
            moves.with_context(force_delete=True).unlink()
        self.message_post(body=_("The related journal entries have been cancelled and deleted"))
        return self.write({'state':'cancelled'})

    def action_draft(self):
        return self.write({'state':'draft'})

    @api.depends('aml_ids')
    def _compute_aml_count(self):
        grouped_data = self.env['account.move.line'].read_group([('balance_carry_forward_id', 'in', self.ids)], ['balance_carry_forward_id'], ['balance_carry_forward_id'])
        mapped_data = dict([(dict_data['balance_carry_forward_id'][0], dict_data['balance_carry_forward_id_count']) for dict_data in grouped_data])
        for r in self:
            r.aml_count = mapped_data.get(r.id, 0)

    def action_view_account_move_lines(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('account.action_account_moves_all')

        # override the context to get rid of the default filtering
        action['context'] = {}

        action['domain'] = "[('balance_carry_forward_id', 'in', %s)]" % self.ids
        return action

    @api.depends('aml_ids.move_id')
    def _compute_account_moves(self):
        for r in self:
            r.account_move_ids = r.aml_ids.mapped('move_id')

    @api.depends('account_move_ids')
    def _compute_account_moves_count(self):
        for r in self:
            r.account_moves_count = len(r.account_move_ids)

    def action_view_account_moves(self):
        move_ids = self.mapped('account_move_ids')

        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')

        # override the context to get rid of the default filtering
        action['context'] = {}

        # choose the view_mode accordingly
        if len(move_ids) != 1:
            action['domain'] = "[('id', 'in', " + str(move_ids.ids) + ")]"
        elif len(move_ids) == 1:
            res = self.env.ref('account.view_move_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = move_ids.id
        return action

    def unlink(self):
        for item in self:
            if item.state != 'draft':
                raise UserError(_('You cannot delete an entry which is not in the draft state.'))
        return super(BalanceCarryForward, self).unlink()

