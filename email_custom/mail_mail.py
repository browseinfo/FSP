# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today browseinfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import base64
import logging
import re
from urllib import urlencode
from urlparse import urljoin

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(self, cr, uid, ids, auto_commit=False, recipient_ids=None, context=None):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param list recipient_ids: specific list of res.partner recipients.
                If set, one email is sent to each partner. Its is possible to
                tune the sent email through ``send_get_mail_body`` and ``send_get_mail_subject``.
                If not specified, one email is sent to mail_mail.email_to.
            :return: True
        """
        ir_mail_server = self.pool.get('ir.mail_server')
        for mail in self.browse(cr, uid, ids, context=context):
            try:
                # handle attachments
                attachments = []
                for attach in mail.attachment_ids:
                    attachments.append((attach.datas_fname, base64.b64decode(attach.datas)))
                # specific behavior to customize the send email for notified partners
                email_list = []
                if recipient_ids:
                    partner_obj = self.pool.get('res.partner')
                    existing_recipient_ids = partner_obj.exists(cr, SUPERUSER_ID, recipient_ids, context=context)
                    for partner in partner_obj.browse(cr, SUPERUSER_ID, existing_recipient_ids, context=context):
                        email_list.append(self.send_get_email_dict(cr, uid, mail, partner=partner, context=context))
                else:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, context=context))

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                send_to = ""
                if context.get('active_model') == 'purchase.order' or context.get('default_type') == 'out_invoice':
                    #send_to = ["TestEmailTomSupplier@gmail.com"]
                    e_list = email_list[0].copy()
                    em_to = e_list['email_to'][0].split('"')[1]
                    user_emailto = '"'+ str(em_to)+'"' + ' <TestEmailTomSupplier@gmail.com>'
                    e_list['email_to'] = [user_emailto]
                    email_list.append(e_list)
                if context.get('active_model') == 'sale.order' or context.get('default_type') == 'in_invoice':
                    #send_to = ["TestEmailTomCustomer@gmail.com"]
                    e_list = email_list[0].copy()
                    em_to = e_list['email_to'][0].split('"')[1]
                    user_emailto = '"'+ str(em_to)+'"' + ' <TestEmailTomCustomer@gmail.com>'
                    e_list['email_to'] = [user_emailto]
                    email_list.append(e_list)
                for email in email_list:
                    print "\n email email email email email to................", email.get('email_to')
                    msg = ir_mail_server.build_email(
                        email_from = mail.email_from,
                        email_to = email.get('email_to'),
                        subject = email.get('subject'),
                        body = email.get('body'),
                        body_alternative = email.get('body_alternative'),
                        email_cc = tools.email_split(mail.email_cc),
                        reply_to = email.get('reply_to'),
                        attachments = attachments,
                        message_id = mail.message_id,
                        references = mail.references,
                        object_id = mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype = 'html',
                        subtype_alternative = 'plain')
                    res = ir_mail_server.send_email(cr, uid, msg,
                        mail_server_id=mail.mail_server_id.id, context=context)
                    print "\n\n\n*****res",res
                if res:
                    mail.write({'state': 'sent', 'message_id': res})
                    mail_sent = True
                else:
                    mail.write({'state': 'exception'})
                    mail_sent = False

                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                if mail_sent:
                    self._postprocess_sent_message(cr, uid, mail, context=context)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                raise
            except Exception:
                _logger.exception('failed sending mail.mail %s', mail.id)
                mail.write({'state': 'exception'})

            if auto_commit == True:
                cr.commit()
        return True
