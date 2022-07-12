from odoo import models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_account_by_code_prefix(self, code_prefix, limit=None):
        domain = [('code', '=ilike', code_prefix + '%'), ('company_id', '=', self.id)]
        if not limit:
            return self.env['account.account'].search(domain)
        else:
            return self.env['account.account'].search(domain, limit=1)

    def _prepare_balance_carry_forward_c200_preceding_rules_data(self):
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
                    'dest_account_id': self._get_account_by_code_prefix('5111', 1).id,
                    'profit_loss': False,
                    'sequence': 2,
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
                'name': _('632->911: Costs of goods sold to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('632').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 195,
                # 631 -> 632
                'preceding_rule_ids': [(0, 0, {
                    'name': _('631->632: Production costs to Costs of goods sold'),
                    'forward_type': 'auto',
                    'source_account_ids': [(6, 0, self._get_account_by_code_prefix('631').ids)],
                    'dest_account_id': self._get_account_by_code_prefix('632', 1).id,
                    'profit_loss': False,
                    'sequence': 4,
                    'company_id': self.id,
                })]
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

    def _prepare_balance_carry_forward_c133_preceding_rules_data(self):
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
                'name': _('632->911: Costs of goods sold to PL'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('632').ids)],
                'dest_account_id': self._get_account_by_code_prefix('911', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 195,
                # 631 -> 632
                'preceding_rule_ids': [(0, 0, {
                    'name': _('631->632: Production costs to Costs of goods sold'),
                    'forward_type': 'auto',
                    'source_account_ids': [(6, 0, self._get_account_by_code_prefix('631').ids)],
                    'dest_account_id': self._get_account_by_code_prefix('632', 1).id,
                    'profit_loss': False,
                    'sequence': 3,
                    'company_id': self.id,
                })]
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

    def _prepare_balance_carry_forward_preceding_rules_data(self):
        self.ensure_one()
        if self.chart_template_id == self.env.ref('l10n_vn.vn_template'):
            return self._prepare_balance_carry_forward_c200_preceding_rules_data()
        elif self.chart_template_id == self.env.ref('l10n_vn_c133.vn_template_c133'):
            return self._prepare_balance_carry_forward_c133_preceding_rules_data()
        else:
            return False


    def _prepare_balance_carry_forward_rules_data(self):
        self.ensure_one()
        preceding_rules_data = []
        for vals in self._prepare_balance_carry_forward_preceding_rules_data():
            preceding_rules_data.append((0, 0, vals))

        vals_list = []
        for rule in [
            # vat tax
            {
                'name': _('33311->1331: Vat tax'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('33311').ids)],
                'dest_account_id': self._get_account_by_code_prefix('1331', 1).id,
                'profit_loss': False,
                'company_id': self.id,
                'sequence': 2000
            },
            {
                'name': _('911->4212'),
                'forward_type': 'auto',
                'source_account_ids': [(6, 0, self._get_account_by_code_prefix('911').ids)],
                'dest_account_id': self._get_account_by_code_prefix('4212', 1).id,
                'profit_loss': True,
                'company_id': self.id,
                'sequence': 1000,
                'preceding_rule_ids': preceding_rules_data
            },
            ]:
            is_existing = False
            for r in self.env['balance.carry.forward.rule'].sudo().search([('company_id', '=', self.id)]):
                if rule['source_account_ids'][0][2] == r.source_account_ids.ids:
                    is_existing = True
                    break
            if not is_existing:
                vals_list.append(rule)
        return vals_list

    def generate_vietnam_balance_carry_forward_rules(self):
        vals_list = []

        vn_chart_ids = [self.env.ref('l10n_vn.vn_template'), self.env.ref('l10n_vn_c133.vn_template_c133')]
        for r in self.filtered(lambda c: c.chart_template_id in vn_chart_ids):
            vals_list.extend(r._prepare_balance_carry_forward_rules_data())

        if vals_list:
            # use sudo to pass the multi-company rule during new company creation
            # when the user has not been assigned with new company access right yet
            self.env['balance.carry.forward.rule'].sudo().create(vals_list)
