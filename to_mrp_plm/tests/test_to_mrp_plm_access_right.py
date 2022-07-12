from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_to_mrp_plm_access_right_common import TestAccessRightCommon


@tagged('post_install','-at_install')
class TestAcessRightFunction(TestAccessRightCommon):
    def test_01_group_mrp_user_right(self):
        # Mrp user can read model mrp.eco
        self.eco.with_user(self.mrp_user).read([])
        # Mrp user can not read bom
        self.bom.with_user(self.mrp_user).read([])
        # Mrp user can not read eco type
        with self.assertRaises(AccessError):
            self.type.with_user(self.mrp_user).read([])
        # Mrp user can not read eco aproval template
        with self.assertRaises(AccessError):
            self.template.with_user(self.mrp_user).read([])
        # Mrp user can not read eco approval template
        with self.assertRaises(AccessError):
            self.stage.with_user(self.mrp_user).read([])
        # Mrp user can not read eco approval
        with self.assertRaises(AccessError):
            self.approval.with_user(self.mrp_user).read([])
        # Mrp user can not read eco tag
        with self.assertRaises(AccessError):
            self.tag.with_user(self.mrp_user).read([])

    def test_02_group_plm_user_right_model_eco(self):
        # Plm user can read ECO
        self.eco.with_user(self.plm_user).read([])
        # Plm user can update ECO
        self.eco.with_user(self.plm_user).write({'name': 'Change Eco 2'})
        # Plm user can create ECO
        eco2 = self.env['mrp.eco'].with_user(self.plm_user).create({
                'name': 'Change Furniture BoM 2',
                'stage_id': self.stage.id,
                'type_id': self.type.id,
                'type': 'bom',
                'product_tmpl_id': self.bom.product_tmpl_id.id,
                'bom_id':self.bom.id
                })
        # Plm user can delete ECO
        eco2.with_user(self.plm_user).unlink()

    def test_04_group_plm_user_right_model_eco_template(self):
        # Plm user can read ECO template
        self.template.with_user(self.plm_user).read([])
        # Plm user can not update ECO template
        with self.assertRaises(AccessError):
            self.template.with_user(self.plm_user).write({'name': 'Change Eco 2'})
        # Plm user can not create ECO template
        with self.assertRaises(AccessError):
            type = self.env['mrp.eco.approval.template'].with_user(self.plm_user).create({
                'name': 'Expert comments 1',
                'user_ids': [(4, self.mrp_user.id)],
                'approval_type': 'comment',
                'stage_id': self.stage.id
                })
        # Plm user can not delete ECO template
        with self.assertRaises(AccessError):
            self.template.with_user(self.plm_user).unlink()

    def test_05_group_plm_user_right_model_eco_stage(self):
        # Plm user can read ECO stage
        self.stage.with_user(self.plm_user).read([])
        # Plm user can not update ECO stage
        with self.assertRaises(AccessError):
            self.stage.with_user(self.plm_user).write({'name': 'Change Eco 2'})
        # Plm user can not create ECO stage
        with self.assertRaises(AccessError):
            type1 = self.env['mrp.eco.stage'].with_user(self.plm_user).create({
                'name': 'Cancel',
                'type_ids': [(4, self.type.id)],
                 })
        # Plm user can not delete ECO stage
        with self.assertRaises(AccessError):
            self.stage.with_user(self.plm_user).unlink()

    def test_06_group_plm_user_right_model_eco_approval(self):
        # Plm user can read ECO approval
        self.approval.with_user(self.plm_user).read([])
        # Plm user can update ECO approval
        self.approval.with_user(self.plm_user).write({'name': 'Change Eco 2'})
        # Plm user can create ECO approval
        approval = self.env['mrp.eco.approval'].with_user(self.plm_user).create({
                            'name': 'Comment 2',
                            'eco_id': self.eco1.id,
                            'approval_template_id': self.template.id
                            })
        # Plm user can delete ECO approval
        approval.with_user(self.plm_user).unlink()

    def test_07_group_plm_user_right_model_eco_tag(self):
        # Plm user can read ECO tag
        self.tag.with_user(self.plm_user).read([])
        # Plm user can update ECO tag
        self.tag.with_user(self.plm_user).write({'name': 'Change Eco 2'})
        # Plm user can create ECO tag
        tag = self.env['mrp.eco.tag'].with_user(self.plm_user).create({'name': 'Change1'})
        # Plm user can delete ECO tag
        tag.with_user(self.plm_user).unlink()

    def test_08_group_plm_manager_right_model_eco(self):
        # Plm manager can read ECO
        self.eco.with_user(self.plm_manager).read([])
        # Plm manager can update ECO
        self.eco.with_user(self.plm_manager).write({'name': 'Change Eco 2'})
        # Plm manager can create ECO
        eco = self.env['mrp.eco'].with_user(self.plm_manager).create({
                'name': 'Change Furniture BoM 2',
                'stage_id': self.stage.id,
                'type_id': self.type.id,
                'type': 'bom',
                'product_tmpl_id': self.bom.product_tmpl_id.id,
                'bom_id':self.bom.id
                })
        # Plm manager can delete ECO
        eco.with_user(self.plm_user).unlink()

    def test_09_group_plm_manager_right_model_eco_template(self):
        # Plm manager can read ECO template
        self.template.with_user(self.plm_manager).read([])
        # Plm manager can update ECO template
        self.template.with_user(self.plm_manager).write({'name': 'Change Eco 2'})
        # Plm manager can create ECO template
        type = self.env['mrp.eco.approval.template'].with_user(self.plm_manager).create({
                'name': 'Expert comments 1',
                'user_ids': [(4, self.mrp_user.id)],
                'approval_type': 'comment',
                'stage_id': self.stage.id
                })
        # Plm manager can  delete ECO template
        type.with_user(self.plm_manager).unlink()

    def test_10_group_plm_manager_right_model_eco_stage(self):
        # Plm manager can read ECO stage
        self.stage.with_user(self.plm_manager).read([])
        # Plm manager can update ECO stage
        self.stage.with_user(self.plm_manager).write({'name': 'Change Eco 2'})
        # Plm manager can create ECO stage
        stage1 = self.env['mrp.eco.stage'].with_user(self.plm_manager).create({
                'name': 'Cancel',
                'type_ids': [(4, self.type.id)],
                 })
        # Plm manager can delete ECO stage
        stage1.with_user(self.plm_manager).unlink()

    def test_11_group_plm_manager_right_model_eco_approval(self):
        # Plm manager can read ECO approval
        self.approval.with_user(self.plm_manager).read([])
        # Plm manager can update ECO approval
        self.approval.with_user(self.plm_manager).write({'name': 'Change Eco 2'})
        # Plm manager can create ECO approval
        approval = self.env['mrp.eco.approval'].with_user(self.plm_manager).create({
                            'name': 'Commnent 2',
                            'eco_id': self.eco1.id,
                            'approval_template_id': self.template.id
                            })
        # Plm manager can delete ECO approval
        approval.with_user(self.plm_manager).unlink()

    def test_12_group_plm_manager_right_model_eco_tag(self):
        # Plm manager can read ECO tag
        self.tag.with_user(self.plm_manager).read([])
        # Plm manager can update ECO tag
        self.tag.with_user(self.plm_manager).write({'name': 'Change Eco 2'})
        # Plm manager can create ECO tag
        tag = self.env['mrp.eco.tag'].with_user(self.plm_manager).create({'name': 'Change1'})
        # Plm manager can delete ECO tag
        tag.with_user(self.plm_manager).unlink()

