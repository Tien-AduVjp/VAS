def migrate(cr, version):
    cr.execute("""
        UPDATE ir_attachment SET name='image_1920', res_field='image_1920' WHERE name='main_screenshot' AND res_model='odoo.module.version';
    """
    )
