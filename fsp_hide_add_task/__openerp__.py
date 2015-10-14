# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Browseinfo (<http://www.browseinfo.in>).
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

{
    'name': 'Hide Add a Task Link',
    'version': '1.0',
    'category': 'mail',
    'summary': 'This Module will hide the Add a Task link',
    'description': """
This Module will hide the Add a Task link
===================================
If user has a rights of Portal then this module will hide that [Add a Task] link 
    """,
    'author': 'Browseinfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base', 'mail','sale'],
    'installable': True,
    'application': True,
    'js': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
