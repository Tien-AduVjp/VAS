from odoo import models, fields, api
from odoo.addons.crm.models import crm_lead

CRM_LEAD_FIELDS_TO_MERGE = crm_lead.CRM_LEAD_FIELDS_TO_MERGE + [
    'team_leader_id',
    'regional_manager_id',
    'crm_team_region_id'
    ]

crm_lead.CRM_LEAD_FIELDS_TO_MERGE = CRM_LEAD_FIELDS_TO_MERGE

class Lead(models.Model):
    _inherit = "crm.lead"

    team_leader_id = fields.Many2one('res.users', string='Team Leader', compute='_compute_team_id', store=True)
    crm_team_region_id = fields.Many2one('crm.team.region', string='Sales Region', compute='_compute_crm_team_region_id', store=True)
    regional_manager_id = fields.Many2one('res.users', string='Regional Manager', compute='_compute_regional_manager_id', store=True)

    @api.depends('team_id')
    def _compute_team_id(self):
        for r in self:
            r.team_leader_id = r.team_id.user_id.id

    @api.depends('team_id', 'user_id')
    def _compute_crm_team_region_id(self):
        for r in self:
            if r.team_id:
                r.crm_team_region_id = r.team_id.crm_team_region_id.id
            elif not r.crm_team_region_id:
                r.crm_team_region_id = r.user_id.sales_region_manager_ids[:1] or r.user_id.sales_region_assistant_ids[:1]
            else:
                r.crm_team_region_id = r.crm_team_region_id

    @api.depends('crm_team_region_id')
    def _compute_regional_manager_id(self):
        for r in self:
            r.regional_manager_id = r.crm_team_region_id.user_id
