# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.bridge_skeleton.models.core.res_partner import _unescape

############## Override classes #################

class ProductProduct(models.Model):
    _inherit = 'product.product'


    @api.model
    def create_template_product_dict(self,vals):
        product_id =self.create(vals)
        temp = {'product_id':product_id.id, 'template_id' : product_id.product_tmpl_id.id}
        return temp
    
    
    
    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        instance_id = ctx.get('instance_id',[])
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        ecomm_id = vals.get('ecomm_id',0)
        product_obj = False
        if any(key in ctx for key in ecomm_cannels):
            vals = self.update_vals(vals, instance_id, True)
            first_product = self.check_first_product(vals , instance_id)
            if first_product['status']:
                product_obj = first_product['product_id']
        instance_obj = self.env['connector.instance'].browse(instance_id)
        if not product_obj:
            if instance_obj.is_reference and vals.get('default_code',False):
                product_obj = self.search([('default_code','=',vals.get('default_code'))],limit=1)
            if instance_obj.is_barcode and not product_obj and vals.get('barcode'):
                product_obj = self.search([('barcode','=',vals.get('barcode'))],limit=1)
            if product_obj:
                channel = "".join(list(set(ctx.keys())&set(ecomm_cannels))) or 'Ecommerce' + str(instance_id)
                self.env['connector.snippet'].create_odoo_connector_mapping('connector.product.mapping',
                                            ecomm_id,product_obj.id,
                                            instance_id,
                                            created_by=channel)
            else:
                product_obj = super(ProductProduct, self).create(vals)
        return product_obj

    
    @api.model
    def check_first_product(self, vals , instance_id):
        template_id = vals.get('product_tmpl_id', False)
        if template_id:
            template_id = self.env['product.template'].browse(int(template_id))
        connector_product = self.env['connector.product.mapping']
        connector_template = self.env['connector.template.mapping']
        status = False
        product_id = False
        if template_id and len(template_id.product_variant_ids.ids)==1 \
            and not template_id.product_variant_ids.product_template_attribute_value_ids:
            vals.pop('product_tmpl_id')
            product_id = template_id.product_variant_ids
            return_check = product_id.write(vals)
            if return_check:
                status = True
                mapping_id = connector_product.search([('name','=',product_id.id),
                                ('instance_id' ,'=' ,int(instance_id))],limit = 1)
                if mapping_id:
                    mapping_id.ecomm_combination_id = self._context.get('ecomm_combination_id', 0)
                    template_mapping = connector_template.search([('name','=',template_id.id),
                                ('instance_id' ,'=' ,int(instance_id))],limit = 1)
                    if template_mapping:
                        template_mapping.is_variants = True

        return{
            'status' : status,
            'product_id':product_id
        }
