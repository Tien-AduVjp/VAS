# load order is IMPORTANT for automatic computation of the field `timesheet_approval`
from . import hr_department
from . import hr_job
from . import hr_contract

# any order below would be fine
from . import hr_timesheet
from . import approval_request
from . import approval_request_type
from . import res_company
