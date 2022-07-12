from odoo import models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_account_by_code_prefix(self, code_prefix, limit=None):
        domain = [('code', '=ilike', code_prefix + '%'), ('company_id', '=', self.id)]
        if not limit:
            return self.env['account.account'].search(domain)
        else:
            return self.env['account.account'].search(domain, limit=1)

    def _prepare_balance_carry_forward_preceding_rules_data(self):
        return [
            # revennue to 911
            {
                'name': _('51x->911: Revenue Balance to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('51').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'sequence': 5,
                'company_id': self.id,
                # 521 -> 511
                'preceding_rule_ids': [(0, 0, {
                    'name': _('521->511: Revenue Deductions Balance to 511'),
                    'forward_type': 'auto',
                    'source_account_ids': [(6, 0, self._get_account_by_code_prefix('521').ids)],
                    'dest_account_id': self._get_account_by_code_prefix('511', 1).id,
                    'profit_loss': False,
                    'sequence': 0,
                    'company_id': self.id,
                    })]
                },
            {
                'name': _('711->911: Other Revenue Balance to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('711').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 10
                },

            # expenses
            {
                'name': _('611->911: Purchases Cost to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('611').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 180
                },
            {
                'name': _('621->911: Direct raw material costs to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('621').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 185
                },
            {
                'name': _('622->911: Direct labour costs to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('622').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 187
                },
            {
                'name': _('623->911: Costs of construction machinery to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('623').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 189
                },
            {
                'name': _('627->911: Factory overheads to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('627').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 191
                },
            {
                'name': _('631->911: Production costs to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('631').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 193
                },
            {
                'name': _('632->911: Costs of goods sold to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('632').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 195
                },
            {
                'name': _('635->911: Financial expenses to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('635').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 201
                },
            {
                'name': _('641->911: Selling expenses to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('641').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 250
                },
            {
                'name': _('642->911: General administration expenses to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('642').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 252
                },
            {
                'name': _('811->911: Other Cost to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('811').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 400
                },
            {
                'name': _('821->911: Income tax expense to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('821').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 450
                },

            ]

    def _prepare_balance_carry_forward_rules_data(self):
        self.ensure_one()
        preceding_rules_data = []
        for vals in self._prepare_balance_carry_forward_preceding_rules_data():
            preceding_rules_data.append((0, 0, vals))
        return {
            'name': _('911->4212'),
            'forward_type': 'auto',
            'source_account_ids': [(6, 0, self._get_account_by_code_prefix('911').ids)],
            'dest_account_id': self._get_account_by_code_prefix('4212', 1).id,
            'profit_loss': True,
            'company_id': self.id,
            'sequence': 1000,
            'preceding_rule_ids': preceding_rules_data
            }

    def generate_vietnam_balance_carry_forward_rules(self):
        vals_list = []

        vn_chart_id = self.env.ref('l10n_vn.vn_template')
        for r in self.filtered(lambda c: c.chart_template_id == vn_chart_id):
            vals = r._prepare_balance_carry_forward_rules_data()

            is_existing = False
            for rule in self.env['balance.carry.forward.rule'].sudo().search([('company_id', '=', r.id)]):
                if vals['source_account_ids'][0][2] == rule.source_account_ids.ids:
                    is_existing = True
                    break
            if not is_existing:
                vals_list.append(vals)

        if vals_list:
            # use sudo to pass the multi-company rule during new company creation
            # when the user has not been assigned with new company access right yet
            self.env['balance.carry.forward.rule'].sudo().create(vals_list)
