def migrate(cr, version):
    cr.execute('UPDATE res_company SET prevent_unlink_related_pickings = TRUE')
