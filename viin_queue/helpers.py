import concurrent.futures

from odoo import api
from odoo.models import BaseModel


def multi_async(model_method, max_workers=10, wait=False):
    records = model_method.__self__
    method_name = model_method.__name__
    if not isinstance(records, BaseModel):
        raise ValueError('%s must be a method of a model.' % method_name)

    def do(record, *args, **kwargs):
        with api.Environment.manage():
            with records.pool.cursor() as cr:
                record = record.with_env(record.env(cr=cr))
                getattr(record, method_name)(*args, **kwargs)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='%s.' % records._name)
    executor.map(do, records)
    executor.shutdown(wait=wait)
