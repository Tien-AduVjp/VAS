# -*- coding: utf-8 -*-
import base64

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['wizard.version.config.from.file']._load_default_files()

