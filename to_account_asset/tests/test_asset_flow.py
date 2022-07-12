from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install')
class TestAssetFlow(asset_common.AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.currency_vnd = cls.env.ref('base.VND')
        if not cls.currency_vnd.active:
            cls.currency_vnd.active = True

    def test_01_asset_depreciation_complete(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(8333333, line.amount)

        self.assertEqual(8333337, asset.depreciation_line_ids[-1].amount)

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create and post all depreciation entries
        asset.depreciation_line_ids.create_move()
        # Check that all depreciation entries are in "posted" state
        for state in asset.depreciation_line_ids.move_id.mapped('state'):
            self.assertEqual('posted', state)

        # Check that asset is in "Close" state
        self.assertEqual(asset.state, 'close')

        # Check disposed entry
        self.assertEqual(1, len(asset.move_ids))
        self.assertEqual('draft', asset.move_ids.state)
        self.assertEqual(asset.value, asset.move_ids.amount_total)

    def test_02_asset_sale(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)

        # Case: sell at 25/11/2020
        # no post entry with depreciation date before 25/11/2020
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2020, 11, 25))
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('draft', state)

        sell_wizard = self.env['asset.sell.wizard'].create({'asset_id': asset.id,
                                                            'stopped_depreciating_date': date(2020, 11, 25),
                                                            'sale_date': date(2020, 11, 25),
                                                            })
        sell_wizard = sell_wizard.with_context(active_ids=asset.ids)
        with self.assertRaises(UserError):
            sell_wizard.action_sell()

        # Case: sell at 20/10/2020
        # has been posted entry with depreciation date before 25/11/2020
        depreciation_lines.move_id.post()
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('posted', state)

        sell_wizard.write({'stopped_depreciating_date': date(2020, 10, 20),
                           'sale_date': date(2020, 10, 20),
                           })
        with self.assertRaises(UserError):
            sell_wizard.action_sell()

        # Case: sell at 25/11/2020
        # has been posted entry with depreciation date before 25/11/2020
        # Check that asset is in "Sold" state
        sell_wizard.write({'stopped_depreciating_date': date(2020, 11, 25),
                           'sale_date': date(2020, 11, 25),
                           })
        sell_wizard.action_sell()

        self.assertEqual(1, len(asset.move_ids))
        self.assertEqual(100000000, asset.move_ids.amount_total)
        self.assertEqual('sold', asset.state)
        self.assertEqual(-6388889, asset.depreciation_line_ids[-1].amount)

    def test_04_asset_dispose(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)

        # Case: dispose at 18/03/2021
        # no post entry with depreciation date before 18/04/2021
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2021, 4, 21))
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('draft', state)

        dispose_wizard = self.env['asset.dispose.wizard'].create({'asset_id': asset.id,
                                                                  'disposed_date': date(2021, 3, 18),
                                                                  })
        dispose_wizard = dispose_wizard.with_context(active_ids=asset.ids)
        with self.assertRaises(UserError):
            dispose_wizard.action_dispose()

        # Case: dispose at 15/04/2021
        # has been posted entry with depreciation date before 18/04/2021
        depreciation_lines.move_id.post()
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('posted', state)

        dispose_wizard.write({'disposed_date': date(2021, 4, 15)})
        with self.assertRaises(UserError):
            dispose_wizard.action_dispose()

        # Case: dispose at 18/04/2021
        # has been posted entry with depreciation date before 18/04/2021
        # Check that asset is in "Disposed" state
        dispose_wizard.write({'disposed_date': date(2021, 4, 25)})
        dispose_wizard.action_dispose()

        self.assertEqual(1, len(asset.move_ids))
        self.assertEqual(100000000, asset.move_ids.amount_total)
        self.assertEqual('disposed', asset.state)
        self.assertEqual(-6388889, asset.depreciation_line_ids[-1].amount)

    def test_05_asset_increase(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)

        # Case: increase at 19/01/2021
        # has been posted entry with depreciation date before 18/01/2021
        # no post revaluation entry
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2021, 1, 18))
        depreciation_lines.move_id.post()
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('posted', state)

        self._revaluation_asset(asset, 'increase', 1000000, date(2021, 1, 19))

        self.assertEqual(asset.value, 100000000)
        self.assertEqual(asset.value_residual, 50000002)
        self.assertEqual(asset.revaluation_value, 0)

        for l in asset.depreciation_line_ids[:-1]:
            self.assertEqual(l.amount, 8333333)
        self.assertEqual(asset.depreciation_line_ids[-1].amount, 8333337)

        # has been posted revaluation entry
        revaluation_move = asset.revaluation_line_ids.create_move()
        revaluation_move.post()
        self.assertEqual(asset.value, 100000000)
        self.assertEqual(asset.value_residual, 51000002)
        self.assertEqual(asset.revaluation_value, 1000000)
        self.assertEqual(sum(asset.depreciation_line_ids.mapped('amount')), 101000000)

        for l in depreciation_lines:
            self.assertEqual(l.amount, 8333333)
        for l in (asset.depreciation_line_ids - depreciation_lines)[:-1]:
            self.assertEqual(l.amount, 8500000)
        self.assertEqual(asset.depreciation_line_ids[-1].amount, 8500002)

        # reset to draft revaluation entry
        revaluation_move.button_draft()
        self.assertEqual(asset.value, 100000000)
        self.assertEqual(asset.value_residual, 50000002)
        self.assertEqual(asset.revaluation_value, 0)

        for l in depreciation_lines:
            self.assertEqual(l.amount, 8333333)
        for l in (asset.depreciation_line_ids - depreciation_lines)[:-1]:
            self.assertEqual(l.amount, 8333334)
        self.assertEqual(asset.depreciation_line_ids[-1].amount, 8333332)

    def test_06_asset_decrease(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)

        # Case: decrease at 17/01/2021
        # has been posted entry with depreciation date before 17/01/2021
        # has been posted revaluation entry
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2021, 1, 17))
        depreciation_lines.move_id.post()
        for state in depreciation_lines.move_id.mapped('state'):
            self.assertEqual('posted', state)

        self._revaluation_asset(asset, 'decrease', 10000000, date(2021, 1, 18))

        # has been posted revaluation entry
        revaluation_move = asset.revaluation_line_ids.create_move()
        revaluation_move.post()
        self.assertEqual(asset.value, 100000000)
        self.assertEqual(asset.value_residual, 48333335)
        self.assertEqual(asset.revaluation_value, -10000000)
        self.assertEqual(sum(asset.depreciation_line_ids.mapped('amount')), 90000000)

        for l in depreciation_lines:
            self.assertEqual(l.amount, 8333333)
        for l in (asset.depreciation_line_ids - depreciation_lines)[:-1]:
            self.assertEqual(l.amount, 6904762)
        self.assertEqual(asset.depreciation_line_ids[-1].amount, 6904763)

    def test_07_asset_decrease(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)
        # Case: decrease at 17/01/2021
        # has been posted entry with depreciation date before 18/01/2021
        # has been posted revaluation entry
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2021, 1, 18))
        depreciation_lines.move_id.post()
        self._revaluation_asset(asset, 'decrease', 10000000, date(2021, 1, 18))

        # has been posted revaluation entry
        revaluation_move = asset.revaluation_line_ids.create_move()
        revaluation_move.post()

        self.assertEqual(asset.value, 100000000)
        self.assertEqual(asset.value_residual, 40000002)
        self.assertEqual(asset.revaluation_value, -10000000)
        self.assertEqual(sum(asset.depreciation_line_ids.mapped('amount')), 90000000)

        for l in depreciation_lines:
            self.assertEqual(l.amount, 8333333)
        for l in (asset.depreciation_line_ids - depreciation_lines):
            self.assertEqual(l.amount, 6666667)

    def test_08_asset_modify(self):
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Check that asset is in "Running" state
        self.assertEqual(asset.state, 'open')
        # Create all depreciation entries
        asset.depreciation_line_ids.create_move(post_move=False)
        # Case: modify at 19/08/2020
        # has been posted entry with depreciation date before 18/08/2020
        depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2020, 8, 18))
        depreciation_lines.move_id.post()

        self._modify_asset(asset, 6, 2)

        self.assertEqual(len(asset.depreciation_line_ids), 6)
        self.assertEqual(sum(asset.depreciation_line_ids.mapped('amount')), 100000000)

        for l in depreciation_lines:
            self.assertEqual(l.amount, 8333333)
        for l in (asset.depreciation_line_ids - depreciation_lines)[:-1]:
            self.assertEqual(l.amount, 18333333)
        self.assertEqual(asset.depreciation_line_ids[-1].amount, 18333335)

    def _modify_asset(self, asset, method_number, method_period):
        modify_wizard = self.env['asset.modify'].create({'name': str(method_number) + '/' + str(method_period),
                                                              'method_number': method_number,
                                                              'method_period': method_period,
                                                              })
        modify_wizard = modify_wizard.with_context(active_id=asset.id)
        modify_wizard.modify()

    def _revaluation_asset(self, asset, method, value, date):
        revaluation_wizard = self.env['asset.revaluation.wizard'].create({'name': method + str(value),
                                                     'revaluation_date': date,
                                                     'method': method,
                                                     'value': value,
                                                     })
        revaluation_wizard = revaluation_wizard.with_context(active_id=asset.id)
        revaluation_wizard.button_revaluation()
