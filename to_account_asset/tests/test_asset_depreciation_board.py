import calendar
from datetime import date

from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install')
class TestAssetDepeciationBoard(asset_common.AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.currency_vnd = cls.env.ref('base.VND')
        if not cls.currency_vnd.active:
            cls.currency_vnd.active = True

    def test_01_depreciation_board_using_linear_method(self):
        """Test depreciation board using linear method
        """
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd)

        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(8333333, line.amount)

        self.assertEqual(8333337, asset.depreciation_line_ids[-1].amount)

        # Case: using prorata
        asset.prorata = True
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        self.assertEqual(5913978, asset.depreciation_line_ids[0].amount)

        for line in asset.depreciation_line_ids[1:-1]:
            self.assertEqual(8333333, line.amount)

        self.assertEqual(2419359, asset.depreciation_line_ids[-1].amount)

        # Case: using Ending Date, no use prorata
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 8, 18),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[0:-1]:
            self.assertEqual(7692308, line.amount)

        self.assertEqual(7692304, asset.depreciation_line_ids[-1].amount)

        # Case: set Ending Date as 17/9/2021, no use prorata
        # period 18/8/2021~17/9/2021 will get the same result as above
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 9, 17),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[0:-1]:
            self.assertEqual(7692308, line.amount)

        self.assertEqual(7692304, asset.depreciation_line_ids[-1].amount)

        # Case: set Ending Date as 18/9/2021, no use prorata
        # period ~ 18/9/2021 will add 1 depreciation line
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 9, 18),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(14, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[0:-1]:
            self.assertEqual(7142857, line.amount)

        self.assertEqual(7142859, asset.depreciation_line_ids[-1].amount)

        # Case: set Ending Date as 15/08/2021, no use prorata
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 8, 15),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[0:-1]:
            self.assertEqual(8333333, line.amount)

        self.assertEqual(8333337, asset.depreciation_line_ids[-1].amount)

    def test_02_depreciation_board_using_degressive_method(self):
        """Test depreciation board using degressive method
        """
        # Case: no use prorata
        asset = self._create_asset(method='degressive', method_progress_factor=0.3, currency=self.currency_vnd)
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        last_amount = asset.currency_id.round(asset.value * asset.method_progress_factor)
        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(last_amount, line.amount)
            last_amount = asset.currency_id.round(line.remaining_value * asset.method_progress_factor)

        self.assertEqual(asset.depreciation_line_ids[-2].remaining_value, asset.depreciation_line_ids[-1].amount)

        # Case: using prorata
        asset.prorata = True
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        self.assertEqual(asset.currency_id.round(100000000 * 0.3 / 31 * 22), asset.depreciation_line_ids[0].amount)

        last_amount = asset.currency_id.round(asset.depreciation_line_ids[0].remaining_value * asset.method_progress_factor)
        for line in asset.depreciation_line_ids[1:-1]:
            self.assertEqual(last_amount, line.amount)
            last_amount = asset.currency_id.round(line.remaining_value * asset.method_progress_factor)

        self.assertEqual(asset.depreciation_line_ids[-2].remaining_value, asset.depreciation_line_ids[-1].amount)

        # Case: no use prorata with end_date as 18/08/2021, no use prorata
        # period ~ 18/08/2021 will add 1 depreciation line
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 8, 18),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        last_amount = asset.currency_id.round(asset.value * asset.method_progress_factor)
        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(last_amount, line.amount)
            last_amount = asset.currency_id.round(line.remaining_value * asset.method_progress_factor)

        self.assertEqual(asset.depreciation_line_ids[-2].remaining_value, asset.depreciation_line_ids[-1].amount)

        # Case: no use prorata with end_date as 17/08/2021, no use prorata
        asset.write({'prorata': False,
                     'method_time': 'end',
                     'method_end': date(2021, 8, 17),
                     })
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        last_amount = asset.currency_id.round(asset.value * asset.method_progress_factor)
        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(last_amount, line.amount)
            last_amount = asset.currency_id.round(line.remaining_value * asset.method_progress_factor)

        self.assertEqual(asset.depreciation_line_ids[-2].remaining_value, asset.depreciation_line_ids[-1].amount)

    def test_03_depreciation_board_using_degressive_then_linear_method(self):
        """Test depreciation board using degressive then linear method
        """
        # Case: no use prorata
        asset_linear_method = self._create_asset(currency=self.currency_vnd)
        asset_degressive_method = self._create_asset(method='degressive', method_progress_factor=0.3, currency=self.currency_vnd)
        asset_degressive_then_linear_method = self._create_asset(method='degressive_then_linear', method_progress_factor=0.3, currency=self.currency_vnd)

        asset_linear_method.action_compute_depreciation_board()
        asset_degressive_method.action_compute_depreciation_board()
        asset_degressive_then_linear_method.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset_degressive_then_linear_method.depreciation_line_ids.mapped('amount')))

        for l, d, dl in zip(asset_linear_method.depreciation_line_ids,
                            asset_degressive_method.depreciation_line_ids,
                            asset_degressive_then_linear_method.depreciation_line_ids):
            if d.amount < l.amount:
                residual_amount = asset_linear_method.value - dl.depreciated_value + dl.amount
                if l.amount < residual_amount:
                    self.assertEqual(l.amount, dl.amount)
                else:
                    self.assertEqual(residual_amount, dl.amount)
            else:
                self.assertEqual(d.amount, dl.amount)

        # Case: use prorata
        (asset_degressive_method | asset_degressive_then_linear_method).write({'prorata': True})
        asset_linear_method.action_compute_depreciation_board()
        asset_degressive_method.action_compute_depreciation_board()
        asset_degressive_then_linear_method.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset_degressive_then_linear_method.depreciation_line_ids.mapped('amount')))

        for l, d, dl in zip(asset_linear_method.depreciation_line_ids,
                            asset_degressive_method.depreciation_line_ids,
                            asset_degressive_then_linear_method.depreciation_line_ids):
            if d.amount < l.amount:
                residual_amount = asset_linear_method.value - dl.depreciated_value + dl.amount
                if l.amount < residual_amount:
                    self.assertEqual(l.amount, dl.amount)
                else:
                    self.assertEqual(residual_amount, dl.amount)
            else:
                self.assertEqual(d.amount, dl.amount)

    def test_04_depreciation_board_using_linear_method_and_based_on_last_day_of_month(self):
        """Test depreciation board using linear method and Depreciation Dates as Based on Last Day of Month
        """
        # Case: no use prorata
        asset = self._create_asset(currency=self.currency_vnd, date_first_depreciation='last_day_period')

        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(12, len(asset.depreciation_line_ids))

        for line in asset.depreciation_line_ids[:-1]:
            self.assertEqual(8333333, line.amount)
            depr_date = line.depreciation_date
            self.assertEqual(calendar.monthrange(depr_date.year, depr_date.month)[1], depr_date.day)

        self.assertEqual(8333337, asset.depreciation_line_ids[-1].amount)
        self.assertEqual(date(2021, 7, 31), asset.depreciation_line_ids[-1].depreciation_date)

        # Case: using prorata
        asset.prorata = True
        asset.action_compute_depreciation_board()

        self.assertEqual(100000000, sum(asset.depreciation_line_ids.mapped('amount')))
        self.assertEqual(13, len(asset.depreciation_line_ids))

        self.assertEqual(5913978, asset.depreciation_line_ids[0].amount)

        for line in asset.depreciation_line_ids[1:-1]:
            self.assertEqual(8333333, line.amount)
            depr_date = line.depreciation_date
            self.assertEqual(calendar.monthrange(depr_date.year, depr_date.month)[1], depr_date.day)

        self.assertEqual(2419359, asset.depreciation_line_ids[-1].amount)
        self.assertEqual(date(2021, 8, 9), asset.depreciation_line_ids[-1].depreciation_date)
