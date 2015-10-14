import sys
import re
import os.path
import getopt
import getpass
import sys, time, os.path, argparse
import atom
import atom.data, gdata.client
import gdata.docs.service
import gdata.docs.data
import gdata.docs.client
import gdata.spreadsheet.service
import time
from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import cStringIO
import Image
import base64
import urllib,urllib2


class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'

    def _GetFileExtension(self, file_name):
        """Returns the uppercase file extension for a file.

        Args:
        file_name: [string] The basename of a filename.

        Returns:
        A string containing the file extension of the file.
        """
        match = re.search('.*\.([a-zA-Z]{3,}$)', file_name)
        if file_name.split('.')[-1] == 'ai':
        	return 'AI'
        print "\n\n**** match",match,file_name
        if match:
            return match.group(1).upper()
        return False


    def connect_google(self, cr, uid, email, password, context=None):
        source = 'Document List Python Sample'
        try:
            self.client = gdata.docs.client.DocsClient()
            self.client.ClientLogin(email, password, source=source)
            self.client.ssl = True
            self.gd_client = gdata.docs.service.DocsService()
            self.gd_client.ClientLogin(email, password, source=source)
            self.gs_client = gdata.spreadsheet.service.SpreadsheetsService()
            self.gs_client.ClientLogin(email, password, source=source)
        except:
            raise osv.except_osv(_('Error!'),_("Authentication Failed..."))
        return True

    def create_attachment(self, cr, uid, ids,image_paths, context=None):
        print "image_path=",image_paths
        attachment_pool = self.pool.get('ir.attachment')
        attach_ids = []
        for image_path in image_paths:
		    image_path = image_path.replace(' ','%20').replace('(','%28').replace(')','%29')
		    image_name = image_path.split('/')[-1]
		    try:
		    	base64.encodestring(urllib2.urlopen(image_path).read())
		    except Exception, e:
	    		print "\n\n exception:",e
		    vals = {'name':image_name,
		            'res_model':'sale.order',
		            'type':'binary',
		            'res_id':ids,
		            'datafile_of':'artwork',
		            'datas_fname':image_name,
		            'datas':base64.encodestring(urllib2.urlopen(image_path).read())}
		    attach_id = attachment_pool.create(cr, uid, vals, context=context)
		    print "\n\n================attach_id==========",attach_id,uid
		    #self.pool.get('sale.order').write(cr, uid, ids,{'attachment_ids':[(6,0,int(attach_id))]} ,context=context)
		    attach_ids.append(attach_id)
        print 'attachment_ids',attach_ids
        #self.pool.get('sale.order').write(cr, uid, ids,{'attachment_ids':[(6,0,attach_ids)]} ,context=context)
        return attach_ids

    def make_gdirectory(self, cr, uid, order_name, context=None):
        """Prompts that creating directory in gdrive when no attachment."""
        print '\n\n\n\n****order name',order_name
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        email = user.gmail_user
        password = user.gmail_password
        self.connect_google(cr,uid,email,password,context=context)

        try:
			collection1 = gdata.docs.data.Resource(type='folder', title = order_name)
			collection1 = self.client.create_resource(collection1)
			subcollection1 = gdata.docs.data.Resource(type='folder', title = 'Artwork')
			subcollection1.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
			subcollection1 = self.client.create_resource(subcollection1, collection=collection1)
			subcollection2 = gdata.docs.data.Resource(type='folder', title = 'Shipping')
			subcollection2.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
			subcollection2 = self.client.create_resource(subcollection2, collection=collection1)
			subcollection3 = gdata.docs.data.Resource(type='folder', title = 'Invoicing')
			subcollection3.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
			subcollection3 = self.client.create_resource(subcollection3, collection=collection1)
        except Exception, e:
			print "\n exception================", e
			raise osv.except_osv(_('Error!'),_("Problems in creating Directory.Exception"))
			return True

        return True

    def upload_document(self, path, order_name):
        """Prompts that enable a user to upload a file to the Document List feed."""
        file_path = ''
        file_path = path
        entry = ''
        print '\n\n\n\n****file path',file_path,order_name
        try:
                collection1 = gdata.docs.data.Resource('folder', title = order_name)
                collection1 = self.client.create_resource(collection1)
                subcollection1 = gdata.docs.data.Resource('folder', title = 'Artwork')
                subcollection1.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
                subcollection1 = self.client.create_resource(subcollection1, collection=collection1)
                subcollection2 = gdata.docs.data.Resource('folder', title = 'Shipping')
                subcollection2.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
                subcollection2 = self.client.create_resource(subcollection2, collection=collection1)
                subcollection3 = gdata.docs.data.Resource('folder', title = 'Invoicing')
                subcollection3.AddCategory(gdata.docs.data.LABELS_NS, gdata.docs.data.LABELS_NS + "#" +gdata.docs.data.HIDDEN_LABEL, gdata.docs.data.HIDDEN_LABEL)
                subcollection3 = self.client.create_resource(subcollection3, collection=collection1)
        except Exception, e:
			raise osv.except_osv(_('Error!'),_("Problems in crating Directory.Exception is %s"))
			return True

        for f_path in file_path:
		    print "\n\nf_path",f_path
		    if not f_path:
		        return
		    elif not os.path.isfile(f_path):
		        print 'Not a valid file.'
		        return
		    file_name = os.path.basename(f_path)
		    print "\n\n****file name",file_name
		    ext = self._GetFileExtension(file_name)
		    print ext
		    SUPPORTED_FILETYPES = {'RAR':'application/x-rar-compressed','PSD':'application/octet-stream','INDD':'application/x-indesign','TIFF':'image/tiff','TIF':'image/tiff','EPS':'application/postscript','GIF':'image/gif','AI':'application/postscript','JPG':'image/jpeg', 'XLSX': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'DOCX': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'RTF': 'application/rtf', 'PPT': 'application/vnd.ms-powerpoint', 'ZIP': 'application/zip', 'DOC': 'application/msword', 'HTM': 'text/html', 'ODS': 'application/x-vnd.oasis.opendocument.spreadsheet', 'ODT': 'application/vnd.oasis.opendocument.text', 'TXT': 'text/plain', 'SWF': 'application/x-shockwave-flash', 'PPS': 'application/vnd.ms-powerpoint', 'HTML': 'text/html', 'TAB': 'text/tab-separated-values', 'SXW': 'application/vnd.sun.xml.writer', 'TSV': 'text/tab-separated-values', 'PDF': 'application/pdf', 'CSV': 'text/csv', 'XLS': 'application/vnd.ms-excel', 'PNG': 'image/png'}

		    if not ext or ext not in SUPPORTED_FILETYPES:
		        raise osv.except_osv(_('Error!'),_("File type not supported. Check the file extension"))
		        return
		    else:
		        content_type = SUPPORTED_FILETYPES[ext]
		        title = file_name
		        print title

		        try:
		            q = gdata.docs.service.DocumentQuery(categories=['folder'], params={'showfolders': 'true'})
		            q['title'] = 'Artwork'
		            q['title-exact'] = 'true'
		            feed = self.gd_client.Query(q.ToUri())
		            for entry in feed.entry:
    					if order_name in str(entry):
    					    ms = gdata.MediaSource(file_path=f_path, content_type=content_type)
    					    entry = entry.content.src.replace('folders','default')
    					    mm = self.gd_client.Upload(ms, title, folder_or_uri= entry + "/contents")

		          #  doc = gdata.docs.data.Resource(type = 'file', title = file_name)
		          #  media = gdata.data.MediaSource()
		          #  media.SetFileHandle(f_path, content_type)
		          #  create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI + '?convert=false'
		          #  entry = self.client.create_resource(doc, create_uri = create_uri, media = media)
		          #  self.client.move_resource(entry, collection = subcollection1, keep_in_collections = False)
		            #ms = gdata.MediaSource(file_path=file_path, content_type=content_type)
		        except IOError:
		            raise osv.except_osv(_('Error!'),_("Problems reading file. Check permissions."))
		            print 'Problems reading file. Check permissions.'
		            return True
		        if ext in ['CSV', 'ODS', 'XLS', 'XLSX']:
		            print 'Uploading spreadsheet...'
		        elif ext in ['PPT', 'PPS']:
		            print 'Uploading presentation...'
		        elif ext in ['PDF']:
		            print 'Uploading PDF..'
		        else:
		            print 'Uploading word processor document...'
		       # entry = self.gd_client.Upload(ms, title)
		        os.unlink(f_path)
		        if entry:
		            print 'Upload successful!'
		            print 'Document now accessible at:', entry.GetAlternateLink().href
		        else:
		            raise osv.except_osv(_('Error!'),_("Upload ERROR"))
		            print 'Upload error.'
        return True

    def upload_file_gdrive(self, path, order_name, fnames):
        file_path = ''
        file_path = path
        entry = ''
        print '\n\n\n\n****file path',file_path,order_name

        for f_path in file_path:
            print "\n\nf_path",f_path
            if not f_path:
                return
            elif not os.path.isfile(f_path):
                print 'Not a valid file.'
                return
            file_name = os.path.basename(f_path)
            print "\n\n****file name",file_name
            ext = self._GetFileExtension(file_name)
            print ext
            SUPPORTED_FILETYPES = {'RAR':'application/x-rar-compressed','PSD':'application/octet-stream','INDD':'application/x-indesign','TIFF':'image/tiff','TIF':'image/tiff','EPS':'application/postscript','GIF':'image/gif','AI':'application/postscript','JPG':'image/jpeg', 'XLSX': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'DOCX': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'RTF': 'application/rtf', 'PPT': 'application/vnd.ms-powerpoint', 'ZIP': 'application/zip', 'DOC': 'application/msword', 'HTM': 'text/html', 'ODS': 'application/x-vnd.oasis.opendocument.spreadsheet', 'ODT': 'application/vnd.oasis.opendocument.text', 'TXT': 'text/plain', 'SWF': 'application/x-shockwave-flash', 'PPS': 'application/vnd.ms-powerpoint', 'HTML': 'text/html', 'TAB': 'text/tab-separated-values', 'SXW': 'application/vnd.sun.xml.writer', 'TSV': 'text/tab-separated-values', 'PDF': 'application/pdf', 'CSV': 'text/csv', 'XLS': 'application/vnd.ms-excel', 'PNG': 'image/png'}

            if not ext or ext not in SUPPORTED_FILETYPES:
                raise osv.except_osv(_('Error!'),_("File type not supported. Check the file extension"))
                return
            else:
                content_type = SUPPORTED_FILETYPES[ext]
                title = file_name
                print title

                try:
                    q = gdata.docs.service.DocumentQuery(categories=['folder'], params={'showfolders': 'true'})
                    q['title'] = fnames
                    q['title-exact'] = 'true'
                    feed = self.gd_client.Query(q.ToUri())
                    for entry in feed.entry:
                        if order_name in str(entry):
                            ms = gdata.MediaSource(file_path=f_path, content_type=content_type)
                            entry = entry.content.src.replace('folders','default')
                            mm = self.gd_client.Upload(ms, title, folder_or_uri= entry + "/contents")

                except IOError:
                    raise osv.except_osv(_('Error!'),_("Problems reading file. Check permissions."))
                    print 'Problems reading file. Check permissions.'
                    return True
                if ext in ['CSV', 'ODS', 'XLS', 'XLSX']:
                    print 'Uploading spreadsheet...'
                elif ext in ['PPT', 'PPS']:
                    print 'Uploading presentation...'
                elif ext in ['PDF']:
                    print 'Uploading PDF..'
                else:
                    print 'Uploading word processor document...'
               # entry = self.gd_client.Upload(ms, title)
                os.unlink(f_path)
                if entry:
                    print 'Upload successful!'
                    print 'Document now accessible at:', entry.GetAlternateLink().href
                else:
                    raise osv.except_osv(_('Error!'),_("Upload ERROR"))
                    print 'Upload error.'
        return True

    def get_doc_file(self, cr, uid, attach_ids, fnames, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        email = user.gmail_user
        password = user.gmail_password
        print "\n attach id============", attach_ids, fnames
        self.connect_google(cr,uid,email,password,context=context)
        paths = []
        for ids in [attach_ids]:
            attachment = self.browse(cr, uid, ids ,context=context)
            print "\n\n\n****attachment",attachment
            print "\n\n\n****file name",attachment.datas_fname
            #path = os.path.abspath('filestore')
            path = "/srv/openerp_test/evan_store"
            print path
            files = base64.b64encode(attachment.datas)
            datas = (attachment.datas).decode('base64')
            fname = attachment.datas_fname
            target = open (path+'/'+fname, 'a')
#            print "\n targetttttttttttttttttttttttt", target
            target.write(datas)
            target.close()
            paths.append(path+'/'+fname)
        so_name = self.read(cr, uid, attach_ids, ['res_name'], context=context)[0].get('res_name')
        print "paths*****",paths
        print "\n so nameeeeeeeeeee", so_name
        self.upload_file_gdrive(paths, so_name, fnames)
        return True

    def get_document(self, cr, uid, attach_ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        email = user.gmail_user
        password = user.gmail_password
        self.connect_google(cr,uid,email,password,context=context)
        paths = []
        for ids in attach_ids:
		    attachment = self.browse(cr, uid, ids ,context=context)
		    print "\n\n\n****attachment",attachment
		    print "\n\n\n****file name",attachment.datas_fname
		    #path = os.path.abspath('filestore')
		    path = "/srv/openerp_test/evan_store"
		    print path
		    files = base64.b64encode(attachment.datas)
		    datas = (attachment.datas).decode('base64')
		    fname = attachment.datas_fname
		    target = open (path+'/'+fname, 'a')
		    print "\n targetttttttttttttttttttttttt", target
		    target.write(datas)
		    target.close()
		    paths.append(path+'/'+fname)
        so_name = self.read(cr, uid, attach_ids, ['res_name'], context=context)[0].get('res_name')
        print "paths*****",paths
        self.upload_document(paths, so_name)
        return True

    def create(self, cr, uid, vals, context=None):
        return super(ir_attachment, self).create(cr, uid, vals, context)
    _columns = {
        'url': fields.text('Url'),
        'file_upload' : fields.binary('File Upload'),
        'datafile_of':fields.char('File of'),
    }

class google_drive(osv.osv):
    _name = 'google.drive'

    def connect_google(self, cr, uid, email, password, context=None):
        source = 'Document List Python Sample'
        try:
            self.gd_client = gdata.docs.service.DocsService()
            self.gd_client.ClientLogin(email, password, source=source)
            self.gs_client = gdata.spreadsheet.service.SpreadsheetsService()
            self.gs_client.ClientLogin(email, password, source=source)
        except:
            raise osv.except_osv(_('Error!'),_("Authentication Failed..."))
        return True

    def add_into_attachment(self, cr, uid, ids, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        model = context.get('model',False)
        model_ids = context.get('model_ids',False)
        current_data = self.browse(cr, uid , ids, context=context)[0]
        for data in current_data.doc_lines:
            if data.select_doc:
                attachment_obj.create(cr,uid,{'name':data.name,'url':data.url,'type':'url','res_model':model,'res_id':model_ids[0]},context=context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _default_documents_id(self, cr, uid, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        email = user.gmail_user
        password = user.gmail_password
        self.connect_google(cr,uid,email,password,context=context)
        attach = self.pool.get('ir.attachment')
        feed = self.gd_client.GetDocumentListFeed()
        model = context.get('model',False)
        model_ids = context.get('model_ids',False)[0]
        list_return = []
        url_ids = attach.search(cr, uid , [('res_id','=',model_ids),('res_model','=',model),('type','=','url')],context=context)
        url_read = attach.read(cr, uid ,url_ids,['url','name'],context=context)
        list_url = []
        for url in url_read:
            list_url.append(url['url'])
        for entry in feed.entry:
            title = entry.title.text
            url = entry.GetAlternateLink().href
            resource_id = entry.resourceId.text
            if url not in list_url:
                list_return.append(({'name': title,'url':url}))
        return list_return

    def google_doc_get_action(self, cr, uid, res_model, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        action_model, action_id = tuple(mod_obj.get_object_reference(cr, uid,'google_drive', 'google_drive_action'))
        context.update({'model':res_model,'model_ids':ids})
        action = self.pool.get(action_model).read(cr, uid, action_id, context=context)
        action['context'] = context
        return action

    _columns = {
        'name' : fields.char('name',size=25),
        'doc_lines': fields.one2many('google.drive.doc', 'doc_id', 'Document Lines'),
    }
    _defaults = {
        'doc_lines' : _default_documents_id,
    }

class google_drive_doc(osv.osv):
    _name = 'google.drive.doc'
    _columns = {
        'name': fields.char('Title',size=256),
        'select_doc' : fields.boolean('Add / Remove'),
        'url': fields.char('URL',size=1024),
        'resource_id': fields.char('Resource ID',size=1024),
        'doc_id': fields.many2one('google.drive','google_drive')
    }


