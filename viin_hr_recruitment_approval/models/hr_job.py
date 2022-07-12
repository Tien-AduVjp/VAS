from odoo import models, fields, api


class HRJob(models.Model):
    _inherit = 'hr.job'

    recuitment_approval_ids = fields.One2many('approval.request', 'job_id',
                                  string='Recruitment Requests',
                                  readonly=True)
    recuitment_approvals_count = fields.Integer(string='Recruitment Requests Count', compute='_compute_recuitment_approvals_count', store=True)

    @api.depends('recuitment_approval_ids')
    def _compute_recuitment_approvals_count(self):
        for r in self:
            r.recuitment_approvals_count = len(r.recuitment_approval_ids)

    def _suggest_no_of_recruitment(self):
        for r in self:
            no_of_recruitment = sum(r.recuitment_approval_ids.filtered(lambda req: req.state == 'validate').mapped('expected_employees'))
            if r.no_of_recruitment < no_of_recruitment:
                r.no_of_recruitment = no_of_recruitment

    def set_recruit(self):
        res = super(HRJob, self).set_recruit()
        self._suggest_no_of_recruitment()
        return res
