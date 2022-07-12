from odoo.tests import SingleTransactionCase


class TestCommon(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.ConfigSection = cls.env['config.section']
        cls.OdooVersion = cls.env['odoo.version']
        cls.OdooVersionConfig = cls.env['odoo.version.config']

        cls.odoo_version_13 = cls.env.ref('to_odoo_version.odoo_v13')

        cls.odoo_version_config_create_val = {
            'name': 'Odoo Version Config',
            'value': 0,
            'odoo_version_id': cls.odoo_version_13.id
        }
