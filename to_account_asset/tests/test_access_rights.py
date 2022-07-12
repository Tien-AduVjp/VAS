from odoo.exceptions import AccessError
from odoo.tools import mute_logger
from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install', 'access_rights')
class TestAssetAccessRight(asset_common.AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        res_users_billing_user = cls.env.ref('account.group_account_invoice')
        res_users_account_user = cls.env.ref('account.group_account_user')
        res_users_account_manager = cls.env.ref('account.group_account_manager')

        User = cls.env['res.users'].with_context(no_reset_password=True)
        cls.billing_user = User.create(dict(
            name="Billing User",
            login="billing_user",
            email="billing_user@yourcompany.com",
            groups_id=[(6, 0, [res_users_billing_user.id])]
        ))
        cls.account_user = User.create(dict(
            name="Accountant",
            login="account_user",
            email="account_user@yourcompany.com",
            groups_id=[(6, 0, [res_users_account_user.id])]
        ))
        cls.account_manager = User.create(dict(
            name="Adviser",
            login="account_manager",
            email="account_manager@yourcompany.com",
            groups_id=[(6, 0, [res_users_account_manager.id])]
        ))

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_01_accountant_user_access_rights(self):
        """Accountant user without Accounting Assets Management access rights
        """
        # Test: category
        asset_category = self.asset_category.with_user(self.account_user)

        # Accountant user can see the category
        asset_category.read([])
        # Accountant user can not update the category
        self.assertRaises(AccessError, asset_category.write, {'name': 'modify by account user'})
        # Accountant user can not delete the category
        self.assertRaises(AccessError, asset_category.unlink)
        # Accountant user can not create the category
        self.assertRaises(AccessError,
                          self.env['account.asset.category'].with_user(self.account_user).create,
                          self._prepare_asset_category_vals())

        # Test: asset
        asset = self._create_asset().with_user(self.account_user)

        # Accountant user can see the asset
        asset.read([])
        # Accountant user can not update the asset
        self.assertRaises(AccessError, asset.write, {'name': 'modify by account user'})
        # Accountant user can not delete the asset
        self.assertRaises(AccessError, asset.unlink)
        # Accountant user can not create the asset
        self.assertRaises(AccessError, asset.copy)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_02_accountant_user_with_group_asset_manager_access_rights(self):
        """Accountant user with Accounting Assets Management access rights.
        He have fully access rights in asset apps.
        """
        self.account_user.write({'groups_id': [(4, self.group_asset_manager.id)]})
        # Test: category
        asset_category = self.asset_category.with_user(self.account_user)

        asset_category.read([])
        asset_category.write({'name': 'modify by account user'})

        asset_category_copy = self.env['account.asset.category'].with_user(self.account_user).create(self._prepare_asset_category_vals())
        asset_category_copy.with_user(self.account_user).unlink()

        # Test: asset
        asset = self._create_asset().with_user(self.account_user)

        asset.read([])
        asset.write({'name': 'modify by account user'})
        asset_copy = asset.copy()
        asset_copy.with_user(self.account_user).unlink()

    def test_03_billing_user_without_group_asset_manager_access_rights(self):
        """Billing user without Accounting Assets Management access rights"""
        # Test: category
        asset_category = self.asset_category.with_user(self.billing_user)

        # Billing user can see the category
        asset_category.read([])
        # Billing user can not update the category
        with self.assertRaises(AccessError):
            asset_category.write({'name': 'modify by account user'})
        # Billing user can not delete the category
        with self.assertRaises(AccessError):
            asset_category.unlink()
        # Billing user can not create the category
        with self.assertRaises(AccessError):
            self.env['account.asset.category'].with_user(self.billing_user).create(
                self._prepare_asset_category_vals()
                )

        # Test: asset
        asset = self._create_asset().with_user(self.billing_user)

        # Billing user cannot see the asset
        with self.assertRaises(AccessError):
            asset.read([])
        # Billing user can not update the asset
        with self.assertRaises(AccessError):
            asset.write({'name': 'modify by account user'})
        # Billing user can not delete the asset
        with self.assertRaises(AccessError):
            asset.unlink()
        # Billing user can not create the asset
        with self.assertRaises(AccessError):
            asset.copy()

    def test_04_invoice_flow_with_billing_user(self):
        """Test invoice flow with billing user."""
        products = self.product_a | self.product_b
        invoice = self.init_invoice('in_invoice', products=products).with_user(self.billing_user)

        invoice.invoice_line_ids[0].asset_category_id = self.asset_category.id

        invoice._post()
        invoice.button_cancel()
        invoice.button_draft()
        invoice.with_context(force_delete=True).unlink()
