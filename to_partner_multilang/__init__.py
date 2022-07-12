from . import models

from odoo.tests.common import TransactionCase, SavepointCase


setUpTransactionCase = TransactionCase.setUp
setUpSavepointCase = SavepointCase.setUp


def _setUpTransactionCase_plus(self):
    """Override setUp method of TransactionCase to avoid recompute
    to avoid recomputing the value of the translated fields
    when changing the language
    """
    setUpTransactionCase(self)

    _disable_translation_of_fields(
        self,
        'res.partner',
        ['name', 'display_name', 'commercial_company_name'],
    )
    _disable_translation_of_fields(self, 'res.company', ['name'])

    self.addCleanup(
        _enable_translation_of_fields,
        self,
        'res.partner',
        ['name', 'display_name', 'commercial_company_name'],
    )
    self.addCleanup(
        _enable_translation_of_fields,
        self,
        'res.company',
        ['name'],
    )


def _setUpSavepointCase_plus(self):
    """Override setUp method of SavepointCase to avoid recompute
    to avoid recomputing the value of the translated fields
    when changing the language
    """
    setUpSavepointCase(self)

    _disable_translation_of_fields(
        self,
        'res.partner',
        ['name', 'display_name', 'commercial_company_name'],
    )
    _disable_translation_of_fields(self, 'res.company', ['name'])

    self.addCleanup(
        _enable_translation_of_fields,
        self,
        'res.partner',
        ['name', 'display_name', 'commercial_company_name'],
    )
    self.addCleanup(
        _enable_translation_of_fields,
        self,
        'res.company',
        ['name'],
    )


def _disable_translation_of_fields(self, model_name, fields_name):
    """Disable the translation of the fields's values"""
    for field_name in fields_name:
        _disable_translation_of_field(self, model_name, field_name)


def _disable_translation_of_field(self, model_name, field_name):
    """Disable the translation of the field's values"""
    attributes = self.env[model_name]._fields[field_name].__dict__
    if attributes.get('translate', False) and field_name != 'name':
        attributes['translate'] = False
    for ctx in ['depends_context', '_depends_context']:
        if ctx in attributes:
            ctx_tmp = list(attributes[ctx])
            if 'lang' in ctx_tmp:
                ctx_tmp.remove('lang')
                attributes[ctx] = tuple(ctx_tmp)


def _enable_translation_of_fields(self, model_name, fields_name):
    """Enable the translation of the fields's values"""
    for field_name in fields_name:
        _enable_translation_of_field(self, model_name, field_name)


def _enable_translation_of_field(self, model_name, field_name):
    """Enable the translation of the field's values"""
    attributes = self.env[model_name]._fields[field_name].__dict__
    if 'translate' in attributes and field_name != 'name':
        attributes['translate'] = True
    for ctx in ['depends_context', '_depends_context']:
        if ctx in attributes:
            ctx_tmp = list(attributes[ctx])
            if 'lang' not in ctx_tmp:
                ctx_tmp.append('lang')
                attributes[ctx] = tuple(ctx_tmp)


def post_load():
    TransactionCase.setUp = _setUpTransactionCase_plus
    SavepointCase.setUp = _setUpSavepointCase_plus
