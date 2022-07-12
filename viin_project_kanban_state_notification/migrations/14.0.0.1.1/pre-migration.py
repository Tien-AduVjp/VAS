def _generate_project_data(cr):
    cr.execute("""
    ALTER TABLE project_project
        ADD COLUMN IF NOT EXISTS kanban_state_notification BOOLEAN;

    UPDATE project_project
        SET kanban_state_notification = true;
    """)

def migrate(cr, version):
    _generate_project_data(cr)
