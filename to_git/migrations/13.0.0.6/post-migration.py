# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    git_repos = env['git.repository'].search([])
    if git_repos:
        git_repos._compute_net_resources()
