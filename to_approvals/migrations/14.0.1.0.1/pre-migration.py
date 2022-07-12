def _generate_temporary_data(cr):
    cr.execute("""
    ALTER TABLE approval_request_type
        ADD COLUMN IF NOT EXISTS legacy_responsible_id INTEGER,
        ADD COLUMN IF NOT EXISTS legacy_validation_type character varying(64);

    UPDATE approval_request_type
        SET legacy_responsible_id = responsible_id,
            legacy_validation_type = validation_type;
    """
    )

    cr.execute("""
    ALTER TABLE approval_request
        ADD COLUMN IF NOT EXISTS legacy_first_approver_id INTEGER,
        ADD COLUMN IF NOT EXISTS legacy_second_approver_id INTEGER,
        ADD COLUMN IF NOT EXISTS legacy_state character varying(64);

    UPDATE approval_request
        SET legacy_first_approver_id = first_approver_id,
            legacy_second_approver_id = second_approver_id,
            legacy_state = state;
    """
    )


def migrate(cr, installed_version):
    _generate_temporary_data(cr)
