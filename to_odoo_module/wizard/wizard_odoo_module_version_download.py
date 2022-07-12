from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class WizardOdooModuleVersionPublicDownloadUrl(models.TransientModel):
    _name = 'wizard.odoo.module.version.public.download.url'
    _inherit = 'abstract.odoo.module.version.public.download.url'
    _description = 'Wizard Odoo Module Version Download URL'

    wizard_id = fields.Many2one('wizard.odoo.module.version.download', string='Download Wizard', required=True, ondelete='cascade')


class WizardOdooModuleVersionDownloads(models.TransientModel):
    _name = 'wizard.odoo.module.version.download'
    _description = 'Wizard Odoo Module Version Download'

    @api.model
    def _default_module_versions(self):
        ctx = self._context
        active_ids = ctx.get('active_ids', [])
        active_model = ctx.get('active_model')
        return self.env[active_model].browse(active_ids)

    module_ids = fields.Many2many('odoo.module.version', string='Odoo Module Versions', required=True,
                                  default=lambda self: self._default_module_versions())
    file = fields.Binary(string='Zipped Source Code', attachment=True, readonly=True,
                         help="The source code of the selected Odoo Module Versions in zip archive")
    zip_all = fields.Binary(string='All Zipped', attachment=True, readonly=True,
                            help="The source code of the selected Odoo Module versions and their"
                            " dependencies in zip archive")
    filename = fields.Char(string='File Name', compute='_compute_file_name',
                           help="Technical field for forming the file name of the Zipped Source Code")
    zip_all_filename = fields.Char(string='All Zipped File Name', compute='_compute_file_name',
                                   help="Technical field for forming the file name of the All Zipped")
    state = fields.Selection([('choose', 'choose'), ('successful', 'successful')], default='choose')
    download_url_ids = fields.One2many('wizard.odoo.module.version.public.download.url', 'wizard_id',
                                       compute='_compute_download_url_ids', store=True,
                                       string='Public Download URLs', readonly=True)

    @api.constrains('module_ids')
    def _check_unique_odoo_version(self):
        for r in self:
            odoo_versions = r.module_ids.mapped('odoo_version_id')
            if len(odoo_versions) > 1:
                raise ValidationError(_("You may not select apps in mutiple Odoo versions. Please do filter to"
                                        " ensure that all the selected belong to the same Odoo version"))

    @api.depends('module_ids')
    def _compute_file_name(self):
        for r in self:
            filename = False
            zip_all_filename = False

            modules_count = len(r.module_ids)
            if modules_count == 1:
                filename = r.module_ids.filename
                zip_all_filename = r.module_ids.zip_all_filename
            elif modules_count > 1:
                odoo_version_strings = r.module_ids.mapped('odoo_version_id.name')
                odoo_version_strings = ["Odoo_v%s" % ver_str for ver_str in odoo_version_strings]
                filename = "apps_package_{0}.zip".format("_".join(odoo_version_strings))
                zip_all_filename = "apps_and_dependencies_package_{0}.zip".format("__".join(odoo_version_strings))

            r.update({
                'filename': filename,
                'zip_all_filename': zip_all_filename
                })

    def get_top_level_modules(self):
        """
        Get the top level modules in the dependencies tree
        """
        exclude_standard_odoo_modules = self._context.get('exclude_standard_odoo_modules', True)
        return self.module_ids.with_context(
            exclude_standard_odoo_modules=exclude_standard_odoo_modules
            ).get_top_level_module_versions()

    @api.depends('module_ids')
    def _compute_download_url_ids(self):
        for r in self:
            vals_list = [(0, 0, {
                'odoo_module_version_id': omv.id
                }) for omv in r.get_top_level_modules()]
            r.download_url_ids = [(5, 0, 0)] + vals_list

    def zip_dirs(self):
        """
        This zip all the selected modules then store in the field `file`
            and zip all the selected modules and their dependencies then store in the field `zip_all`
        """
        self.ensure_one()
        data = {}
        file = self.module_ids.make_zip()
        if file:
            data['file'] = file
        exclude_standard_odoo_modules = self._context.get('exclude_standard_odoo_modules', True)
        modules_and_dependencies = self.module_ids.with_context(
            exclude_standard_odoo_modules=exclude_standard_odoo_modules).get_recursive_dependencies(incl_the_current=True)
        zip_all = modules_and_dependencies.make_zip()
        if zip_all:
            data['zip_all'] = zip_all
        if bool(data):
            data['state'] = 'successful'
            self.write(data)

    def action_prepare_download(self):
        self.ensure_one()
        for module in self.module_ids:
            if not module.git_branch_id:
                raise UserError(_("The module version %s has no git branch specified, then there is no thing to download."
                                  " Please exclude it from your download.") % module.display_name)
        self.module_ids.increase_download_count()
        self.zip_dirs()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

