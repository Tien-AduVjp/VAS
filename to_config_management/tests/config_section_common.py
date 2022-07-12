from odoo.tests import TransactionCase


class ConfigSectionCommon(TransactionCase):

    def setUp(self):
        super(ConfigSectionCommon, self).setUp()

        self.create_val = {
            'name': 'CONFIG SECTION'
        }
        self.config_section = self.env['config.section']

