from random import randint

from odoo import fields
from odoo.tests.common import tagged, HttpCase


@tagged("post_install", "-at_install")
class TestProductReturnReasonPos(HttpCase):
        
    def test_01(self):
        env = self.env(user=self.env.ref('base.user_admin'))
        pos_config = env.ref('point_of_sale.pos_config_main')
        
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'point_of_sale')], limit=1).state = 'installed'
        self.check_allow_create_new_reason(pos_config)
        self.check_not_allow_create_new_reason(pos_config)
        
    def check_not_allow_create_new_reason(self, pos_config):
        pos_config.write({'allow_to_create_new_reason': False})
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'not_allow_create_new_reason', login="admin")
        pos_config.current_session_id.action_pos_session_closing_control()
    
    def check_allow_create_new_reason(self, pos_config):
        pos_config.write({'allow_to_create_new_reason': True})
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'allow_create_new_reason', login="admin")
        pos_config.current_session_id.action_pos_session_closing_control()
