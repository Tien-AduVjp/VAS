def migrate(cr, installed_version):
    # Remove unused fields
    cr.execute("""
        ALTER TABLE res_company
        DROP COLUMN IF EXISTS privkey_bin,
        DROP COLUMN IF EXISTS pubkey_bin""")
    cr.execute("""
        ALTER TABLE git_repository
        DROP COLUMN IF EXISTS protocol,
        DROP COLUMN IF EXISTS cloned_dir,
        DROP COLUMN IF EXISTS working_dir,
        DROP COLUMN IF EXISTS description""")
    cr.execute("""
        ALTER TABLE git_branch
        DROP COLUMN IF EXISTS remote_name,
        DROP COLUMN IF EXISTS description""")
