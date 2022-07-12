import logging
import os
import shutil

_logger = logging.getLogger(__name__)

try:
    import git
except ImportError:
    _logger.error('Please install GitPython package and ensure git was also installed.')

from . import models
from . import wizard
from . import helper


def uninstall_hook(cr, reg):
    git_dir = helper.git_data_path()
    _logger.info('[uninstall hook] Removing directory {}'.format(git_dir))
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)
