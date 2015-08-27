# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2012  Renato Lima (Akretion)                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from openerp import models,fields,api
import re

class L10n_brZip(models.Model):
    _name = 'l10n_br.zip'
    _description = u'CEPs'

    name       = fields.Char(string='ZIP Code', size=9, required=True)
    street     = fields.Char(string='Street', size=100)
    district   = fields.Char(string='District', size=72)
    complement = fields.Char(string='Complement', size=72)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id   = fields.Many2one('res.country.state', string='State', domain="[('country_id','=',country_id)]", required=True)
    l10n_br_city_id = fields.Many2one('l10n_br_base.city', string='City', domain="[('state_id','=',state_id)]", required=True)   

    @api.onchange('name')
    def onchange_mask_zip(self):
        if self.name:
            val = re.sub('[^0-9]', '', self.name)
            if len(val) == 8:
                zip = "%s-%s" % (val[0:5], val[5:8])
                self.name = zip

