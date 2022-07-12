from odoo.tests.common import tagged, SingleTransactionCase


@tagged('post_install', '-at_install')
class TestRegenerateAnalyticLines(SingleTransactionCase):
    
    @classmethod
    def setUpClass(cls): 
        super(TestRegenerateAnalyticLines, cls).setUpClass()
        
        # Create accounts
        user_type_liquidity = cls.env.ref('account.data_account_type_liquidity')
        account_1 = cls.env['account.account'].create({
            'code': 'NC1115',
            'name': 'Liquidity Account1',
            'user_type_id': user_type_liquidity.id,
        })
        account_2 = cls.env['account.account'].create({
            'code': 'NC1116',
            'name': 'Liquidity Account2',
            'user_type_id': user_type_liquidity.id,
        })
        
        cls.analytic_account = cls.env.ref('analytic.analytic_absences')
        cls.analytic_account_2 = cls.env.ref('analytic.analytic_internal')
        cls.analytic_tag = cls.env.ref('analytic.tag_contract')
        
        
        cls.move = cls.env['account.move'].with_context(tracking_disable=True).create({
            'type': 'entry',
            'line_ids': [(0, 0, {'account_id': account_1.id, 'debit': 500.0, 'credit': 0.0}),
                         (0, 0, {'account_id': account_2.id, 'debit': 0.0, 'credit': 500.0})]
        })
        
    @staticmethod
    def _prepare_form_data(analytic_account, analytic_tags, move_lines):
        return {
            'analytic_account_id': analytic_account.id,
            'analytic_tag_ids': [(6, 0, analytic_tags.ids)],
            'account_move_line_ids': [(6, 0, move_lines.ids)],
            'forced_regenerate': True,
        }
        
    def test_01_regenerate_draft_move(self):
        Wizard = self.env['account.analytic.lines.regenerate']
        wizard1 = Wizard.create(self._prepare_form_data(self.analytic_account, self.analytic_tag, self.move.line_ids))
        wizard1.regeneate_analytic_lines()
        self.assertFalse(self.move.line_ids.mapped('analytic_line_ids'))
        
    def test_02_regenerate_posted_move_single_line(self):
        self.move.post()
        Wizard = self.env['account.analytic.lines.regenerate']
        wizard1 = Wizard.create(self._prepare_form_data(self.analytic_account, self.analytic_tag, self.move.line_ids[0]))
        wizard1.regeneate_analytic_lines()
        self.assertRecordValues(self.move.line_ids[0].analytic_line_ids, [
            {'account_id': self.analytic_account.id, 'tag_ids': self.analytic_tag.ids, 'amount': -500.0},
        ])
    
    def test_03_regenerate_posted_move_multi_line(self):
        Wizard = self.env['account.analytic.lines.regenerate']
        wizard1 = Wizard.create(self._prepare_form_data(self.analytic_account_2, self.analytic_tag, self.move.line_ids))
        wizard1.regeneate_analytic_lines()
        self.assertRecordValues(self.move.line_ids.analytic_line_ids, [
            {'account_id': self.analytic_account_2.id, 'tag_ids': self.analytic_tag.ids, 'amount': -500.0},
            {'account_id': self.analytic_account_2.id, 'tag_ids': [], 'amount': 500.0},
        ])
