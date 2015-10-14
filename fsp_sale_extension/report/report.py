# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright Browseinfo (<http://browseinfo.in>).
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
from openerp.osv import osv
from openerp import pooler
import base64
import urllib,urllib2
import barcode
import os
barcode.PROVIDED_BARCODES
['code39', 'ean', 'ean13', 'ean8', 'gs1', 'gtin', 'isbn', 'isbn10', 'isbn13', 'issn', 'jan', 'pzn', 'upc', 'upca']
[u'code39', u'code128', u'ean', u'ean13', u'ean8', u'gs1', u'gtin',u'isbn', u'isbn10', u'isbn13', u'issn', u'jan', u'pzn', u'upc', u'upca']
[u'code39', u'code128', u'ean', u'ean13', u'ean8', u'gs1', u'gtin', u'isbn', u'isbn10', u'isbn13', u'issn', u'jan', u'pzn', u'upc', u'upca']
EAN = barcode.get_barcode_class(u'code39')
from barcode.writer import ImageWriter

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        'time': time,
        'get_artwork':self._get_artwork,
        'get_barcode':self._get_barcode,
        })
    def _get_artwork(self, obj):
        attach = self.pool.get('ir.attachment')
        res = ''
        attach_ids = attach.search(self.cr, self.uid, [('res_id','=',obj.id),('res_name','=',obj.name)])
        if attach_ids:
            res = attach.browse(self.cr, self.uid, attach_ids[0]).db_datas
#        for line in obj.order_line:
#            if line.serial:
#                b = line.serial + '  ' + obj.name
#        ean = EAN(b, writer=ImageWriter())
#        fullname = ean.save(obj.name)
#        url =  str(os.path.abspath(fullname))
#        vals = {'name':'BC' + obj.name,
#                    'res_model':'purchase.order',
#                    'type':'binary',
#                    'res_id':obj.id,
#                    'datas_fname':'BC' + obj.name,
#                    'datas':base64.encodestring(open(url).read())
#                }
#        attach_id = attach.create(self.cr, self.uid, vals)
#        print "\n\n\n attach_id",attach_id
        return res
    def _get_barcode(self, obj):
        attach = self.pool.get('ir.attachment')
        b = ''
        for line in obj.order_line:
            if line.serial:
                b = line.serial + '  ' + obj.name
        ean = EAN(b, writer=ImageWriter())
        fullname = ean.save(obj.name)
        url =  str(os.path.abspath(fullname))
#        vals = {'name':'BC' + obj.name,
#                    'res_model':'purchase.order',
#                    'type':'binary',
#                    'res_id':obj.id,
#                    'datas_fname':'BC' + obj.name,
#                    'datas':base64.encodestring(open(url).read())
#                }
#        attach_id = attach.create(self.cr, self.uid, vals)
#        print "\n\n\n attachment id",attach_id
        return base64.encodestring(open(url).read())
report_sxw.report_sxw('report.purchase.quotation.fsp','purchase.order','addons/fsp_sale_extension/report/request_quotation.rml',parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

