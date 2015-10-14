# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Browseinfo (<http://browseinfo.in>).
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
from openerp import tools
from openerp.osv import osv, fields



class mail_compose_message_task(osv.TransientModel):
    _inherit = 'mail.compose.message'
    _name = 'mail.compose.message.task'

    def __get_templates(self, cr, uid, context=None):
		res = super(mail_compose_message_task, self)._get_templates(cr, uid, context=context)
		if context is None:
			context = {}
		model = False
		email_template_obj = self.pool.get('email.template')
		message_id = context.get('default_parent_id', context.get('message_id', context.get('active_id')))

		if context.get('default_composition_mode') == 'reply' and message_id:
			message_data = self.pool.get('mail.message').browse(cr, uid, message_id, context=context)
			if message_data:
				model = 'project.task'
		else:
			model = 'project.task'

		record_ids = email_template_obj.search(cr, uid, [('model', '=', model)], context=context)
		return email_template_obj.name_get(cr, uid, record_ids, context) + [(False, '')]

    _columns = {
        'template_id': fields.selection(__get_templates, 'Use Template', size=-1),
        'project_id': fields.many2one('project.project', 'Use Project'),
		'user_id': fields.many2one('res.users'),
        'partner_ids': fields.many2many('res.partner',
            'mail_compose_message_res_partner_task_rel',
            'wizard_id', 'partner_id', 'Additional contacts'),
    }

    def send_mail(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            follower_ids = []
            for follow_id in self.pool.get(context.get('default_model')).browse(cr, uid, context.get('default_res_id'), context=context).message_follower_ids:
                follower_ids.append(follow_id.id)
            self.pool.get('project.task').create(cr, uid, {'name':wizard.record_name,
                                                           'project_id':wizard.project_id and wizard.project_id.id or False,
                                                           'user_id':wizard.user_id and wizard.user_id.id or False,
                                                           'message_follower_ids':[(6, 0, follower_ids)]
                                                          },context=context)
            body = 'Task for SO0'+str(context.get('default_res_id'))+' created'
            self.pool.get('sale.order').message_post(cr, uid, context.get('default_res_id'),body=body,context=context)
            if wizard.template_id:
                self.pool.get('email.template').write(cr, uid, wizard.template_id, {'user_id':wizard.user_id and wizard.user_id.id or False,'project_id': wizard.project_id and wizard.project_id.id or False },context=context) 
        return super(mail_compose_message_task, self).send_mail(cr, uid, ids, context=context)

    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
		res = super(mail_compose_message_task, self).onchange_template_id(cr, uid, ids, template_id, composition_mode, model, res_id, context)
		if template_id:
			for temp_obj in self.pool.get('email.template').browse(cr, uid, [template_id], context=context):
				res.get('value').update({'user_id': temp_obj.user_id and temp_obj.user_id.id or False,'project_id':temp_obj.project_id and temp_obj.project_id.id or False})
		return res

class email_template(osv.osv):
    _inherit = 'email.template'
    _columns = {
                'user_id': fields.many2one('res.users','Recipients'),
                'project_id': fields.many2one('project.project','Project'),
}

