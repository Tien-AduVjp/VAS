import logging
import os
import threading

from odoo.http import request
from odoo.tools import config

_logger = logging.getLogger(__name__)


def git_data_path():
    """
    Returns path to git data.
    """
    dbname = threading.current_thread().dbname
    return os.path.join(config.filestore(dbname), 'git')


def rerun_with_credentials(method):
    """
    We must use this decorator for the methods we want to be able to be rerun
    automatically after user submits credentials.
    """

    def wrapper(self, *args, **kwargs):
        # This feature should do nothing in a automatic cron job.
        if not request:
            return method(self, *args, **kwargs)

        # save current call to stack to re-call later if it failed
        if not hasattr(request, 'o_call_stack'):
            request.o_call_stack = []
        call = dict(name=method.__name__,
                    model=self._name,
                    ids=self.ids)
        request.o_call_stack.append(call)

        try:
            return method(self, *args, **kwargs)
        except MissingCredentialsError as e:
            # Propagate missing credentials error until the bottom of the call
            # stack, where we can response authentication action to the request.
            call = request.o_call_stack.pop()
            if request.o_call_stack:
                raise
            return {
                'name': 'Git Authentication',
                'type': 'ir.actions.act_window',
                'res_model': 'git.authenticate',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'origin_call': call,
                    'default_username': e.username
                }
            }

    return wrapper


class MissingCredentialsError(Exception):
    def __init__(self, username):
        self.username = username
