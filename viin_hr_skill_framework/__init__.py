# -*- coding: utf-8 -*-

from . import models
from . import report

from odoo import api, SUPERUSER_ID


def _generate_skill_description_records(env):
    skill_types = env['hr.skill.type'].search([])
    if skill_types:
        skill_types._synch_description()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_skill_description_records(env)
