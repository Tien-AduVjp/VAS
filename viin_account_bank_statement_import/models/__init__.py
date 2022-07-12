# -*- encoding: utf-8 -*-

from . import account_bank_statement_line
from . import account_journal
from . import ir_attachment
# The below ir_attachement* modules MUST be imported after the above ir_attachment
# as they all present the same model 'ir.attachment' but overriding things by order
from . import ir_attachment_csv
from . import ir_attachment_xlsx
