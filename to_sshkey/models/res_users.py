from odoo import models, fields
from odoo.osv import expression


class ResUsers(models.Model):
    _inherit = 'res.users'

    sshkey_pair_ids = fields.One2many('sshkey.pair', 'user_id', string='SSH Keys')

    @classmethod
    def _build_model(cls, pool, cr):
        User = super(ResUsers, cls)._build_model(pool, cr)
        if 'sshkey_pair_ids' not in User.SELF_WRITEABLE_FIELDS:
            User.SELF_WRITEABLE_FIELDS.append('sshkey_pair_ids')
        if 'sshkey_pair_ids' not in User.SELF_READABLE_FIELDS:
            User.SELF_READABLE_FIELDS.append('sshkey_pair_ids')
        return User

    def _personal_sshkeys_only(self):
        if not self.has_group('to_sshkey.group_sshkey_manager') and not self.env.su:
            return True
        return False

    def _prepare_available_sshkey_pairs_domain(self):
        self.ensure_one()
        domain = ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)]
        if self._personal_sshkeys_only():
            personal_domain = ['|', ('user_id', '=', self.id), ('user_id', '=', False)]
            domain = expression.AND([personal_domain, domain])
        return domain

    def get_available_sshkey_pairs(self):
        """
        Get all the sshkey pairs that the user can use

        @return: sshkey.pair recordset
        @rtype: sshkey.pair
        """
        self.ensure_one()
        domain = self._prepare_available_sshkey_pairs_domain()
        return self.env['sshkey.pair'].search(domain)

    def get_private_sshkeys_paths(self):
        """
        Get on-disk paths to the private sshkeys that the user has access

        @return: list of abs paths in string
        @rtype: list
        """
        self.ensure_one()
        key_pairs = self.get_available_sshkey_pairs()
        paths = key_pairs.get_private_sshkeys_paths()
        return paths
