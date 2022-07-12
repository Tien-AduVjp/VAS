import os
import shutil

from git import Git
from odoo.tools import config


def migrate(cr, installed_version):
    data_path = config.filestore(cr.dbname)
    git_data_path = os.path.join(data_path, 'git')

    # Migrate repositories
    cr.execute("""
        ALTER TABLE git_repository
        RENAME COLUMN url TO remote_url""")
    cr.execute("""
        ALTER TABLE git_repository
        ADD COLUMN path VARCHAR""")
    cr.execute("""SELECT id, cloned_dir FROM git_repository""")
    repos = cr.fetchall()
    for row in repos:
        repo_id, _ = row
        repo_path = os.path.join(git_data_path, str(repo_id), 'repo')
        cr.execute("""UPDATE git_repository SET path = %s WHERE id = %s""", (repo_path, repo_id))

    # Migrate branches
    cr.execute("""
        ALTER TABLE git_branch
        ADD COLUMN recent_pull_time TIMESTAMP""")

    # Migrate ssh keys with default name to company id and type to RSA
    cr.execute("""SELECT id, pubkey_bin, privkey_bin FROM res_company""")
    companies = cr.fetchall()
    key_pairs = [(str(row[0]), 'rsa') + row for row in companies if row[2]]
    cr.executemany("""
        INSERT INTO sshkey_pair (name, type, company_id, pubkey_bin, privkey_bin)
        VALUES (%s, %s, %s, %s, %s)""", key_pairs)

    if not os.path.exists(git_data_path):
        return

    # Copy repositories to new location and convert them to bare repositories
    git_data_path_new = os.path.join(data_path, 'git.new')
    if os.path.exists(git_data_path_new):
        shutil.rmtree(git_data_path_new)
    for row in repos:
        repo_id, cloned_dir = row
        if not cloned_dir:
            continue
        repo_path = os.path.join(git_data_path, cloned_dir, '.git')
        if not os.path.exists(repo_path):
            continue
        repo_path_new = os.path.join(git_data_path_new, str(repo_id), 'repo')
        shutil.copytree(repo_path, repo_path_new)
        Git(repo_path_new).config('--bool', 'core.bare', 'true')

    if not os.path.exists(git_data_path_new):
        return

    # Switch to use new git data
    git_data_path_old = os.path.join(data_path, 'git.old')
    if os.path.exists(git_data_path_old):
        shutil.rmtree(git_data_path_old)
    shutil.move(git_data_path, git_data_path_old)
    shutil.move(git_data_path_new, git_data_path)
    shutil.rmtree(git_data_path_old)
