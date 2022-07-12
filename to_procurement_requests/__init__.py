from . import models
#
# 
# from odoo import api,SUPERUSER_ID,_
# from odoo.exceptions import AccessDenied
# from odoo.http import request
# 
# def pre_init_hook(cr):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     ''' If this module installed by using command line, the raise an exception is the following will the system is break.
#     So we only check on UI, that mean a http request must exist. Otherwise (http request is unbounded object) it is ignored. 
#     '''
#     try:
#         # try if http request exist, that mean somebody try install module through UI
#         current_user = request.env.user
#         if env['ir.module.module'].search([('name', '=', 'to_procurement_approval')], limit=1) and current_user.id != SUPERUSER_ID:
#             raise AccessDenied(_('The module is deprecated, it cannot be installed. Please install module Procurement Approvals (to_procurement_approval)'))
#     except RuntimeError: # Otherwise it maybe installed through command line, eg. runbot system,...
#         return
#     