# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class sale_order(osv.Model):
    _inherit='sale.order'
    _columns = {
                'boom_store_id':fields.integer('Boom-Store ID'),
                'opencart_store_id':fields.integer('Open-Cart ID'),
                }
    def extra_offer(self, cr, uid, ids,context=None):
        if isinstance(ids,(list)):
            ids = ids[0]
        return self.read(cr, uid, ids, [],context=context)
class product_product(osv.Model):
    _inherit='product.product'
    _columns = {
                'description_sale':fields.html('Description for Quotation'),
                }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
