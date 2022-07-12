from unittest.mock import patch

from odoo import fields
from odoo.tests.common import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestMPSFlow(Common):

    @patch.object(fields.Date, 'today', lambda : fields.Date.to_date('2021-10-22'))
    def test_01_master_production_schedule_report(self):
        """1. Test kế họach sản xuất tổng thể
        Input 1.1 (sử dụng dữ liệu demo):

            - Ngày hiện tại là 22/10/2021
            - Chu kỳ sản xuất: hàng tuần
            - Số cột chu kỳ để hiện thị: 3

        Sản phẩm Table (MTO) chỉ sử dụng tuyến Sản xuất
        Sản phẩm Bolt có thiết lập tab mua hàng:
            - đối tác A
            - số lượng 1
            - giá: 1000

        Thành phẩm Table (MTO), có BOM chứa các thành phần sau:
            - 1 Table Top
            - 4 Table Leg
            - 4 Bolt
            - 10 Screw
        Thành phẩm Table Top, có Bom chứa các thành phần sau:
                - 2 Wood Panel
        """

        self.env.company.write({
            'manufacturing_period': 'week',
            'manufacturing_period_to_display': 3,
            })

        self.product_table_mto.write({
            'route_ids': [(6, 0, [self.env.ref('mrp.route_warehouse0_manufacture').id])],
            })
        (self.product_table_top
         | self.product_table_leg
         | self.product_bolt
         | self.product_screw
         | self.product_wood_panel
         | self.product_table_top
         ).write({
             'route_ids': [(6, 0, [self.env.ref('purchase_stock.route_warehouse0_buy').id])],
             })
        self.product_bolt.write({
            'seller_ids': [
                (0, 0, {
                    'name': self.partner_a.id,
                    'min_qty': 1,
                    'price': 1000,
                    })]})
        """
        Thực hiện thêm các sản phẩm vào kế hoạch sản xuất tổng thể như sau:
        - Sản phẩm Table (MTO)
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 100

        - Sản phẩm Table Top
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 50

        - Sản phẩm Table Leg
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 50

        - Sản phẩm Bolt
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 50

        - Sản phẩm Screw
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 50

        - Sản phẩm Wood Panel
            - Mục tiêu dự trữ an toàn: 30
            - Tối thiểu để cung ứng: 10
            - Tối đa để cung ứng: 50
        """
        # Remove old mps to avoid to indirect demand
        self.env['mrp.production.schedule'].search([]).unlink()

        table_mto_mps = self._create_mps(
            self.product_table_mto,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=100
            )
        table_top_mps = self._create_mps(
            self.product_table_top,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=50
            )
        table_leg_mps = self._create_mps(
            self.product_table_leg,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=50
            )
        bolt_mps = self._create_mps(
            self.product_bolt,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=50
            )
        screw_mps = self._create_mps(
            self.product_screw,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=50
            )
        wood_panel_mps = self._create_mps(
            self.product_wood_panel,
            target_qty=30,
            min_replenish_qty=10,
            max_replenish_qty=50
            )

        # Số lượng của tất cả các sản phẩm trên bằng 0
        all_product = (self.product_table_mto
                       | self.product_table_top
                       | self.product_table_leg
                       | self.product_bolt
                       | self.product_screw
                       | self.product_wood_panel
                       )
        inventory_adj = self.env['stock.inventory'].create({
            'name': 'Set to zero',
            'product_ids': [(6, 0, all_product.ids)],
            'prefill_counted_quantity': 'zero',
            })
        inventory_adj.action_start()
        inventory_adj.action_validate()

        # Kiểm tra dữ liệu của kế hoạch tổng thể:
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        """- Sản phẩm Table (MTO):
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 30
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 30
        - Tuần 44
            - Tồn Đầu kỳ: 30
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 40
            - Đáp ứng Khả dụng: 40
        - Tuần 45
            - Tồn Đầu kỳ: 40
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 50
            - Đáp ứng Khả dụng: 50
            """
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'replenish_qty': 30,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 30,
                    },
                {
                    'starting_inventory_qty': 30,
                    'outgoing_qty': 0,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 40,
                    'available_to_promise': 40,
                    },
                {
                    'starting_inventory_qty': 40,
                    'outgoing_qty': 0,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 50,
                    'available_to_promise': 50,
                    }
                ]
            )

        """- Sản phẩm Table Top:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 30
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 20
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: 20
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 10
            - Chờ cung ứng: 20
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 40
        - Tuần 45
            - Tồn Đầu kỳ: 30
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 10
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 40
        """
        table_top_mps_line = self._get_mps_line_by_id(mps_data, table_top_mps.id)
        self.assertListValues(
            table_top_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 30,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': 20,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': 20,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 10,
                    'replenish_qty': 20,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 40,
                    },
                {
                    'starting_inventory_qty': 30,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 10,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 40,
                    }
                ]
            )

        """- Sản phẩm Table Leg:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 120
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -70
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -70
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -60
            - Đáp ứng Khả dụng: -20
        - Tuần 45
            - Tồn Đầu kỳ: -60
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -50
            - Đáp ứng Khả dụng: -10
        """
        table_leg_mps_line = self._get_mps_line_by_id(mps_data, table_leg_mps.id)
        self.assertListValues(
            table_leg_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 120,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -70,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -70,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -60,
                    'available_to_promise': -20,
                    },
                {
                    'starting_inventory_qty': -60,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -50,
                    'available_to_promise': -10,
                    }
                ]
            )

        """- Sản phẩm Wood Panel:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -50
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -50
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -40
            - Đáp ứng Khả dụng: 0
        - Tuần 45
            - Tồn Đầu kỳ: -40
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 20
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -10
            - Đáp ứng Khả dụng: 10
        """
        wood_panel_mps_line = self._get_mps_line_by_id(mps_data, wood_panel_mps.id)
        self.assertListValues(
            wood_panel_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -50,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -50,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -40,
                    'available_to_promise': 0,
                    },
                {
                    'starting_inventory_qty': -40,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 20,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -10,
                    'available_to_promise': 10,
                    }
                ]
            )

        """- Sản phẩm Bolt:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 120
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -70
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -70
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -60
            - Đáp ứng Khả dụng: -20
        - Tuần 45
            - Tồn Đầu kỳ: -60
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -50
            - Đáp ứng Khả dụng: -10
        """
        bolt_mps_line = self._get_mps_line_by_id(mps_data, bolt_mps.id)
        self.assertListValues(
            bolt_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 120,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -70,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -70,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -60,
                    'available_to_promise': -20,
                    },
                {
                    'starting_inventory_qty': -60,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -50,
                    'available_to_promise': -10,
                    }
                ]
            )

        """- Sản phẩm Screw:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 300
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -250
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -250
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -300
            - Đáp ứng Khả dụng: -200
        - Tuần 45
            - Tồn Đầu kỳ: -300
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -350
            - Đáp ứng Khả dụng: -250
        """
        screw_mps_line = self._get_mps_line_by_id(mps_data, screw_mps.id)
        self.assertListValues(
            screw_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 300,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -250,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -250,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -300,
                    'available_to_promise': -200,
                    },
                {
                    'starting_inventory_qty': -300,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -350,
                    'available_to_promise': -250,
                    }
                ]
            )

        """Input 1.2: Thiết lập dự báo nhu cầu cho sản phẩm Tabel (MTO) là 15"""
        table_mto_mps.update_forecast_qty(0, 15)
        """
           Output 1.2:
        """
        # Kiểm tra dữ liệu của kế hoạch tổng thể:
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        """- Sản phẩm Table (MTO):
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 45
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 45
        - Tuần 44
            - Tồn Đầu kỳ: 30
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 40
            - Đáp ứng Khả dụng: 40
        - Tuần 45
            - Tồn Đầu kỳ: 40
            - Nhu cầu Thực tế: 0
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 50
            - Đáp ứng Khả dụng: 50
        """
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'replenish_qty': 45,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 45,
                    },
                {
                    'starting_inventory_qty': 30,
                    'outgoing_qty': 0,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 40,
                    'available_to_promise': 40,
                    },
                {
                    'starting_inventory_qty': 40,
                    'outgoing_qty': 0,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 50,
                    'available_to_promise': 50,
                    }
                ]
            )

        """- Sản phẩm Table Top:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 45
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 5
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: 5
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 10
            - Chờ cung ứng: 35
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 40
        - Tuần 45
            - Tồn Đầu kỳ: 30
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 10
            - Chờ cung ứng: 10
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: 30
            - Đáp ứng Khả dụng: 40
        """
        table_top_mps_line = self._get_mps_line_by_id(mps_data, table_top_mps.id)
        self.assertListValues(
            table_top_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 45,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': 5,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': 5,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 10,
                    'replenish_qty': 35,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 40,
                    },
                {
                    'starting_inventory_qty': 30,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 10,
                    'replenish_qty': 10,
                    'incoming_qty': 0,
                    'safety_stock_qty': 30,
                    'available_to_promise': 40,
                    }
                ]
            )

        """- Sản phẩm Table Leg:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 180
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -130
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -130
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -120
            - Đáp ứng Khả dụng: -80
        - Tuần 45
            - Tồn Đầu kỳ: -120
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -110
            - Đáp ứng Khả dụng: -70
        """
        table_leg_mps_line = self._get_mps_line_by_id(mps_data, table_leg_mps.id)
        self.assertListValues(
            table_leg_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 180,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -130,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -130,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -120,
                    'available_to_promise': -80,
                    },
                {
                    'starting_inventory_qty': -120,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -110,
                    'available_to_promise': -70,
                    }
                ]
            )

        """- Sản phẩm Wood Panel:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -50
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -50
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 70
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -70
            - Đáp ứng Khả dụng: 0
        - Tuần 45
            - Tồn Đầu kỳ: -70
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 20
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -40
            - Đáp ứng Khả dụng: -20
        """
        wood_panel_mps_line = self._get_mps_line_by_id(mps_data, wood_panel_mps.id)
        self.assertListValues(
            wood_panel_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -50,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -50,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 70,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -70,
                    'available_to_promise': 0,
                    },
                {
                    'starting_inventory_qty': -70,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 20,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -40,
                    'available_to_promise': -20,
                    }
                ]
            )

        """- Sản phẩm Bolt:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 180
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -130
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -130
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -120
            - Đáp ứng Khả dụng: -80
        - Tuần 45
            - Tồn Đầu kỳ: -120
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 40
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -110
            - Đáp ứng Khả dụng: -70
        """
        bolt_mps_line = self._get_mps_line_by_id(mps_data, bolt_mps.id)
        self.assertListValues(
            bolt_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 180,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -130,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -130,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -120,
                    'available_to_promise': -80,
                    },
                {
                    'starting_inventory_qty': -120,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 40,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -110,
                    'available_to_promise': -70,
                    }
                ]
            )

        """- Sản phẩm Screw:
        - Tuần 43
            - Tồn Đầu kỳ: 0
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 450
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -400
            - Đáp ứng Khả dụng: 50
        - Tuần 44
            - Tồn Đầu kỳ: -400
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -450
            - Đáp ứng Khả dụng: -350
        - Tuần 45
            - Tồn Đầu kỳ: -450
            - Nhu cầu Thực tế: 0
            - Dự báo nhu cầu gián tiếp: 100
            - Chờ cung ứng: 50
            - Tái cung ứng Thực tế: 0
            - Tồn Dự báo: -500
            - Đáp ứng Khả dụng: -400
        """
        screw_mps_line = self._get_mps_line_by_id(mps_data, screw_mps.id)
        self.assertListValues(
            screw_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 450,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -400,
                    'available_to_promise': 50,
                    },
                {
                    'starting_inventory_qty': -400,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -450,
                    'available_to_promise': -350,
                    },
                {
                    'starting_inventory_qty': -450,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 100,
                    'replenish_qty': 50,
                    'incoming_qty': 0,
                    'safety_stock_qty': -500,
                    'available_to_promise': -400,
                    }
                ]
            )

        """Input 1.3: Ấn nút cung ứng trên dòng Chờ cung ứng của sản phẩm Table (MTO)

        Output 1.3:
            - Sản phẩm Table (MTO):
                - Tuần 43
                   - Tồn Đầu kỳ: 0
                    - Nhu cầu Thực tế: 0
                    - Chờ cung ứng: 45
                    - Tái cung ứng Thực tế: 45
                    - Tồn Dự báo: 30
                    - Đáp ứng Khả dụng: 45
            - Một Lệnh sản xuất được tạo ra, với các thông tin:
                - sản phẩm Tabel (MTO)
                - số lượng để sản xuất: 45
                - Nguồn: MPS
        """
        table_mto_mps.action_replenish(based_on_lead_time=False)
        # Check
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'replenish_qty': 45,
                    'incoming_qty': 45,
                    'safety_stock_qty': 30,
                    'available_to_promise': 45,
                    },
                ]
            )

        mrp_order = self.env['mrp.production'].search([
            ('product_id', '=', table_mto_mps.product_id.id),
            ('product_qty', '=', 45),
            ('origin', '=', 'MPS')
            ])
        self.assertEqual(len(mrp_order), 1)

        """Input 1.4: Ấn nút cung ứng trên dòng Chờ cung ứng của sản phẩm Bolt

        Output 1.4:
            - Sản phẩm Bolt:
                - Tuần 43
                    - Tồn Đầu kỳ: 0
                    - Nhu cầu Thực tế: 0
                    - Dự báo nhu cầu gián tiếp: 180
                    - Chờ cung ứng: 50
                    - Tái cung ứng Thực tế: 50
                    - Tồn Dự báo: -130
                    - Đáp ứng Khả dụng: 50
            - Một Đơn mua được tạo ra, với các thông tin:
                - Đối tác A
                - sản phẩm Bold
                - số lượng: 50
                - đơn giá 1000
                - Nguồn: MPS
        """
        bolt_mps.action_replenish(based_on_lead_time=False)
        # Check
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        bolt_mps_line = self._get_mps_line_by_id(mps_data, bolt_mps.id)
        self.assertListValues(
            bolt_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'indirect_demand_qty': 180,
                    'replenish_qty': 50,
                    'incoming_qty': 50,
                    'safety_stock_qty': -130,
                    'available_to_promise': 50,
                    },
                ]
            )

        purchase_order = self.env['purchase.order'].search([
            ('partner_id', '=', self.partner_a.id),
            ('order_line.product_id', '=', bolt_mps.product_id.id),
            ('order_line.price_unit', '=', 1000),
            ('order_line.product_qty', '=', 50),
            ('origin', '=', 'MPS')
            ])
        self.assertEqual(len(purchase_order), 1)

        """
        Input 1.5: Tạo đơn bán như sau:
            - Đối tác B
            - Sản phẩm Tabel (MTO)
            - số lượng 5
            - đơn giá 1.000.000

        Output 1.5:
            - Sản phẩm Table (MTO):
                - Tuần 43
                    - Tồn Đầu kỳ: 0
                    - Nhu cầu Thực tế: 0
                    - Chờ cung ứng: 45
                    - Tái cung ứng Thực tế: 45
                    - Tồn Dự báo: 30
                    - Đáp ứng Khả dụng: 45
        """
        table_mto_sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_b.id,
            'date_order': fields.Datetime.to_datetime('2021-10-22 09:00:00'),
            'order_line': [(0, 0, {
                'name': table_mto_mps.product_id.name,
                'product_id': table_mto_mps.product_id.id,
                'product_uom_qty': 5,
                'product_uom': table_mto_mps.product_id.uom_id.id,
                'price_unit': 1000000,
                'tax_id': False,
                })]
        })
        # Check
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'replenish_qty': 45,
                    'incoming_qty': 45,
                    'safety_stock_qty': 30,
                    'available_to_promise': 45,
                    },
                ]
            )

        """
        Input 1.6: Xác nhận đơn bán trên:

        Output 1.6:
            - Sản phẩm Table (MTO):
                - Tuần 43
                    - Tồn Đầu kỳ: 0
                    - Nhu cầu Thực tế: 5
                    - Chờ cung ứng: 45
                    - Tái cung ứng Thực tế: 45
                    - Tồn Dự báo: 30
                    - Đáp ứng Khả dụng: 45
        """
        table_mto_sale_order.action_confirm()
        table_mto_sale_order.picking_ids.move_lines.date_expected = fields.Datetime.to_datetime('2021-10-22 09:00:00')
        # Check
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 5,
                    'replenish_qty': 45,
                    'incoming_qty': 45,
                    'safety_stock_qty': 30,
                    'available_to_promise': 40,
                    },
                ]
            )

        """
        Input 1.7: Hủy đơn bán trên:

        Output 1.7 = output 1.5
        """
        table_mto_sale_order.action_cancel()
        # Check
        mps_data = self.env['mrp.production.schedule'].get_mps_view_state_by_domain()
        table_mto_mps_line = self._get_mps_line_by_id(mps_data, table_mto_mps.id)
        self.assertListValues(
            table_mto_mps_line,
            [
                {
                    'starting_inventory_qty': 0,
                    'outgoing_qty': 0,
                    'replenish_qty': 45,
                    'incoming_qty': 45,
                    'safety_stock_qty': 30,
                    'available_to_promise': 45,
                    },
                ]
            )

    def _get_mps_line_by_id(self, mps_data, mps_id):
        vals = {}
        for state in mps_data['schedule_states']:
            if state['id'] == mps_id:
                vals = state
                break
        return vals

    def assertListValues(self, source_values, expected_values):
        ''' Compare a list of dictionaries with a list of dictionaries representing the expected results.
        This method performs a comparison element by element based on their key of dict.

        :param source_values:         The list of dictionaries to compare.
        :param expected_values:       List of dicts expected to be exactly matched in records
        '''
        errors = ['The source_values and expected_values of product %s do not match.' % source_values['product_id'][1]]

        for index, expected_value in enumerate(expected_values):
            source_value = source_values['mrp_product_forecast_ids'][index]

            for key in expected_value.keys():
                if key not in source_value and key != 'available_to_promise':
                    errors += ['Missing key: %s' % key]
                    continue

                if key == 'available_to_promise':
                    value = source_value['starting_inventory_qty'] + source_value['replenish_qty'] - source_value['outgoing_qty']
                else:
                    value = source_value[key]

                if expected_value[key] != value:
                    errors += ['Differences at key %s at index %s: %s != %s' % (key, index, expected_value[key], value)]

        if len(errors) > 1:
            self.fail('\n'.join(errors))
