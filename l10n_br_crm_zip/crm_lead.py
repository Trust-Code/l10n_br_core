# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2010-2012  Renato Lima (Akretion)                             #
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

from openerp import models,fields,api,exceptions,_
import requests

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.one
    def zip_search(self):
        if not self.zip:
           if not self.street:
              raise exceptions.Warning(_('Please type in at least 3 letters of the Street Name for search'))

           if len(self.street) < 3:
              raise exceptions.Warning(_('Please type in at least 3 letters of the Street Name for search'))

           if not self.country_id:
              raise exceptions.Warning(_('Choose a Country'))

           if not self.state_id:
              raise exceptions.Warning(_('Choose a State'))

           if not self.l10n_br_city_id:
              raise exceptions.Warning(_('Choose a City'))

           get_url_viacep = 'http://viacep.com.br/ws/' + self.state_id.code + '/' + self.l10n_br_city_id.name + '/' + self.street + '/json'
           obj_viacep = requests.get(get_url_viacep)
           data_viacep = obj_viacep.json()

           # Write data to the database
           for res in data_viacep:
               Zip_search = self.env['l10n_br.zip'].search([('name','=',res['cep'])])
               if len(Zip_search) == 0:
                  # Locate Country Code
                  Country = self.env['res.country']
                  cod_pais = Country.search([('name','=','Brasil')])

                  # Locate State Code
                  State = self.env['res.country.state']
                  cod_estado = State.search([('code','=',res['uf'])])

                  # Locate City
                  City = self.env['l10n_br_base.city']
                  City.filtered
                  cod_cidade = City.search(['&',('name','=',res['localidade']),('state_id','=',cod_estado.id)])

                  # Append this Zip code info to the Zip table
                  Zip_table = self.env['l10n_br.zip'].create({'name': res['cep'],
                                                              'street': res['logradouro'],
                                                              'district': res['bairro'],
                                                              'complement': res['complemento'],
                                                              'country_id': cod_pais.id,
                                                              'state_id': cod_estado.id,
                                                              'l10n_br_city_id': cod_cidade.id})

           if len(data_viacep) == 1:

              # Locate Country Code
              Country = self.env['res.country']
              cod_pais = Country.search([('name','=','Brasil')])

              # Locate State Code
              State = self.env['res.country.state']
              cod_estado = State.search([('code','=',res['uf'])])

              # Locate City
              City = self.env['l10n_br_base.city']
              City.filtered
              cod_cidade = City.search(['&',('name','=',res['localidade']),('state_id','=',cod_estado.id)])

              # Only 1 ZIP Code found, populating data
              self.write({'zip': data_viacep[0]['cep'],
                          'street': data_viacep[0]['logradouro'],
                          'district': data_viacep[0]['bairro'],
                          'country_id': cod_pais.id,
                          'state_id': cod_estado.id,
                          'l10n_br_city_id': cod_cidade.id})

           elif len(data_viacep) > 1:

              # Alert the user to specify street better
              raise exceptions.Warning(_('Please specify the street name better, we are getting too much results !'))
  
           return True

        else:

           # Search the ZIP Table for the given code
           Zip_search = self.env['l10n_br.zip'].search([('name','=',self.zip)])
           if len(Zip_search) == 0:
              get_url_viacep = 'http://viacep.com.br/ws/' + self.zip + '/json'
              obj_viacep = requests.get(get_url_viacep)
              data_viacep = obj_viacep.json()

              # Ignore if error returned
              if ("erro" in data_viacep):

                 # Write data to self object
                 self.write({'street': '',
                             'district': '',
                             'country_id': False,
                             'state_id': False,
                             'l10n_br_city_id': False})

              else:

                 # Locate Country Code
                 Country = self.env['res.country']
                 cod_pais = Country.search([('name','=','Brasil')])

                 # Locate State Code
                 State = self.env['res.country.state']
                 cod_estado = State.search([('code','=',data_viacep['uf'])])

                 # Locate City
                 City = self.env['l10n_br_base.city']
                 City.filtered
                 cod_cidade = City.search(['&',('name','=',data_viacep['localidade']),('state_id','=',cod_estado.id)])

                 # Write data to self object
                 self.write({'street': data_viacep['logradouro'],
                             'district': data_viacep['bairro'],
                             'country_id': cod_pais.id,
                             'state_id': cod_estado.id,
                             'l10n_br_city_id': cod_cidade.id})

                 # Append this Zip code info to the Zip table
                 Zip_table = self.env['l10n_br.zip'].create({'name': self.zip,
                                                             'street': data_viacep['logradouro'],
                                                             'district': data_viacep['bairro'],
                                                             'complement': data_viacep['complemento'],
                                                             'country_id': cod_pais.id,
                                                             'state_id': cod_estado.id,
                                                             'l10n_br_city_id': cod_cidade.id})

           else:
              if len(Zip_search) > 1:
                 raise exceptions.Warning(_('Please type in ZIP Code entirely, we are getting too much results!'))

              else:

                 # Write data to self object
                 self.write({'street': Zip_search.street,
                             'district': Zip_search.district,
                             'country_id': Zip_search.country_id.id,
                             'state_id': Zip_search.state_id.id,
                             'l10n_br_city_id': Zip_search.l10n_br_city_id.id})

        return True

