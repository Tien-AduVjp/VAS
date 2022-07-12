from odoo.tests.common import TransactionCase

class TestPLMCommon(TransactionCase):

    def setUp(self):
        super(TestPLMCommon, self).setUp()
        
        self.user_admin = self.env.ref('base.user_admin')
        self.user_demo = self.env.ref('base.user_demo')
                                      
        self.new_stage = self.env.ref('to_mrp_plm.eco_stage_new')
        self.progress_stage = self.env.ref('to_mrp_plm.eco_stage_progress')
        self.validated_stage = self.env.ref('to_mrp_plm.eco_stage_validated')
        self.validated_stage.update({'is_final_stage': True})
        
        self.comment_role = self.env['mrp.eco.approval.template'].create({
            'name': 'Expert comments',
            'user_ids': [(4, self.env.user.id), (4, self.user_admin.id)],
            'approval_type': 'comment',
            'stage_id': self.new_stage.id
            })
        self.opt_approval_role = self.env['mrp.eco.approval.template'].create({
            'name': 'Validate expert comments',
            'user_ids': [(4, self.user_demo.id),(4, self.env.user.id)],
            'approval_type': 'optional',
            'stage_id': self.progress_stage.id
            })
        self.approval_role = self.env['mrp.eco.approval.template'].create({
            'name': 'Validate expert comments',
            'user_ids': [(4, self.user_admin.id),(4, self.env.user.id)],
            'approval_type': 'mandatory',
            'stage_id': self.validated_stage.id
            })
        
        self.eco_type = self.env.ref('to_mrp_plm.eco_type0')
        
        self.bom_desk = self.env.ref('mrp.mrp_bom_desk')
        
        self.eco = self.env['mrp.eco']
        self.eco1 = self.eco.create({
            'name': 'Change Funiture BoM',
            'stage_id': self.new_stage.id,
            'type_id': self.eco_type.id,
            'type': 'bom',
            'product_tmpl_id': self.bom_desk.product_tmpl_id.id,
            'bom_id':self.bom_desk.id
            })

        self.routing_funiture_assembly = self.env.ref('mrp.mrp_routing_3')
        

        
        
