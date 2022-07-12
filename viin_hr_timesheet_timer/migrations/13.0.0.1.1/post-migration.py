# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.addons.viin_hr_timesheet_timer.__init__ import _fix_missing_start_date_end_date

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_missing_start_date_end_date(env)
