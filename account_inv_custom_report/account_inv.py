from datetime import datetime, timedelta
import time
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
class account_invoice(osv.osv):
    _inherit = "account.invoice"

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
    			'product_img':fields.boolean('Report image'),
    }