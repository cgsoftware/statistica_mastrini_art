# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2009 Italian Community. 
#    All Rights Reserved
#    
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Mastrini Articoli',
    'version': '0.1',
    'category': 'Statistiche',
    'description': """Questo modulo calcola e stampa una statistica sulle movimentazioni degli articoli  """,
    'author': 'C & G Software sas',
    'website': 'http://www.cgsoftware.it',
    "depends" : ['jasper_reports','Reportistica','ItalianFiscalDocument'],
    "update_xml" :[ 'wizard/mastrini_view.xml', 'report.xml', 'security/ir.model.access.csv' ], #'security/ir.model.access.csv',
    "active": False,
    "installable": True
}
