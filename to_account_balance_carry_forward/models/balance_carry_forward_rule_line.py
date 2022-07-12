from odoo import models, fields, api, _


class BalanceCarryForwardRuleLine(models.Model):
    _name = 'balance.carry.forward.rule.line'
    _description = 'Balance carry Forward Rule Line'
    _order = 'rule_id, sequence'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    forward_id = fields.Many2one('balance.carry.forward', string='Balance Forward Document', required=True, ondelete='cascade')
    rule_id = fields.Many2one('balance.carry.forward.rule', string='Rule')
    sequence = fields.Integer(string='Sequence')
    forward_type = fields.Selection(related='rule_id.forward_type', store=True)

    source_account_id = fields.Many2one('account.account', string='Source Account', required=True,
                                        help="The source account from which the balance will be carried forward.")
    dest_account_id = fields.Many2one('account.account', string='Destination Account', required=True,
                                      help="The destination account to which the balance of the source account is brought")

    succeeding_rule_line_ids = fields.Many2many('balance.carry.forward.rule.line', 'balance_forward_preceding_rule_line_suceeding_rule_line_rel',
                                               'preceding_rule_line_id', 'succeeding_rule_line_id',
                                                string='Succeeding Rules',)

    preceding_rule_line_ids = fields.Many2many('balance.carry.forward.rule.line', 'balance_forward_preceding_rule_line_suceeding_rule_line_rel',
                                               'succeeding_rule_line_id', 'preceding_rule_line_id', string='Preceding Rules',
                                              help="The rules required to be excecuted and done before executing this rule")
    source_aml_ids = fields.Many2many('account.move.line', string='Source Journal Items')
    balance = fields.Float(string='Source Account Balance', compute='_compute_balance', store=True,
                           help="The balance summary of the accounts of the source journal items which is computed as debit sum - credit sum")

    @api.depends('source_account_id.name', 'dest_account_id.name')
    def _compute_name(self):
        for r in self:
            r.name = '[%s > %s] %s' % (r.source_account_id.code, r.dest_account_id.code, r.rule_id.name)

    @api.depends('source_aml_ids.balance')
    def _compute_balance(self):
        self.flush()

        if not self.source_aml_ids.ids:
            for r in self:
                r.balance = 0.0
            return

        self.env.cr.execute(
            "SELECT id, balance FROM account_move_line WHERE id IN %s",
            [tuple(self.source_aml_ids.ids)],
        )
        all_source_aml = self.env.cr.dictfetchall()

        data = {aml['id']: aml['balance'] for aml in all_source_aml}
        for r in self:
            r.balance = sum(data[aml_id] for aml_id in r.source_aml_ids.ids)

    def _find_succeeding_rule_lines(self):
        self.ensure_one()
        succeeding_rule_lines = self.search([
            ('id', '!=', self.id),
            ('forward_id', '=', self.forward_id.id),
            ('source_account_id', '=', self.dest_account_id.id),
            ('rule_id.preceding_rule_ids', 'in', [self.rule_id.id])])
        return succeeding_rule_lines

    def _map_succeeding_rule_lines(self):
        for r in self:
            r.succeeding_rule_line_ids = r._find_succeeding_rule_lines() or False

    def _prepare_acc_move_lines_domain(self):
        domain = [
            ('account_id', 'in', self.source_account_id.ids),
            ('date', '<=', max(self.forward_id.mapped('date'))),
            ('forward_aml_id', '=', False),
            # ('forwarded_from_aml_ids', '=', False),
            ('company_id', 'in', self.forward_id.company_id.ids),
        ]
        if not self._context.get('include_draft_move_lines', False):
            domain.append(('parent_state', '=', 'posted'))
        return domain

    def _generate_account_moves(self):
        self.flush()
        if not self.forward_id:
            return self.env['account.move']

        query = self.env['account.move.line']._where_calc(
            self._prepare_acc_move_lines_domain()
        )
        from_clause, where_clause, where_clause_params = query.get_sql()
        # equal as ('forwarded_from_aml_ids', '=', False)
        # Todos: consider on Odoo master / 16+ to using ORM,
        # because Odoo promised to handle on Odoo 16
        where_clause += "AND (SELECT COUNT(*) FROM account_move_line aml WHERE account_move_line.id = aml.forward_aml_id LIMIT 1) = 0"
        query = "SELECT id, account_id, date, company_id FROM " + from_clause + " WHERE " + where_clause
        self.env.cr.execute(query, where_clause_params)

        all_source_amls = self.env.cr.dictfetchall()

        moves = self.env['account.move']
        with self.env.cr.savepoint():
            for r in self:
                source_aml_data = [v['id'] for v in all_source_amls \
                                   if v['account_id'] == r.source_account_id.id \
                                   and v['date'] <= r.forward_id.date \
                                   and v['company_id'] == r.forward_id.company_id.id]
    
                if not source_aml_data:
                    continue
                source_amls = self.env['account.move.line'].browse(set(source_aml_data))
                move_vals = source_amls._prepare_balance_carry_forward_move_data(r.forward_id.journal_id, r.dest_account_id, r.forward_id.date)
    
                # inject forward rule line into account.move.line for tracking later
                move_vals['line_ids'][0][2]['forward_line_id'] = r.id
                move_vals['line_ids'][1][2]['forward_line_id'] = r.id
                move = self.env['account.move'].create(move_vals)
                move.message_post(
                    body=_("The entry was generated from the %s") % '<a href=# data-oe-model=balance.carry.forward data-oe-id={id}>{name}</a>'.format(
                        id=r.forward_id.id,
                        name=r.forward_id.name
                        )
                    )
                moves += move
    
                new_lines_data = [
                    {
                        'id': line.id,
                        'account_id': line.account_id.id,
                        'date': line.date,
                        'company_id': line.company_id.id,
                    } for line in move.line_ids
                ]
                all_source_amls.extend(new_lines_data)
    
                new_line_id = [line['id'] for line in new_lines_data if line['account_id'] == r.source_account_id.id][0]
                # equal as new_line_id.forwarded_from_aml_ids = source_amls
                # this is not using invalidate_cache because we is not using ORM method
                r._cr.execute("""
                    UPDATE account_move_line
                    SET forward_aml_id = %s
                    WHERE id IN %s
                """, [new_line_id, tuple(source_aml_data)])
        return moves
