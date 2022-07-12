# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE res_users
        SET notification_type = 'email'
        WHERE notification_type = 'inbox';
    """)

