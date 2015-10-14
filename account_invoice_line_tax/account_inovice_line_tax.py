#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _compute_tax_line(self, cr, uid, ids, name, args, context=None):
        res ={}
        for line in self.browse(cr, uid, ids, context=context):
            taxes = self.pool.get('account.tax').compute_all(cr, uid, line.invoice_line_tax_id, line.price_unit, line.quantity, )
            res[line.id] = taxes['taxes'][0]['amount']
        return res

    _columns = {
        'tax_par_line': fields.function(_compute_tax_line, digits_compute=dp.get_precision('Account'), string='Tax Amount', help='Count tax par line'),
        'product_img':fields.boolean(),
    }

account_invoice_line()
