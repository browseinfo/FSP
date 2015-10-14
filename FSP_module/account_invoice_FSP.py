# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

class account_invoice1(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'web_store': fields.char('Web Store'),
        'vat_tax_number': fields.char('Vat Tax Number'),
    }

account_invoice1()
class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    _columns = {
    }

account_bank_statement()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'account_id':fields.many2one('account.account','Account',domain=[('type','<>','view'), ('type', '<>', 'closed')]),
        }
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        inv_vals = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context=context)
        print "\n\n****lines",line
        inv_vals.update({'account_id':line.account_id.id})        
        return inv_vals
         

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
