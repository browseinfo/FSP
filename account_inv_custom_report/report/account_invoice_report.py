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

import time
from openerp.report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context)
        self.index = 0
        self.localcontext.update({
            'time': time,
            'get_tax_name': self.get_tax_name,
            'get_total_vat':self.get_total_vat,
            'get_add_inv':self.get_add_inv,
            'get_add_ship':self.get_add_ship,
            'get_inq':self.get_inq,
            })
        self.context = context.copy()


    def get_tax_name(self, invoice_id):
        invoice_obj = self.pool.get('account.invoice')
        for inv in invoice_obj.browse(self.cr, self.uid, [invoice_id.id]):
            vat = inv.invoice_line[self.index].invoice_line_tax_id[0].amount
            percent = (vat * 100) or 0.0
            self.index += 1
        return percent

    def get_inq(self,origin):
        sale_ids = self.pool.get('sale.order').search(self.cr,self.uid,[('name','=',origin)])
        sale_obj = self.pool.get('sale.order').browse(self.cr,self.uid,sale_ids[0])
        order_date = sale_obj.date_order
        return order_date


    def get_add_inv(self, origin):
        sale_ids = self.pool.get('sale.order').search(self.cr,self.uid,[('name','=',origin)])
        sale_obj = self.pool.get('sale.order').browse(self.cr,self.uid,sale_ids[0])
        partner_invoice_id = sale_obj.partner_invoice_id
        return partner_invoice_id

    def get_add_ship(self, origin):
        sale_ids = self.pool.get('sale.order').search(self.cr,self.uid,[('name','=',origin)])
        sale_obj = self.pool.get('sale.order').browse(self.cr,self.uid,sale_ids[0])
        partner_shipping_id = sale_obj.partner_shipping_id
        return partner_shipping_id

    def get_total_vat(self,untax_amt,total_amt):
        final_vat_amt = total_amt - untax_amt
        return final_vat_amt

report_sxw.report_sxw(
    'report.account.invoice.extend',
    'account.invoice',
    'account_inv_custom_report/report/account_inv_custom.rml',
    parser=account_invoice, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

