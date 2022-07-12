import os
import base64
import hashlib

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
from ..exceptions import InvalidInput

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config

try:
    import paramiko
except ImportError:
    _logger.error(_("Could NOT do 'import paramiko'. Please install paramiko by firing command 'pip install paramiko'"))


class SSHKeyPair(models.Model):
    _name = 'sshkey.pair'
    _description = 'SSHKey Pair'

    name = fields.Char(string='Name', required=True, index=True)
    privkey_bin = fields.Binary("Private Key", required=True, attachment=True)
    privkey_filename = fields.Char(string='Private Key Filename', help="Technical field to store file name of the Private Key")
    pubkey_bin = fields.Binary(string="Public Key", help="The key to send to the server when needed",
                               attachment=True)
    pubkey_filename = fields.Char(string='Public Key Filename', help="Technical field to store file name of the Public Key")
    privkey_passphrare = fields.Char(string='Privkey Passphrase', help="The password to decrypt the private key in case the key is password protected")
    type = fields.Selection([
        ('dsa', _('DSA')),
        ('rsa', _('RSA'))], string='Type', default='rsa', required=True)
    description = fields.Text("Description")
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user, help="The user who owns"
                             " this SSH Key and has full access to it.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,
                                 help='The company that owns this SSH Key and has full access to it.')
    pubkey_fingerprint = fields.Char(string='Public Key Fingerprint', compute='_compute_pubkey_fingerprint', store=True)

    @api.constrains('privkey_bin', 'type', 'privkey_passphrare')
    def _check_privkey_bin(self):
        for r in self:
            if r.privkey_bin:
                # try to load the key content. Exception will raise if key is invalid
                r.get_privkey()

    @api.onchange('privkey_filename')
    def _onchange_privkey_filename(self):
        if self.privkey_filename:
            self.name = self.privkey_filename

    @api.depends('pubkey_bin')
    def _compute_pubkey_fingerprint(self):
        for r in self:
            if r.pubkey_bin:
                r.pubkey_fingerprint = r._generate_fingerprint()
            else:
                r.pubkey_fingerprint = False

    def get_privkey_content(self):
        """
        Method to get the utf-8 decoded content of the field self.privkey_bin
        
        @return: the utf-8 decoded content of the field self.privkey_bin
        @rtype: string | None
        """
        try:
            return None if not self.privkey_bin else base64.decodebytes(self.privkey_bin).decode("utf-8")
        except TypeError as e:
            raise InvalidInput(_("Bytes-like object is expected during decoding Private Key!")) from e

    def get_pubkey_content(self):
        """
        Method to get the utf-8 decoded content of the field self.privkey_bin
        
        @return: the utf-8 decoded content of the field self.privkey_bin
        @rtype: string | None
        """
        try:
            return None if not self.pubkey_bin else base64.decodebytes(self.pubkey_bin).decode("utf-8")
        except TypeError as e:
            raise InvalidInput(_("Bytes-like object is expected during decoding Public Key!")) from e

    def _get_privkey_file(self):
        """
        @return: Return file-like object from the record's binary field privkey_bin
        @rtype: StringIO file-like object
        """
        return StringIO(self.get_privkey_content())

    def get_privkey(self):
        """
        @return: a new `.PKey` based on the given private key
        @rtype: .PKey
        @raises: `InvalidInput` -- if either the key file is invalid or there was an error reading the key file or Password is required for the private key
        """
        self.ensure_one()
        try:
            file = self._get_privkey_file()

            privkey_passphrare = self.privkey_passphrare or None
            if self.type == 'rsa':
                return paramiko.RSAKey.from_private_key(file, password=privkey_passphrare)
            else:
                return paramiko.DSSKey.from_private_key(file, password=privkey_passphrare)
        except IOError:
            raise InvalidInput(_("There was an error reading the key file"))
        except paramiko.PasswordRequiredException:
            raise InvalidInput(_("Password is required for the private key %s") % (self.name,))
        except paramiko.SSHException as e:
            raise InvalidInput(_("Invalid private key or passphrare. Please note that,"
                                 " when generating SSH Key with OpenSSH, you should add option `-m PEM` for RSA"))

    def _get_pubkey_file(self):
        """
        @return: Return file-like object from the record's binary field pubkey_bin
        @rtype: file-like object
        """
        try:
            return StringIO(base64.decodebytes(self.pubkey_bin).decode("utf-8"))
        except TypeError as e:
            raise InvalidInput(_("Bytes-like object is expected!")) from e

    def get_private_sshkeys_paths(self):
        """
        Get on-disk paths to the private sshkeys in self

        @return: list of abs paths in string
        @rtype: list
        """
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', self._name),
             ('res_field', '=', 'privkey_bin'),
             ('res_id', 'in', self.ids)])
        paths = attachments.mapped('store_fname')
        paths = [os.path.join(config.filestore(self.env.cr.dbname), path)
                 for path in paths]
        return paths

    def _generate_fingerprint(self):
        """
        Method to generate public key's fingerprint
        :rtype: string
        """
        # self.pubkey should be an instance of bytes when it already stored
        if isinstance(self.pubkey_bin, bytes):
            key_str = self.pubkey_bin.decode('utf-8')
        # self.pubkey should be an instance of string when it is not stored yet
        elif isinstance(self.pubkey_bin, str):
            key_str = self.pubkey_bin
        else:
            raise ValidationError(_("The Public Key data must be either string or bytes."))
        # Shamelessly copied from https://stackoverflow.com/questions/6682815/deriving-an-ssh-fingerprint-from-a-public-key-in-python
        key_split = key_str.strip().split()
        if len(key_split) > 1:
            key_split = key_split[1]
        else:
            key_split = key_split[0]
        encode_key_split = key_split.encode('ascii')
        key = base64.b64decode(encode_key_split)
        fp_plain = hashlib.md5(key).hexdigest()
        return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))
