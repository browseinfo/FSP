# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today browseinfo (<http://browseinfo.in>)
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

from datetime import datetime, date
from lxml import etree
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task


class project(osv.osv):
    _inherit = "project.project"
    
    def _get_visibility_selection(self, cr, uid, context=None):
        """ Overriden in portal_project to offer more options """
        return [('public', 'All Users'),
                ('employees', 'Employees Only'),
                ('followers', 'Followers Only'),
                ('dtp','DTP'),
                ('fulfilment','Fulfilment')]
    _visibility_selection = lambda self, *args, **kwargs: self._get_visibility_selection(*args, **kwargs)
    _columns = {
               'privacy_visibility': fields.selection(_visibility_selection, 'Privacy / Visibility', required=True),
               }
