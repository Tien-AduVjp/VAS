from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class Deferral(models.Model):
    _name = 'cost.revenue.deferral'
    _description = 'Cost Revenue Deferral'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, readonly=True, states={'draft':[('readonly', False)]})
    type = fields.Selection([
        ('cost', 'Cost'),
        ('revenue', 'Revenue'),
    ], string="Deferral Type", required=True, readonly=True, states={'draft':[('readonly', False)]})
    deferral_category_id = fields.Many2one('cost.revenue.deferral.category', string="Deferral Category", required=True,
        readonly=True, states={'draft':[('readonly', False)]})
    date = fields.Date(string="Entry Date", required=True, default=fields.Date.today, readonly=True, states={'draft':[('readonly', False)]})
    value = fields.Float(string="Value", required=True, digits='Account', readonly=True, states={'draft':[('readonly', False)]})
    salvage_value = fields.Float(string="Salvage Value", digits='Account', readonly=True, states={'draft':[('readonly', False)]})
    value_residual = fields.Float(string="Residual Value", compute='_compute_value_residual', method=True, digits='Account')
    partner_id = fields.Many2one('res.partner', string="Partner", readonly=True, states={'draft':[('readonly', False)]})
    method = fields.Selection([
        ('linear', 'Linear'),
        ('degressive', 'Degressive')
    ], string="Computation Method", required=True, default='linear', readonly=True, states={'draft':[('readonly', False)]})
    method_time = fields.Selection([
        ('number', 'Number of Deferrals'),
        ('end', 'Ending Date'),
    ], string="Time Method", required=True, default='number', readonly=True, states={'draft':[('readonly', False)]})
    method_number = fields.Integer(string="Number of Deferrals", default=5, readonly=True, states={'draft':[('readonly', False)]})
    method_period = fields.Integer(string="Number of Months in a Period", required=True, default=12, readonly=True, states={'draft':[('readonly', False)]})
    method_end = fields.Date(string="Ending Date", readonly=True, states={'draft':[('readonly', False)]})
    note = fields.Text(string="Note")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft':[('readonly', False)]},
        default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id.id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Running'),
        ('close', 'Close')
    ], string="Status", required=True, readonly=True, default='draft', copy=False)
    deferral_line_ids = fields.One2many('cost.revenue.deferral.line', 'deferral_id', string="Deferral Lines",
        readonly=True, states={'draft':[('readonly', False)], 'open':[('readonly', False)]})
    account_move_line_ids = fields.One2many('account.move.line', 'deferral_id', string="Entries", readonly=True, states={'draft':[('readonly', False)]})
    move_line_count = fields.Integer(string="# Deferral Entries", compute='_compute_move_line_count')
    auto_create_move = fields.Boolean(string="Auto-Posted Deferral", readonly=True, 
                                      states={'draft':[('readonly', False)], 'open':[('readonly', False)]},
                                      default=False, help="Check this if you want to automatically generate the deferral lines of running deferral and posted this deferral.")

    @api.constrains('type', 'deferral_category_id')
    def _check_type_consistent(self):
        for r in self:
            if r.deferral_category_id.type != r.type:
                raise ValidationError(_("The type of the deferral must be the same as the one of the corresponding category."))

    @api.depends('value', 'salvage_value', 'deferral_line_ids.move_check', 'deferral_line_ids.amount')
    def _compute_value_residual(self):
        total_amount = 0.0
        for r in self:
            for line in r.deferral_line_ids:
                if line.move_check:
                    total_amount += line.amount
            r.value_residual = r.value - total_amount - r.salvage_value

    @api.depends('account_move_line_ids')
    def _compute_move_line_count(self):
        for r in self:
            r.move_line_count = len(r.account_move_line_ids)

    @api.onchange('deferral_category_id')
    def onchange_deferral_category_id(self):
        self.method = self.deferral_category_id.method
        self.method_time = self.deferral_category_id.method_time
        self.method_number = self.deferral_category_id.method_number
        self.method_period = self.deferral_category_id.method_period
        self.method_end = self.deferral_category_id.method_end
        self.auto_create_move = self.deferral_category_id.auto_create_move

    def open_entries(self):
        context = dict(self._context or {}, search_default_deferral_id=self.ids, default_deferral_id=self.ids)
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }

    @api.model
    def compute_generated_entries(self, date):
        deferral_lines = self.env['cost.revenue.deferral.line'].search([
            ('state', '=', 'open'),
            ('deferral_date', '<=', date),
            ('move_check', '=', False)])
        deferral_lines_auto_post = deferral_lines.filtered(lambda r:r.deferral_id.auto_create_move)
        created_move_ids = deferral_lines_auto_post.create_move()
        created_move_ids += (deferral_lines - deferral_lines_auto_post).create_move(post_move=False)
        return created_move_ids

    def validate(self):
        self.compute_deferral_board()
        self.write({'state': 'open'})

    def set_to_close(self):
        self.write({'state': 'close'})

    def set_to_draft(self):
        for r in self:
            if r.deferral_line_ids.move_id.filtered(lambda m:m.state != 'cancel'):
                raise UserError(_("You need to cancel all journal entries of the deferral '%s' first.") % (r.name))
        self.write({'state': 'draft'})

    def _get_last_deferral_date(self):
        """
        @param id: ids of a account.asset.asset objects
        @return: Returns a dictionary of the effective dates of the last deferral entry made for given asset ids. If there isn't any, return the purchase date of this asset
        """
        self._cr.execute("""
            SELECT a.id as id, COALESCE(MAX(l.date),a.date) AS date
            FROM cost_revenue_deferral a
            LEFT JOIN account_move_line l ON (l.deferral_id = a.id)
            WHERE a.id IN %s
            GROUP BY a.id, a.date """, (tuple(self.ids),))
        return dict(self._cr.fetchall())

    def _get_board_undone_dotation_nb(self, deferral_date):
        undone_dotation_number = self.method_number
        if self.method_time == 'end':
            end_date = self.method_end
            undone_dotation_number = 0
            while deferral_date <= end_date:
                deferral_date = fields.Date.add(deferral_date, months=self.method_period)
                undone_dotation_number += 1
        return undone_dotation_number

    # def _get_board_amount(self, i, residual_amount, amount_to_depr, undone_dotation_number, total_days, deferral_date):
    #     # by default amount = 0
    #     amount = 0
    #     if i == undone_dotation_number:
    #         amount = residual_amount
    #     else:
    #         if self.method == 'linear':
    #             # amount = amount_to_depr / (undone_dotation_number - len(posted_deferral_line_ids))
    #             amount = amount_to_depr / self.method_number
    #             days = total_days - float(deferral_date.strftime('%d')) + 1
    #             if i == 1:
    #                 amount = (amount_to_depr / self.method_number) / total_days * days
    #             elif i == undone_dotation_number:
    #                 amount = (amount_to_depr / self.method_number) / total_days * (total_days - days)
    #         elif self.method == 'degressive':
    #             amount = residual_amount * self.method_progress_factor
    #             days = total_days - float(deferral_date.strftime('%j'))
    #             if i == 1:
    #                 amount = (residual_amount * self.method_progress_factor) / total_days * days
    #             elif i == undone_dotation_number:
    #                 amount = (residual_amount * self.method_progress_factor) / total_days * (total_days - days)
    #     return amount

    def _get_deferral_board(self):
        self.ensure_one()
        if self.deferral_line_ids.move_id.filtered(lambda r:r.state != 'cancel'):
            return
        self.deferral_line_ids.unlink()
        if self.value_residual == 0.0:
            return

        residual_amount = self.value_residual
        deferral_date = self._get_last_deferral_date()[self.id]
        undone_dotation_number = self._get_board_undone_dotation_nb(deferral_date)
        amount = self.value_residual / undone_dotation_number
        line_data = []
        for x in range(0, undone_dotation_number):
            i = x + 1
            if i == undone_dotation_number:
                amount = residual_amount
            residual_amount -= amount
            vals = {
                 'amount': amount,
                 'sequence': i,
                 'name': str(self.id) + '/' + str(i),
                 'remaining_value': residual_amount,
                 'distributed_value': self.value_residual - residual_amount - amount,
                 'deferral_date': deferral_date
            }
            line_data.append((0,0,vals))
            deferral_date = fields.Date.add(deferral_date, months=self.method_period)
        self.deferral_line_ids = line_data

    def compute_deferral_board(self):
        for r in self:
            r._get_deferral_board()
