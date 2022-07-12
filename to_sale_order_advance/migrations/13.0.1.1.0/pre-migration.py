from odoo import api, SUPERUSER_ID


def _move_old_data_to_account_payment_sale_order_rel_table():
    return """
        CREATE TABLE IF NOT EXISTS account_payment_sale_order_rel (
            account_payment_id INTEGER NOT NULL,
            sale_order_id INTEGER NOT NULL,
            UNIQUE(account_payment_id, sale_order_id));
        COMMENT ON TABLE account_payment_sale_order_rel IS 'RELATION BETWEEN account_payment AND sale_order';
        CREATE INDEX ON account_payment_sale_order_rel (account_payment_id);
        CREATE INDEX ON account_payment_sale_order_rel (sale_order_id);

        WITH account_payment_temp AS (
            SELECT
                payment.id,
                payment.sale_order_id
            FROM account_payment payment
            WHERE payment.sale_order_id > 0
        )

        INSERT INTO account_payment_sale_order_rel(account_payment_id, sale_order_id)
            SELECT account_payment_temp.id, account_payment_temp.sale_order_id FROM account_payment_temp;
    """

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Move data to account_payment_sale_order_rel table
    cr.execute(_move_old_data_to_account_payment_sale_order_rel_table())
