from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Company(models.Model):
    _inherit = "res.company"

    property_promotion_voucher_profit_account_id = fields.Many2one('account.account', string='Voucher Profit Account',
                                                         domain=[('deprecated', '=', False)],
                                                         help="When customers make payment using a promotion voucher of this type, the profit created"
                                                         " by the voucher credit will be encoded into this account. If None is set, the income account"
                                                         " set on the voucher product will be used.")
    property_promotion_voucher_loss_account_id = fields.Many2one('account.account', string='Voucher Loss Account',
                                                       domain=[('deprecated', '=', False)],
                                                       help="When customers make payment using a promotion voucher of this type, the loss created"
                                                       " by the voucher credit will be encoded into this account. If None is set, the expense account"
                                                       " set on the voucher product will be used.")

    property_unearn_revenue_account_id = fields.Many2one('account.account', string='Unearn Revenue Account',
                                                         domain=[('deprecated', '=', False)])

    @api.model
    def create_voucher_sequence(self):
        company_ids = self.env['res.company'].search([])
        sequences = self.env['ir.sequence'].search([])
        sequence_code_need_created = ('picking.type.voucher.issue.order', 'picking.type.voucher.move.order', 'picking.type.receipt.voucher')
        for sequence_code in sequence_code_need_created:
            company_voucher = sequences.filtered(lambda sequence: sequence.code == sequence_code).company_id
            company_todo_sequence = company_ids - company_voucher
            company_todo_sequence._create_voucher_sequence(sequence_code)

    def _create_voucher_sequence(self, sequence_code):
        if sequence_code == 'picking.type.voucher.issue.order':
            name_sequence = 'Picking Type Voucher Issue Order (%s)'
            prefix = 'PVIO'
        elif sequence_code == 'picking.type.voucher.move.order':
            name_sequence = 'Picking Type Voucher Move Order (%s)'
            prefix = 'PVMO'
        elif sequence_code == 'picking.type.receipt.voucher':
            name_sequence = 'Picking Type Receipt Voucher (%s)'
            prefix = 'PRV'

        val_list = []
        for company in self:
            val_list.append({
                'name':  name_sequence % company.name,
                'code': sequence_code,
                'company_id': company.id,
                'prefix': prefix,
                'padding': 5,
            })
        if val_list:
            self.env['ir.sequence'].create(val_list)

    def _create_per_company_sequences(self):
        super(Company, self)._create_per_company_sequences()
        sequence_code_need_created = ('picking.type.voucher.issue.order', 'picking.type.voucher.move.order', 'picking.type.receipt.voucher')
        for sequence_code in sequence_code_need_created:
            self._create_voucher_sequence(sequence_code)

    @api.model
    def create_picking_type_voucher(self):
        company_ids = self.env['res.company'].search([])
        picking_types = self.env['stock.picking.type'].search([])
        codes = ('voucher_issue_order', 'voucher_move_order')
        for code in codes:
            company_todo_picking_type = company_ids - picking_types.filtered(lambda type: type.code == code).company_id
            company_todo_picking_type._create_picking_type_voucher(code)

    def _create_picking_type_voucher(self, code):
        vals = {}
        val_list = []
        if code == 'voucher_issue_order':
            location_productions = self.env['stock.location'].search([('usage', '=', 'production')])
            sequences = self.env['ir.sequence'].search([('code','=', 'picking.type.voucher.issue.order')])
            vals.update({'name': _('Voucher Issue Order'),
                         'sequence_code': 'VIO',
                         'code': code,
                         'can_create_voucher':True,})
        elif code == 'voucher_move_order':
            sequences = self.env['ir.sequence'].search([('code','=', 'picking.type.voucher.move.order')])
            vals.update({'name': _('Voucher Move Order'),
                         'sequence_code': 'VMO',
                         'code': code,})

        for company in self:
            company_sequences = sequences.filtered(lambda sequence: sequence.company_id == company)
            company_picking_type_value ={'sequence_id': company_sequences[0].id,
                                         'warehouse_id':False,
                                         'company_id':company.id,}
            company_picking_type_value.update(vals)
            if code == 'voucher_issue_order':
                production = location_productions.filtered(lambda production: production.company_id == company)
                if not production:
                    raise ValidationError(_('Could not find production location for the company: %s.') % company.name)
                company_picking_type_value.update({'default_location_src_id': production[0].id})
            val_list.append(company_picking_type_value)
        if val_list:
            self.env['stock.picking.type'].create(val_list)

    def _create_per_company_picking_types(self):
        super(Company, self)._create_per_company_picking_types()
        codes = ('voucher_issue_order', 'voucher_move_order')
        for code in codes:
            self._create_picking_type_voucher(code)

    def _prepare_promotion_voucher_journal_data(self):
        self.ensure_one()
        return {
            'name': _('Promotion Voucher'),
            'type': 'cash',
            'code': 'PVJ',
            'show_on_dashboard': True,
            'sequence': 11,
            'voucher_payment':True,
            'company_id':self.id,
        }
