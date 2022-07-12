import datetime
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestMPSMethod(Common):

    def test_01_compute_date_planned_mps_method(self):
        """1. Test compute _compute_date_planned_mps
        Input:
            - PO:
                - Order Date ngày 15/10/2021
                - Order line chứa sản phẩm A, ngày nhận hàng 14/10/2021
        Output:
            - Ngày kế hoạch là 14/10/2021
        """
        po = self.env['purchase.order'].create({
            'date_order': fields.Datetime.to_datetime('2021-10-15 09:00:00'),
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_wood_panel.name,
                    'product_id': self.product_wood_panel.id,
                    'product_uom': self.product_wood_panel.uom_id.id,
                    'product_qty': 1.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Datetime.to_datetime('2021-10-14 09:00:00'),
                }),
            ],
        })

        self.assertEqual(po.date_planned_mps, fields.Datetime.to_datetime('2021-10-14 09:00:00'))

        """1.1 Test compute _compute_date_planned_mps
        Input:
            - PO:
                - Order Date ngày 15/10/2021
                - Order line chứa sản phẩm A, không thiết lập ngày nhận hàng
        Output:
            - Ngày kế hoạch là 15/10/2021
        """
        po.order_line.date_planned = False
        self.assertEqual(po.date_planned_mps, fields.Datetime.to_datetime('2021-10-15 09:00:00'))

    @patch('odoo.addons.to_mrp_mps.models.res_company.fields')
    def test_02_get_mps_date_range_method(self, mock_obj):
        """2. Test hàm _get_mps_date_range
        Input:
            - Ngày hiện tại là 15/10/2021
            - Chu kỳ sản xuất: hàng ngày
            - Số cột chu kỳ để hiện thị: 5
        Output:
            - [
                (datetime.date(2021, 10, 15), datetime.date(2021, 10, 15)),
                (datetime.date(2021, 10, 16), datetime.date(2021, 10, 16)),
                (datetime.date(2021, 10, 17), datetime.date(2021, 10, 17)),
                (datetime.date(2021, 10, 18), datetime.date(2021, 10, 18)),
                (datetime.date(2021, 10, 19), datetime.date(2021, 10, 19))
                ]
        """
        mock_obj.Date.today.return_value = fields.Date.to_date('2021-10-15')

        self.env.company.write({
            'manufacturing_period': 'day',
            'manufacturing_period_to_display': 5,
            })

        expected_values = [
            (datetime.date(2021, 10, 15), datetime.date(2021, 10, 15)),
            (datetime.date(2021, 10, 16), datetime.date(2021, 10, 16)),
            (datetime.date(2021, 10, 17), datetime.date(2021, 10, 17)),
            (datetime.date(2021, 10, 18), datetime.date(2021, 10, 18)),
            (datetime.date(2021, 10, 19), datetime.date(2021, 10, 19))
            ]
        self.assertEqual(self.env.company._get_mps_date_range(), expected_values)

        """2.1 Test hàm _get_mps_date_range
        Input:
            - Ngày hiện tại là 15/10/2021
            - Chu kỳ sản xuất: hàng tuần
            - Số cột chu kỳ để hiện thị: 5
        (sử dụng tiêu chuẩn ISO8601 để thứ 2 là ngày đầu tuần, chủ nhận là ngày cuối tuần)
        Output:
            - [
                (datetime.date(2021, 10, 11), datetime.date(2021, 10, 17)),
                (datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)),
                (datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)),
                (datetime.date(2021, 11, 1), datetime.date(2021, 11, 7)),
                (datetime.date(2021, 11, 8), datetime.date(2021, 11, 14))
                ]
        """
        self.env.company.write({
            'manufacturing_period': 'week',
            })

        expected_values = [
            (datetime.date(2021, 10, 11), datetime.date(2021, 10, 17)),
            (datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)),
            (datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)),
            (datetime.date(2021, 11, 1), datetime.date(2021, 11, 7)),
            (datetime.date(2021, 11, 8), datetime.date(2021, 11, 14))
            ]
        self.assertEqual(self.env.company._get_mps_date_range(), expected_values)

        """2.2 Test hàm _get_mps_date_range
        Input:
            - Ngày hiện tại là 15/10/2021
            - Chu kỳ sản xuất: hàng tháng
            - Số cột chu kỳ để hiện thị: 5
        (sử dụng tiêu chuẩn ISO8601 để thứ 2 là ngày đầu tuần, chủ nhận là ngày cuối tuần)
        Output:
            - [
                (datetime.date(2021, 10, 1), datetime.date(2021, 10, 31)),
                (datetime.date(2021, 11, 1), datetime.date(2021, 11, 30)),
                (datetime.date(2021, 12, 1), datetime.date(2021, 12, 31)),
                (datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)),
                (datetime.date(2022, 2, 1), datetime.date(2022, 2, 28))
                ]
        """
        self.env.company.write({
            'manufacturing_period': 'month',
            })

        expected_values = [
            (datetime.date(2021, 10, 1), datetime.date(2021, 10, 31)),
            (datetime.date(2021, 11, 1), datetime.date(2021, 11, 30)),
            (datetime.date(2021, 12, 1), datetime.date(2021, 12, 31)),
            (datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)),
            (datetime.date(2022, 2, 1), datetime.date(2022, 2, 28))
            ]
        self.assertEqual(self.env.company._get_mps_date_range(), expected_values)
