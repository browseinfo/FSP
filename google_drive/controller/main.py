# -*- coding: utf-8 -*-

import ast
import base64
import csv
import glob
import itertools
import logging
import operator
import datetime
import hashlib
import os
import re
import simplejson
import time
import urllib
import urllib2
import urlparse
import xmlrpclib
import zlib
from xml.etree import ElementTree
from cStringIO import StringIO

import babel.messages.pofile
import werkzeug.utils
import werkzeug.wrappers
try:
    import xlwt
except ImportError:
    xlwt = None

import openerp
import openerp.modules.registry
from openerp.tools.translate import _
from openerp.tools import config

from openerp.addons.web import http
openerpweb = http



class Binarydata(openerpweb.Controller):
    _cp_path = "/google_drive/binarydata"


    @openerpweb.httprequest
    def upload_attachment_artwork(self, req, callback, model, id, ufile):
        Model = req.session.model('ir.attachment')
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        try:
            attachment_id = Model.create({
                'name': ufile.filename,
                'datas': base64.encodestring(ufile.read()),
                'datas_fname': ufile.filename,
                'res_model': model,
                'res_id': int(id),
                'datafile_of':'artwork',
            }, req.context)
            args = {
                'filename': ufile.filename,
                'id':  attachment_id
            }
        except xmlrpclib.Fault, e:
            args = {'error':e.faultCode }
        return out % (simplejson.dumps(callback), simplejson.dumps(args))

    @openerpweb.httprequest
    def upload_attachment_barcode(self, req, callback, model, id, ufile):
        Model = req.session.model('ir.attachment')
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        try:
            attachment_id = Model.create({
                'name': ufile.filename,
                'datas': base64.encodestring(ufile.read()),
                'datas_fname': ufile.filename,
                'res_model': model,
                'res_id': int(id),
                'datafile_of':'barcode',
            }, req.context)
            args = {
                'filename': ufile.filename,
                'id':  attachment_id
            }
        except xmlrpclib.Fault, e:
            args = {'error':e.faultCode }
        return out % (simplejson.dumps(callback), simplejson.dumps(args))


# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
