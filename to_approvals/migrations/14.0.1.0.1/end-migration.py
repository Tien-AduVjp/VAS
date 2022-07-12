def _drop_temp_column(cr):
    cr.execute(
        """
            ALTER TABLE approval_request_type
                DROP COLUMN legacy_responsible_id,
                DROP COLUMN legacy_validation_type;
            ALTER TABLE approval_request
                DROP COLUMN legacy_first_approver_id,
                DROP COLUMN legacy_second_approver_id,
                DROP COLUMN legacy_state;
        """
    )

def _update_approval_request_legacy_state(cr):
    # ensure the states are the same as they were before migration
    cr.execute("""
    UPDATE approval_request
        SET state = CASE
                WHEN legacy_state = 'validate1' THEN 'confirm'
            ELSE legacy_state
            END
    """)

def migrate(cr, installed_version):
    _update_approval_request_legacy_state(cr)
    # don't drop temporary columns please,
    # we may need them if any problems after migration
    # _drop_temp_column(cr)
