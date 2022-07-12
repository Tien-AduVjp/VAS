from unittest.mock import patch
from odoo.tests import Form
from odoo import fields
from .common import Common


class TestAccountMove(Common):
    
    @classmethod
    def setUpClass(cls):
        super(TestAccountMove, cls).setUpClass()
        AnalyticTag = cls.env['account.analytic.tag']
        cls.analytic_tag_revenue = AnalyticTag.create({'name': 'Revenue Tag'})
        cls.analytic_tag_cost = AnalyticTag.create({'name': 'Cost Tag'})
        
        AnalyticAccount = cls.env['account.analytic.account']
        cls.analytic_account_revenue = AnalyticAccount.create({'name': 'Revenue Analytic'})
        cls.analytic_account_cost = AnalyticAccount.create({'name': 'Cost Analytic'})
        
        cls.partner = cls.env.ref('base.partner_admin')

    def test_aml_onchange_product_revenue_01(self):
        f = Form(self.env['account.move'].with_context(default_type='out_invoice'), view='account.view_move_form')
        with f.invoice_line_ids.new() as line:
            line.product_id = self.product_A
        invoice = f.save()
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.account_id, self.revenue_deferral_category.deferred_account_id)
        self.assertFalse(move_line.analytic_tag_ids)
        self.assertFalse(move_line.analytic_account_id)
 
    def test_aml_onchange_product_revenue_02(self):
        self.revenue_deferral_category.write({
            'account_analytic_id': self.analytic_account_revenue.id,
            'analytic_tag_ids': [(6,0,self.analytic_tag_revenue.ids)]
        })
        f = Form(self.env['account.move'].with_context(default_type='out_invoice'), view='account.view_move_form')
        with f.invoice_line_ids.new() as line:
            line.product_id = self.product_A
        invoice = f.save()
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.account_id, self.revenue_deferral_category.deferred_account_id)
        self.assertEqual(move_line.analytic_tag_ids, self.revenue_deferral_category.analytic_tag_ids)
        self.assertEqual(move_line.analytic_account_id, self.revenue_deferral_category.account_analytic_id)

    def test_aml_onchange_product_cost_01(self):
        f = Form(self.env['account.move'].with_context(default_type='in_invoice'), view='account.view_move_form')
        with f.invoice_line_ids.new() as line:
            line.product_id = self.product_A
        invoice = f.save()
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.account_id, self.cost_deferral_category.deferred_account_id)
        self.assertFalse(move_line.analytic_tag_ids)
        self.assertFalse(move_line.analytic_account_id)

    def test_aml_onchange_product_cost_02(self):
        self.cost_deferral_category.write({
            'account_analytic_id': self.analytic_account_cost.id,
            'analytic_tag_ids': [(6,0,self.analytic_tag_cost.ids)]
        })
        f = Form(self.env['account.move'].with_context(default_type='in_invoice'), view='account.view_move_form')
        with f.invoice_line_ids.new() as line:
            line.product_id = self.product_A
        invoice = f.save()
        move_line = invoice.invoice_line_ids[0]
        self.assertEqual(move_line.account_id, self.cost_deferral_category.deferred_account_id)
        self.assertEqual(move_line.analytic_tag_ids, self.cost_deferral_category.analytic_tag_ids)
        self.assertEqual(move_line.analytic_account_id, self.cost_deferral_category.account_analytic_id)

    def test_account_move_revenue_01(self):
        """
        Tạo bút toán từ dòng phân bổ doanh thu
        Không thiết lập đối tác trên phân bổ
        Không thiết lập kế toán quản trị trên nhóm phân bổ doanh thu
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids.create_move(post_move=False)
        moves = self.revenue_deferral.deferral_line_ids.move_id
    
        self.assertRecordValues(
            moves, 
            [{
                'ref': 'RD',
                'date': fields.Date.to_date('2022-01-01'),
                'journal_id': self.journal_revenue_deferral.id,
                'state': 'draft'
            },
            {
                'ref': 'RD',
                'date': fields.Date.to_date('2022-02-01'),
                'journal_id': self.journal_revenue_deferral.id,
                'state': 'draft'
            }])
        self.assertRecordValues(
            moves[0].line_ids, 
            [{
                'name': 'RD (1/2)',
                'ref': 'RD',
                'account_id': self.account_unrealized_revenue.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-01-01')
            },
            {
                'name': 'RD (1/2)',
                'ref': 'RD',
                'account_id': self.account_revenue.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-01-01')
            }])
    
        self.assertRecordValues(
            moves[1].line_ids, 
            [{
                'name': 'RD (2/2)',
                'ref': 'RD',
                'account_id': self.account_unrealized_revenue.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-02-01')
            },
            {
                'name': 'RD (2/2)',
                'ref': 'RD',
                'account_id': self.account_revenue.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-02-01')
            }])

    def test_account_move_revenue_02(self):
        """
        Tạo bút toán từ dòng phân bổ doanh thu
        Thiết lập đối tác trên phân bổ
        Thiết lập kế toán quản trị trên nhóm phân bổ doanh thu
        """
        self.revenue_deferral_category.write({
            'account_analytic_id': self.analytic_account_revenue.id,
            'analytic_tag_ids': [(6,0,self.analytic_tag_revenue.ids)]
        })
        self.revenue_deferral.partner_id = self.partner
    
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids.create_move(post_move=False)
        moves = self.revenue_deferral.deferral_line_ids.move_id
    
        self.assertRecordValues(
            moves, 
            [{
                'ref': 'RD',
                'date': fields.Date.to_date('2022-01-01'),
                'journal_id': self.journal_revenue_deferral.id,
                'state': 'draft'
            },
            {
                'ref': 'RD',
                'date': fields.Date.to_date('2022-02-01'),
                'journal_id': self.journal_revenue_deferral.id,
                'state': 'draft'
            }])
        self.assertRecordValues(
            moves[0].line_ids, 
            [{
                'name': 'RD (1/2)',
                'ref': 'RD',
                'account_id': self.account_unrealized_revenue.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-01-01')
            },
            {
                'name': 'RD (1/2)',
                'ref': 'RD',
                'account_id': self.account_revenue.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.analytic_account_revenue.id,
                'analytic_tag_ids': self.analytic_tag_revenue.ids,
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-01-01')
            }])
    
        self.assertRecordValues(
            moves[1].line_ids, 
            [{
                'name': 'RD (2/2)',
                'ref': 'RD',
                'account_id': self.account_unrealized_revenue.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-02-01')
            },
            {
                'name': 'RD (2/2)',
                'ref': 'RD',
                'account_id': self.account_revenue.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.analytic_account_revenue.id,
                'analytic_tag_ids': self.analytic_tag_revenue.ids,
                'journal_id': self.journal_revenue_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-02-01')
            }])
    
    def test_account_move_cost_01(self):
        """
        Tạo bút toán từ dòng phân bổ chi phí
        Không thiết lập đối tác trên phân bổ
        Không thiết lập kế toán quản trị trên nhóm phân bổ chi phí
        """
        self.cost_deferral.validate()
        self.cost_deferral.deferral_line_ids.create_move(post_move=False)
        moves = self.cost_deferral.deferral_line_ids.move_id
    
        self.assertRecordValues(
            moves, 
            [{
                'ref': 'CD',
                'date': fields.Date.to_date('2022-01-01'),
                'journal_id': self.journal_cost_deferral.id,
                'state': 'draft'
            },
            {
                'ref': 'CD',
                'date': fields.Date.to_date('2022-02-01'),
                'journal_id': self.journal_cost_deferral.id,
                'state': 'draft'
            }])
        self.assertRecordValues(
            moves[0].line_ids, 
            [{
                'name': 'CD (1/2)',
                'ref': 'CD',
                'account_id': self.account_long_term_cost.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-01-01')
            },
            {
                'name': 'CD (1/2)',
                'ref': 'CD',
                'account_id': self.account_expense.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-01-01')
            }])
    
        self.assertRecordValues(
            moves[1].line_ids, 
            [{
                'name': 'CD (2/2)',
                'ref': 'CD',
                'account_id': self.account_long_term_cost.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-02-01')
            },
            {
                'name': 'CD (2/2)',
                'ref': 'CD',
                'account_id': self.account_expense.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.env['res.partner'],
                'date': fields.Date.to_date('2022-02-01')
            }])

    def test_account_move_cost_02(self):
        """
        Tạo bút toán từ dòng phân bổ chi phí
        Thiết lập đối tác trên phân bổ
        Thiết lập kế toán quản trị trên nhóm phân bổ chi phí
        """
        self.cost_deferral_category.write({
            'account_analytic_id': self.analytic_account_cost.id,
            'analytic_tag_ids': [(6,0,self.analytic_tag_cost.ids)]
        })
        self.cost_deferral.partner_id = self.partner
    
        self.cost_deferral.validate()
        self.cost_deferral.deferral_line_ids.create_move(post_move=False)
        moves = self.cost_deferral.deferral_line_ids.move_id
    
        self.assertRecordValues(
            moves, 
            [{
                'ref': 'CD',
                'date': fields.Date.to_date('2022-01-01'),
                'journal_id': self.journal_cost_deferral.id,
                'state': 'draft'
            },
            {
                'ref': 'CD',
                'date': fields.Date.to_date('2022-02-01'),
                'journal_id': self.journal_cost_deferral.id,
                'state': 'draft'
            }])
        self.assertRecordValues(
            moves[0].line_ids, 
            [{
                'name': 'CD (1/2)',
                'ref': 'CD',
                'account_id': self.account_long_term_cost.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-01-01')
            },
            {
                'name': 'CD (1/2)',
                'ref': 'CD',
                'account_id': self.account_expense.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.analytic_account_cost.id,
                'analytic_tag_ids': self.analytic_tag_cost.ids,
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-01-01')
            }])
    
        self.assertRecordValues(
            moves[1].line_ids, 
            [{
                'name': 'CD (2/2)',
                'ref': 'CD',
                'account_id': self.account_long_term_cost.id,
                'debit': 0.0,
                'credit': 10000.0,
                'analytic_account_id': self.env['account.analytic.account'],
                'analytic_tag_ids': self.env['account.analytic.tag'],
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-02-01')
            },
            {
                'name': 'CD (2/2)',
                'ref': 'CD',
                'account_id': self.account_expense.id,
                'debit': 10000.0,
                'credit': 0.0,
                'analytic_account_id': self.analytic_account_cost.id,
                'analytic_tag_ids': self.analytic_tag_cost.ids,
                'journal_id': self.journal_cost_deferral.id,
                'partner_id': self.partner.id,
                'date': fields.Date.to_date('2022-02-01')
            }])
    
    @patch.object(fields.Date, 'today', lambda : fields.Date.to_date('2022-01-15'))
    def test_cron_auto_create_move_deferral_01(self):
        self.revenue_deferral.validate()
        self.cost_deferral.validate()
        self.env.ref('to_cost_revenue_deferred.ir_cron_create_move_deferral').method_direct_trigger()
        
        self.assertFalse(self.revenue_deferral.deferral_line_ids.move_id)
        self.assertFalse(self.cost_deferral.deferral_line_ids.move_id)
    
    @patch.object(fields.Date, 'today', lambda : fields.Date.to_date('2022-01-15'))
    def test_cron_auto_create_move_deferral_02(self):
        self.revenue_deferral.auto_create_move = True
        self.cost_deferral.auto_create_move = True
        self.revenue_deferral.validate()
        self.cost_deferral.validate()
        self.env.ref('to_cost_revenue_deferred.ir_cron_create_move_deferral').method_direct_trigger()
        
        self.assertTrue(self.revenue_deferral.deferral_line_ids[0].move_id)
        self.assertFalse(self.revenue_deferral.deferral_line_ids[1].move_id)
        self.assertTrue(self.cost_deferral.deferral_line_ids[0].move_id)
        self.assertFalse(self.cost_deferral.deferral_line_ids[1].move_id)
