# -*- coding: utf-8 -*-
##############################################################################
#
#    Browseinfo, Open Source Management Solution
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

{
    'name': 'Google Drive integration',
    'version': '0.2',
    'author': 'Browseinfo',
    'website': 'http://browseinfo.in',
    'category': 'Tools',
    'installable': True,
    'auto_install': False,
    'js': ['static/src/js/gdrive.js'],
    'qweb': ['static/src/xml/gdrive.xml'],
    'data': ['google_drive.xml'],
    'depends': ['google_base_account','document'],
    'description': """
Module to attach a google document from 
google drive to any model.
"""
}
