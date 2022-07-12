from odoo import models, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        Attachments = self.env['ir.attachment']
        access_right_for_create = self.env['hr.job'].check_access_rights('create', raise_exception=False)
        if self.env.user.has_group('website.group_website_designer') and not access_right_for_create:
            for vals in vals_list:
                if vals.get('res_model', False) == 'hr.job':
                    job = self.env['hr.job'].browse(vals.get('res_id', False))
                    website = job.exists() and job.website_id or False
                    if (website and website.allow_edit_website_jobs_website_setting) \
                    or (not website and self.env.company.allow_edit_website_jobs_company_setting):
                        Attachments |= super(Attachment, self.sudo()).create(vals)
                        vals_list.remove(vals)
        if vals_list:
            Attachments |= super(Attachment, self).create(vals_list)
        return Attachments

    def write(self, vals):
        access_right_for_edit = self.env['hr.job'].check_access_rights('write', raise_exception=False)
        if self.env.user.has_group('website.group_website_designer') and not access_right_for_edit:
            for r in self:
                if r.res_model == 'hr.job':
                    job = self.env['hr.job'].browse(r.res_id)
                    website = job.exists() and job.website_id or False
                    if (website and website.allow_edit_website_jobs_website_setting) \
                    or (not website and r.company_id.allow_edit_website_jobs_company_setting):
                        super(Attachment, r.sudo()).write(vals)
                        self -= r
        return super(Attachment, self).write(vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        access_right_for_edit = self.env['hr.job'].check_access_rights('write', raise_exception=False)
        if self.res_model == 'hr.job' and self.env.user.has_group('website.group_website_designer') and not access_right_for_edit:
            job = self.env['hr.job'].browse(self.res_id)
            website = job.exists() and job.website_id or False
            if (website and website.allow_edit_website_jobs_website_setting) \
            or (not website and self.company_id.allow_edit_website_jobs_company_setting):
                return super(Attachment, self.sudo()).copy(default)
        return super(Attachment, self).copy(default)

    def unlink(self):
        access_right_for_unlink = self.env['hr.job'].check_access_rights('unlink', raise_exception=False)
        if self.env.user.has_group('website.group_website_designer') and not access_right_for_unlink:
            for r in self:
                if r.res_model == 'hr.job':
                    job = self.env['hr.job'].browse(r.res_id)
                    website = job.exists() and job.website_id or False
                    if (website and website.allow_edit_website_jobs_website_setting) \
                    or (not website and r.company_id.allow_edit_website_jobs_company_setting):
                        super(Attachment, r.sudo()).unlink()
                        self -= r
        return super(Attachment, self).unlink()
