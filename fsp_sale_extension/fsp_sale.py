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
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc
from tools import ustr
import datetime
from openerp import tools
class sale_order(osv.Model):
    _inherit = 'sale.order'
    def _get_default_shop(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',company_id)], context=context)
        if not shop_ids:
            raise osv.except_osv(_('Error!'), _('There is no default shop for the current user\'s company!'))
        return shop_ids[0]
    _columns = {
        'purchase_fiscal_position': fields.many2one('account.fiscal.position', 'Purchase Fiscal Position'),
        'purchase_company_id': fields.many2one('res.company',string='Purchase Company'),
        'date_delivery': fields.date('Expected Delivery date'),
    }
    
    _defaults = {
        'shop_id': _get_default_shop,
    }
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        return {
            'name': line.name,
            'origin': order.name,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty)\
                    or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
            'procure_method': line.type,
            'move_id': move_id,
            'company_id': order.company_id.id,
            'note': line.name,
            'purchase_fiscal_position':order.purchase_fiscal_position and order.purchase_fiscal_position.id or False,
            'purchase_company_id':order.purchase_company_id and order.purchase_company_id.id or False,
            'shop_id':order.shop_id and order.shop_id.id or False,
        }
    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        partner_id = self.browse(cr, uid, ids[0], context=context).partner_id.id
        partner_pool = self.pool.get('res.partner')
        partner_pool._construct_constraint_msg(cr, uid, [partner_id], context=context)
        partner_pool.button_check_vat(cr, uid, [partner_id], context=context)
        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
#
#This method is for to take web-shop value to web-store in the customer Invoice
#
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'web_store': order.shop_id and order.shop_id.name or False
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

class procurement_order(osv.Model):
    _inherit = 'procurement.order'
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop',readonly='True'),
        'purchase_fiscal_position': fields.many2one('account.fiscal.position', 'Purchase Fiscal Position'),
        'purchase_company_id': fields.many2one('res.company',string='Purchase Company',readonly='True')
    }
    
    def _get_warehouse(self, procurement, user_company):
        """
            Return the warehouse containing the procurment stock location (or one of it ancestors)
            If none match, returns then first warehouse of the company
        """
        # TODO refactor the domain once we implement the "parent_of" domain operator
        # NOTE This method has been copied in the `purchase_requisition` module to ensure
        #      retro-compatibility. This code duplication will be deleted in next stable version.
        #      Do not forget to update both version in case of modification.
        company_id = (procurement.company_id or user_company).id
        domains = [
            [
                '&', ('company_id', '=', company_id),
                '|', '&', ('lot_stock_id.parent_left', '<', procurement.location_id.parent_left),
                          ('lot_stock_id.parent_right', '>', procurement.location_id.parent_right),
                     ('lot_stock_id', '=', procurement.location_id.id)
            ],
            [('company_id', '=', company_id)]
        ]

        cr, uid = procurement._cr, procurement._uid
        context = procurement._context
        Warehouse = self.pool['stock.warehouse']
        for domain in domains:
            ids = Warehouse.search(cr, uid, domain, context=context)
            if ids:
                return ids[0]
        return False
    
    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        res = {}
        if context is None:
            context = {}
        old_uid = uid
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        so_obj = self.pool.get('sale.order')
        so_line_obj = self.pool.get('sale.order.line')
        warehouse_obj = self.pool.get('stock.warehouse')
        for procurement in self.browse(cr, uid, ids, context=context):
            partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
            print "=====================ids==========",ids
            if procurement.purchase_company_id:
                uids = self.pool.get('res.users').search(cr, uid, [('company_id','=',procurement.purchase_company_id.id)])
                print "uidsdsdsd",uids
                if uids:
                    group_object = self.pool.get('res.groups')
                    group_id = group_object.search(cr, uid, [('name','=','Intercompany User')],context=context)[0]
                    for user in group_object.browse(cr, uid, group_id, context=context).users:
                        print 'user.id=',user.id
                        if user.id in uids:
                            uid = user.id
                            print "in condition uid=",uid
                            #break
                #if uids:
                #    uid = uids[0]
                res_id = procurement.move_id.id
                supplier_info_obj = self.pool.get('product.supplierinfo')
                supplier_info_ids = supplier_info_obj.search(cr, old_uid, [('product_id', '=', procurement.product_id.id),('company_id','=',procurement.purchase_company_id.id)], context=context)
                print "\n****supplier_info_ids=",supplier_info_ids
                if supplier_info_ids:
                    print "taken uid=",uid
                    partner_id = supplier_info_obj.read(cr, uid, supplier_info_ids[0], ['name'], context=context).get('name')[0]
                    partner = partner_obj.browse(cr, uid, partner_id, context=context)
                    print "***************partner.id=",partner.id,partner,partner_id
                    seller_qty = procurement.product_id.seller_qty
                    #partner_id = partner.id
                    address_id = partner_obj.address_get(cr, uid, [partner.id], ['delivery'])['delivery']
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    print "pricelist id===",pricelist_id
                    uom_id = procurement.product_id.uom_po_id.id

                    qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
                    if seller_qty:
                        qty = max(qty,seller_qty)

                    price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

                    schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
                    purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)

                    #Passing partner_id to context for purchase order line integrity of Line name
                    new_context = context.copy()
                    new_context.update({'lang': partner.lang, 'partner_id': partner_id})

                    product = prod_obj.browse(cr, uid, procurement.product_id.id, context=new_context)
                    taxes_ids = procurement.product_id.supplier_taxes_id
                    taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)
                    
                    name = product.partner_ref
                    if product.description_purchase:
                        name += '\n'+ product.description_purchase
                    name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
                    line_vals = {}
                    so_id = so_obj.search(cr, old_uid, [('name', '=', procurement.origin)])
                    print "so_idso_idso_id",so_id,procurement.origin
                    if so_id:
                        so_line_id = so_line_obj.search(cr, uid, [('order_id','=',so_id[0]),('product_id','=',procurement.product_id.id)],context=context)
                        serial = so_line_obj.browse(cr,uid,so_line_id[0],context=context).serial
                        so_lines = so_obj.browse(cr,uid,so_id[0],context=context).order_line
                        product_name = procurement.name
                        self.index = 1
                        for line in so_lines:
                            if ustr(line.name) == ustr(product_name):
                                fiscal_pos_tax_id = acc_pos_obj.browse(cr,uid,procurement.purchase_fiscal_position.id,context=context).tax_ids
                                for tax in fiscal_pos_tax_id:
                                    print "\n\nTAX============",tax,line.product_id.supplier_taxes_id
                                    if tax.tax_src_id.id == line.product_id.supplier_taxes_id[0].id:
                                        print tax.tax_src_id.id ,"==",line.product_id.supplier_taxes_id[0].id
                                        print "\n\nSOURCE NAME==",tax.tax_src_id.name,"DEST==",tax.tax_dest_id.id
                                        tax_id = [tax.tax_dest_id.id]
                                        print "\n\n\ntax_id=",tax_id
                                        line_vals.update({
                                            'product_id':line.product_id,
                                            'name': line.name,
                                            'serial':line.serial,
                                            'product_qty': qty,
                                            'product_id': procurement.product_id.id,
                                            'product_uom': uom_id,
                                            'price_unit': line.price_unit or 0.0,
                                            'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'move_dest_id': res_id,
                                            'taxes_id': [(6,0,tax_id)],
                                        })
                                        break
                                    else:
                                        tax_id = [line.product_id.supplier_taxes_id[0].id]
                                        print "\n\n\n else code tax_id=",tax_id
                                        line_vals.update({
                                            'product_id':line.product_id,
                                            'name': line.name,
                                            'serial':line.serial,
                                            'product_qty': qty,
                                            'product_id': procurement.product_id.id,
                                            'product_uom': uom_id,
                                            'price_unit': line.price_unit or 0.0,
                                            'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            'move_dest_id': res_id,
                                            'taxes_id': [(6,0,tax_id)],
                                        })
                        print "\n\nline_vals===========",line_vals
                        #name = seq_obj.get(cr, uid, 'purchase.order') or _('PO00: %s') % self.index
                        #self.index += 1
                        po_vals = {
                            'name': name,
                            'origin': procurement.origin,
                            'partner_id': partner_id,
                            'location_id': procurement.location_id.id,
                            'warehouse_id': self._get_warehouse(procurement, company),
                            'pricelist_id': pricelist_id,
                            'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            'order_line': [(0,0,line_vals)],
                            'company_id': procurement.purchase_company_id and procurement.purchase_company_id.id or False,
                            'fiscal_position':procurement.purchase_fiscal_position and procurement.purchase_fiscal_position.id or False,
                            'payment_term_id': partner.property_supplier_payment_term.id or False,
                            'invoice_method' : 'order',
                        }
                        print "\n\npo_vals=====",po_vals
                        res[procurement.id] = self.pool.get('purchase.order').create(cr, uid, po_vals, context=context)
                        #**********************************************************************************************
                        #...Following code is for those products of sale order which has type = service
                        #**********************************************************************************************
                        so_line_pool = self.pool.get('sale.order.line')
                        po_line_pool = self.pool.get('purchase.order.line')
                        sale_order_line_ids = so_line_pool.search(cr, uid, [('order_id', '=', so_id[0]),('serial','=',serial)], context=context)
                        print "sale_order_line_ids with serial=",serial, '====',sale_order_line_ids
                        for line_obj in so_line_pool.browse(cr, uid, sale_order_line_ids, context=context):
                            #if line_obj.product_id.type != 'service':
                                #serial = line_obj.serial
                            if line_obj.product_id.type == 'service' and line_obj.product_id.id not in [line.product_id.id for line in self.pool.get('purchase.order').browse(cr, uid, res[procurement.id], context=context).order_line]:
                                fiscal_pos_tax_id = acc_pos_obj.browse(cr,uid,procurement.purchase_fiscal_position.id,context=context).tax_ids
                                for tax in fiscal_pos_tax_id:
                                    print tax.tax_src_id.id, '==',   line_obj.product_id.supplier_taxes_id[0].id
                                    if tax.tax_src_id.id == line_obj.product_id.supplier_taxes_id[0].id:
                                        tax_id = [tax.tax_dest_id.id]
                                        break
                                    else:
                                        tax_id = [line_obj.product_id.supplier_taxes_id[0].id]
                                create_vals = {
                                        'product_id':line_obj.product_id.id,
                                        'name':line_obj.product_id.name,
                                        'serial':line_obj.serial,
                                        'product_qty':1,
                                        'price_unit':0.0,
                                        'product_uom':line_obj.product_uom.id,
                                        'order_id':res[procurement.id],
                                        'date_planned':str(datetime.datetime.today().date()),
                                        'taxes_id':[(6,0,tax_id)]
                                        }
                                line_id = po_line_pool.create(cr, uid, create_vals, context=context)
                        #**************************end code for above comment******************************************                        
                        self.write(cr, uid, [procurement.id], {'state': 'running', 'purchase_id': res[procurement.id]})
                        self.message_post(cr, uid, ids, body=_("Draft Purchase Order created"), context=context)
            else:
                print "\n\n\nELSE############################"
                so_id = so_obj.search(cr, old_uid, [('name', '=', procurement.origin)])
                print "so_idso_idso_id",so_id,procurement.origin
                serial = ''
                if so_id:
                    so_line_id = so_line_obj.search(cr, uid, [('order_id','=',so_id[0]),('product_id','=',procurement.product_id.id)],context=context)
                    serial = so_line_obj.browse(cr,uid,so_line_id[0],context=context).serial
                res_id = procurement.move_id.id
                partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
                seller_qty = procurement.product_id.seller_qty
                partner_id = partner.id
                address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                pricelist_id = partner.property_product_pricelist_purchase.id
                warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', procurement.company_id.id or company.id)], context=context)
                uom_id = procurement.product_id.uom_po_id.id

                qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
                if seller_qty:
                    qty = max(qty,seller_qty)

                price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

                schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
                purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)

                #Passing partner_id to context for purchase order line integrity of Line name
                new_context = context.copy()
                new_context.update({'lang': partner.lang, 'partner_id': partner_id})

                product = prod_obj.browse(cr, uid, procurement.product_id.id, context=new_context)
                taxes_ids = procurement.product_id.supplier_taxes_id
                taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)

                name = product.partner_ref
                if product.description_purchase:
                    name += '\n'+ product.description_purchase
                line_vals = {
                    'name': name,
                    'product_qty': qty,
                    'product_id': procurement.product_id.id,
                    'serial':serial,
                    'product_uom': uom_id,
                    'price_unit': price or 0.0,
                    'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'move_dest_id': res_id,
                    'taxes_id': [(6,0,taxes)],
                }
                name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
                po_vals = {
                    'name': name,
                    'origin': procurement.origin,
                    'partner_id': partner_id,
                    'location_id': procurement.location_id.id,
                    'warehouse_id': warehouse_id and warehouse_id[0] or False,
                    'pricelist_id': pricelist_id,
                    'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'company_id': procurement.company_id.id,
                    'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                    'payment_term_id': partner.property_supplier_payment_term.id or False,
                }
                res[procurement.id] = self.create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=new_context)
                #**********************************************************************************************
                #...Following code is for those products of sale order which has type = service
                #**********************************************************************************************
                so_line_pool = self.pool.get('sale.order.line')
                po_line_pool = self.pool.get('purchase.order.line')
                sale_order_line_ids = so_line_pool.search(cr, uid, [('order_id', '=', so_id[0]),('serial','=',serial)], context=context)
                print "sale_order_line_ids with serial=",serial, '====',sale_order_line_ids
                for line_obj in so_line_pool.browse(cr, uid, sale_order_line_ids, context=context):
                    if line_obj.product_id.type == 'service' and line_obj.product_id.id not in [line.product_id.id for line in self.pool.get('purchase.order').browse(cr, uid, res[procurement.id], context=context).order_line]:
                        fiscal_pos_tax_id = acc_pos_obj.browse(cr,uid,procurement.purchase_fiscal_position.id,context=context).tax_ids
                        if fiscal_pos_tax_id:
                            for tax in fiscal_pos_tax_id:
                                print tax.tax_src_id.id, '==',   line_obj.product_id.supplier_taxes_id[0].id
                                if tax.tax_src_id.id == line_obj.product_id.supplier_taxes_id[0].id:
                                    tax_id = [tax.tax_dest_id.id]
                                    break
                                else:
                                    tax_id = [line_obj.product_id.supplier_taxes_id[0].id]
                                    print "tax_id",tax_id
                        else:
                            tax_id = [line_obj.product_id.supplier_taxes_id[0].id]
                        create_vals = {
                                'product_id':line_obj.product_id.id,
                                'name':line_obj.product_id.name,
                                'serial':line_obj.serial,
                                'product_qty':1,
                                'price_unit':0.0,
                                'product_uom':line_obj.product_uom.id,
                                'order_id':res[procurement.id],
                                'date_planned':str(datetime.datetime.today().date()),
                                'taxes_id':[(6,0,tax_id)]
                                }
                        line_id = po_line_pool.create(cr, uid, create_vals, context=context)
                #**************************end code for above comment******************************************
                self.write(cr, uid, [procurement.id], {'state': 'running', 'purchase_id': res[procurement.id]})
                self.message_post(cr, uid, ids, body=_("Draft Purchase Order created"), context=context)
        print "============res=======",res
        return res

    def _product_virtual_get(self, cr, uid, order_point):
        procurement = order_point.procurement_id
        if procurement and procurement.state != 'exception' and procurement.purchase_id and procurement.purchase_id.state in ('draft', 'confirmed'):
            return None
        return super(procurement_order, self)._product_virtual_get(cr, uid, order_point)

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def action_invoice_create(self, cr, uid, ids, context=None):
        print "\n\n\n ***********************in invoice create method"
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        print "\n\n\n\n\n\n\n\n\n\n\n\n\n context=",context
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        property_obj = self.pool.get('ir.property')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        #uids = self.pool.get('res.users').search(cr, uid, [('company_id','=',order_line.order_id.company_id.id)])
        #group_object = self.pool.get('res.groups')
        #group_id = group_object.search(cr, uid, [('name','=','Intercompany User')],context=context)[0]
        #for user in group_object.browse(cr, uid, group_id, context=context).users:
        #    if user.id in uids:
        #        uid = user.id
        #        break
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            uids = self.pool.get('res.users').search(cr, uid, [('company_id','=',order.company_id.id)])
            if uids:
                uid=uids[0]
#            if order.company_id.id != uid_company_id:
                #if the company of the document is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
            context['force_company'] = order.company_id.id
            order = self.browse(cr, uid, order.id, context=context)
#            pay_acc_id = order.partner_id.property_account_payable.id
            property_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',order.company_id.id), ('res_id', '=', False)])
            pay_acc_id = property_obj.browse(cr, uid, property_id)[0].value_reference.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', order.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define purchase journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)

                po_line.write({'invoice_lines': [(4, inv_line_id)]}, context=context)

            # get invoice data and create invoice
            inv_data = {
                'name': order.partner_ref or order.name,
                'reference': order.partner_ref or order.name,
                'account_id': pay_acc_id,
                'type': 'in_invoice',
                'partner_id': order.partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, inv_lines)],
                'origin': order.name,
                'fiscal_position': order.fiscal_position.id or False,
                'payment_term': order.payment_term_id.id or False,
                'company_id': order.company_id.id,
            }
            print "\n\n\n inv_data=",inv_data
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]}, context=context)
            res = inv_id
        return res

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        print '_________order_line__________',order_line
        uids = self.pool.get('res.users').search(cr, uid, [('company_id','=',order_line.order_id.company_id.id)])
        group_object = self.pool.get('res.groups')
        group_id = group_object.search(cr, uid, [('name','=','Intercompany User')],context=context)[0]
        for user in group_object.browse(cr, uid, group_id, context=context).users:
            if user.id in uids:
                uid = user.id
                break
        #if uids:
        #    uid = uids[0]

        acc_pos_obj = self.pool.get('account.fiscal.position')
        print "\n\n in invoice line",order_line.taxes_id,order_line.order_id.fiscal_position,account_id,
        product_account_id = order_line.product_id.categ_id.property_account_expense_categ.id
        fiscal_pos_account_id = acc_pos_obj.browse(cr,uid,order_line.order_id.fiscal_position.id,context=context).account_ids
        print "\n\nfiscal_pos_account_id======",fiscal_pos_account_id
        account_dest_id = 0
        if fiscal_pos_account_id:
            for account in fiscal_pos_account_id:
                print "\n\naccount=======",account,account.account_src_id.id,"=",account_id
                if account.account_src_id.id == product_account_id:
                    account_dest_id = account.account_dest_id.id
        print "\n\naccount dest id=====",account_dest_id,"account_id",account_id
        return {
            'name': order_line.name,
            'account_id': account_dest_id or order_line.product_id.categ_id.property_account_expense_categ.id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
        }
class sale_shop(osv.Model):
    _inherit = 'sale.shop'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
                'image': fields.binary("Logo",help="This field holds the image used as Logo for the Shop, limited to 1024x1024px."),
                'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                        string="Medium-sized photo", type="binary", multi="_get_image",
                        store = {
                            'sale.shop': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                        },
                        help="Medium-sized photo of the employee. It is automatically "\
                             "resized as a 128x128px image, with aspect ratio preserved. "\
                             "Use this field in form views or some kanban views."),
                'image_small': fields.function(_get_image, fnct_inv=_set_image,
                        string="Smal-sized photo", type="binary", multi="_get_image",
                        store = {
                            'sale.shop': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                        },
                        help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
                }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
