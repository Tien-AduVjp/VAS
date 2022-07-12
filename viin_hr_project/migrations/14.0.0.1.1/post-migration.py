# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_task_assign_employee(env):
    tasks = env['project.task'].with_context(active_test=False).search([])
    tasks._compute_assign_employee()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_task_assign_employee(env)

