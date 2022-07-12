from odoo import models, fields, api


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'
    _mail_post_access = 'read'

    approval_id = fields.Many2one('approval.request', string='Recruitment Request', compute='_compute_approval_id', store=True, index=True)

    @api.depends('job_id')
    def _compute_approval_id(self):
        approvals = self.env['approval.request'].search([
            ('state', '=', 'validate'),
            ('job_id', 'in', self.job_id.ids)])
        for r in self:
            r.approval_id = approvals.filtered(lambda req: req.job_id == r.job_id)[:1]
