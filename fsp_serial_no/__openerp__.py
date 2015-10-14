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

{
    'name': 'Serial No. for Sale Order/Purchase Order',
    'version': '1.1',
    'author': 'Browseinfo',
    'website': 'www.browseinfo.in',
	'category': 'sale',
	'description': """
	This module adds the field Serial No in the sale order line and purhase order line.
	""",
    'depends': [
        'sale',
        'purchase',
        'stock'
    ],
    'data': ['serial_view.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
