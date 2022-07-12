from odoo import models, api, _
from odoo.exceptions import AccessError


class Job(models.Model):
    _inherit = 'hr.job'

    def write(self, vals):
        access_right_for_edit = self.check_access_rights('write', raise_exception=False)
        if not access_right_for_edit and self.env.user.has_group('website.group_website_designer') and \
                self._validate_vals_for_website_editors(vals):
            if all([(r.website_id and r.website_id.allow_edit_website_jobs_website_setting) \
                    or (not r.website_id and r.company_id.allow_edit_website_jobs_company_setting) for r in self]):
                return super(Job, self.sudo()).write(vals)
            elif not access_right_for_edit:
                raise AccessError(_("You don't have permission to edit this recruitment post. "
                                "Please ask an administrator to configure website for the job first. "
                                "In case this job is not website specific, please get it configured to allow editing in General Settings / Recruitment ."))
        return super(Job, self).write(vals)

    @api.model
    def _get_writable_fnames_for_website_editors(self):
        website_seo_metadata_fnames = list(self.env['website.seo.metadata'].fields_get())
        website_published_multi_mixin_fnames = list(self.env['website.published.multi.mixin'].fields_get())
        extra_fnames = ['website_description']
        return set(website_seo_metadata_fnames + website_published_multi_mixin_fnames + extra_fnames)

    def _validate_vals_for_website_editors(self, vals):
        fnames = set(vals)
        validable_fnames = self._get_writable_fnames_for_website_editors()
        if fnames.issubset(validable_fnames):
            return True
        else:
            return False
