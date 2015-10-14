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
from openerp import netsvc
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    def set_to_draft(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'draft'})
        move_obj = self.pool.get('stock.move') 
        wf_service = netsvc.LocalService("workflow")
        move_ids = move_obj.search(cr, uid, [('picking_id', '=', ids)])
        for move_id in move_ids:
            move_obj.write(cr, uid, [move_id], {'state': 'draft'})
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        return True
    
stock_picking_out()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    def set_to_draft(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        move_obj = self.pool.get('stock.move') 
        move_ids = move_obj.search(cr, uid, [('picking_id', '=', ids)])
        for move_id in move_ids:
            move_obj.write(cr, uid, [move_id], {'state': 'draft'})
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        return True
    
stock_picking_in()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def set_to_draft(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        move_obj = self.pool.get('stock.move') 
        move_ids = move_obj.search(cr, uid, [('picking_id', '=', ids)])
        for move_id in move_ids:
            move_obj.write(cr, uid, [move_id], {'state': 'draft'})
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        return True
    
stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: