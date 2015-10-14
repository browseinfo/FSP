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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import time

from openerp.report import report_sxw

class received_products_wizard(osv.osv_memory):
    _name = "received.products.wizard"
    _columns={
        'shipment_id': fields.many2one('stock.picking','Shipment No.',domain="[('type','=','in')]"),
        'serial_id': fields.many2one('stock.production.lot','Serial No.'),
        'document_id': fields.many2one('purchase.order','Document No.'),
        'partner_id': fields.many2one('res.partner','Partner Name.'),
    }
    def onchange_shipment_id(self, cr, uid, ids, shipment_id,context=None):
        if shipment_id:
            stock_pool = self.pool.get('stock.move')
            stock_id = stock_pool.search(cr, uid, [('picking_id','=',shipment_id)])[0]
            stock_pool_browse = stock_pool.browse(cr, uid, stock_id, context=context)
            res = {'partner_id':stock_pool_browse.partner_id.id,
                   'serial_id':stock_pool_browse.prodlot_id.id,
                   }
            purchase_id = self.pool.get('purchase.order').search(cr, uid, [('name','=',stock_pool_browse.origin)], context=context)
            if purchase_id:
                res.update({'document_id':purchase_id[0]})

            return {'value':res}
        else:
            return {'value':{}}
    def get_values(self, cr, uid, ids, context=None):
        if isinstance(ids,(list)):
            ids = ids[0]
        domain = []
    	wizard = self.browse(cr, uid, ids, context=context)
        document_name = wizard.document_id and wizard.document_id.name or ''
        shipment_id = wizard.shipment_id and wizard.shipment_id.id or False
        partner_id = wizard.partner_id and wizard.partner_id.id or False
        serial_id = wizard.serial_id and wizard.serial_id.id
        domain.append(('state','=','assigned'))
        if shipment_id:
            domain.append(('picking_id','=',shipment_id))
        if partner_id:
            domain.append(('partner_id','=',partner_id))
        if wizard.document_id:
            domain.append(('origin','=',document_name))
        if wizard.serial_id:
            domain.append(('prodlot_id','=', serial_id))
        return {
            'name': _('Stock Move'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
    	return True
class delivered_products_wizard(osv.osv_memory):
    _name = "delivered.products.wizard"
    _columns={
        'shipment_id': fields.many2one('stock.picking','Shipment No.',domain="[('type','=','out')]"),
        'serial_id': fields.many2one('stock.production.lot','Serial No.'),
        'document_id': fields.many2one('sale.order','Document No.'),
        'partner_id': fields.many2one('res.partner','Partner Name.'),
    }
    def onchange_shipment_id(self, cr, uid, ids, shipment_id,context=None):
        if shipment_id:
            stock_pool = self.pool.get('stock.move')
            stock_id = stock_pool.search(cr, uid, [('picking_id','=',shipment_id)])[0]
            stock_pool_browse = stock_pool.browse(cr, uid, stock_id, context=context)
            res = {'partner_id':stock_pool_browse.partner_id.id,
                   'serial_id':stock_pool_browse.prodlot_id.id,
                   }
            sale_id = self.pool.get('sale.order').search(cr, uid, [('name','=',stock_pool_browse.origin)], context=context)
            if sale_id:
                res.update({'document_id':sale_id[0]})
            return {'value':res}
        else:
            return {'value':{}}

    def get_values(self, cr, uid, ids, context=None):
        if isinstance(ids,(list)):
            ids = ids[0]
        domain = []
        wizard = self.browse(cr, uid, ids, context=context)
        document_name = wizard.document_id and wizard.document_id.name or ''
        shipment_id = wizard.shipment_id and wizard.shipment_id.id or False
        partner_id = wizard.partner_id and wizard.partner_id.id or False
        serial_id = wizard.serial_id and wizard.serial_id.id
        domain.append(('state','=','confirmed'))
        if shipment_id:
            domain.append(('picking_id','=',shipment_id))
        if partner_id:
            domain.append(('partner_id','=',partner_id))
        if wizard.document_id:
            domain.append(('origin','=',document_name))
        if wizard.serial_id:
            domain.append(('prodlot_id','=', serial_id))
        return {
            'name': _('Stock Move'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return True

