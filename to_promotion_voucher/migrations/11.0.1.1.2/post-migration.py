from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sequence_ids = env['ir.sequence']
    xml_ids = [
        'sequence_issue_release_order',
        'sequence_voucher_move_order',
        'sequence_voucher_give_order',
        'sequence_picking_type_receipt_voucher',
        'sequence_picking_type_issue_release_order',
        'sequence_picking_type_move_order',
        ]
    for xml_id in xml_ids:
        record = env.ref('to_promotion_voucher.' + xml_id, raise_if_not_found=False)
        if record:
            sequence_ids += record
    if sequence_ids:
        sequence_ids.write({'company_id': False})
