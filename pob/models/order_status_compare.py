# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api,models,fields
from odoo.exceptions import UserError
from odoo.addons.pob.models import prestapi
from odoo.tools.translate import _
from odoo.addons.pob.models.prestapi import PrestaShopWebService, PrestaShopWebServiceDict, PrestaShopWebServiceError, PrestaShopAuthenticationError
import logging
_logger = logging.getLogger(__name__)

class OrderStatusCompare(models.TransientModel):
    _name="order.status.compare"

    name = fields.Char("Name",invisible='1')
    date_to = fields.Date(string="To")
    date_from = fields.Date(string="From")
    range_to = fields.Integer(
    string='To', default = ''
    )
    range_from = fields.Integer(
    string='From', default = ''
    )
    specific_order = fields.Char(string='Specific Order')
    instance_id = fields.Many2one(
        'connector.instance', string='Connector Instance', 
        default=lambda self: self.env['connector.instance'].search([],limit=1,order='id'))

    def get_specific_order(self):
        self.env['order.status.result'].search([]).unlink()
        if self.specific_order:
            order_name = self.specific_order
            mismatch = 'yes'
            odoo_invoiced = False
            odoo_delivered = False
            odoo_cancelled = False
            prestashp = False
            odoo_order_status = 'none'
            try:
                config_id = self.instance_id
                url = config_id.user
                key = config_id.pwd
                prestashop = PrestaShopWebServiceDict(url,key)
            except:
                return self.env['message.wizard'].genrated_message("Error in Connection")
            order_map = self.env['connector.order.mapping'].search([('odoo_order_id.name','=',order_name),('instance_id','=',config_id.id)])
            if order_map:
                if order_map.is_invoiced:
                    odoo_invoiced = True
                    odoo_order_status = 'invoiced'
                if order_map.is_shipped:
                    odoo_delivered = True
                    odoo_order_status = 'delivered'
                if odoo_invoiced and odoo_delivered:
                    odoo_order_status = 'both'
                if order_map.odoo_order_id.state == 'cancel':
                    odoo_cancelled=True
                    odoo_order_status = 'cancelled'
                if prestashop:
                    order_status_his = prestashop.get('order_histories',options={'display': '[id,id_order,id_order_state]','filter[id_order]':order_map.ecommerce_order_id})
                    self.create_order_status(order_status_his,odoo_order_status,order_map)
            return self.create_tree_view()
        else:
            return self.env['message.wizard'].genrated_message("Order name can't be blank!!")
            
    def get_all_order(self):
        self.env['order.status.result'].search([]).unlink()
        order_maps = self.env['connector.order.mapping'].search([('instance_id','=', self.instance_id.id)])
        prestashp = False
        try:
            config_id = self.instance_id
            url=config_id.user
            key=config_id.pwd
            prestashop = PrestaShopWebServiceDict(url,key)
        except:
            return self.env['message.wizard'].genrated_message("Error in Connection")
        for order_map in order_maps:
            mismatch = 'yes'
            odoo_invoiced = False
            odoo_delivered = False
            odoo_cancelled = False
            odoo_order_status = 'none'
            if order_map:
                if order_map.is_invoiced:
                    odoo_invoiced = True
                    odoo_order_status = 'invoiced'
                if order_map.is_shipped:
                    odoo_delivered = True
                    odoo_order_status = 'delivered'
                if odoo_invoiced and odoo_delivered:
                    odoo_order_status = 'both'
                if order_map.odoo_order_id.state == 'cancel':
                    odoo_cancelled=True
                    odoo_order_status = 'cancelled'
                if prestashop:
                    order_status_his = prestashop.get('order_histories',options={'display': '[id,id_order,id_order_state]','filter[id_order]':order_map.ecommerce_order_id})
                    self.create_order_status(order_status_his,odoo_order_status,order_map)
        return self.create_tree_view()
     

    def get_date_order(self):
        if not (self.date_from and self.date_to):
            return self.env['message.wizard'].genrated_message("Please Enter Date")
        self.env['order.status.result'].search([]).unlink()
        order_maps = self.env['connector.order.mapping'].search([('odoo_order_id.date_order','>',self.date_from),('odoo_order_id.date_order','<=',self.date_to),('instance_id','=',self.instance_id.id)])
        prestashp = False
        try:
            config_id = self.instance_id
            url=config_id.user
            key=config_id.pwd
            prestashop = PrestaShopWebServiceDict(url,key)
        except:
            return self.env['message.wizard'].genrated_message("Error in Connection")
        for order_map in order_maps:
            mismatch = 'yes'
            odoo_invoiced = False
            odoo_delivered = False
            odoo_cancelled = False
            odoo_order_status = 'none'
            if order_map:
                if order_map.is_invoiced:
                    odoo_invoiced = True
                    odoo_order_status = 'invoiced'
                if order_map.is_shipped:
                    odoo_delivered = True
                    odoo_order_status = 'delivered'
                if odoo_invoiced and odoo_delivered:
                    odoo_order_status = 'both'
                if order_map.odoo_order_id.state == 'cancel':
                    odoo_cancelled=True
                    odoo_order_status = 'cancelled'
                if prestashop:
                    order_status_his = prestashop.get('order_histories',options={'display': '[id,id_order,id_order_state]','filter[id_order]':order_map.ecommerce_order_id})
                    self.create_order_status(order_status_his,odoo_order_status,order_map)
        return self.create_tree_view()

    def get_range_order(self):
        if not (self.range_from and self.range_to):
            if self.range_to < self.range_from:
                return self.env['message.wizard'].genrated_message("Please Enter Sequence in increasing order!!!")
            return self.env['message.wizard'].genrated_message("Please Enter Sequence first!!!")
        self.env['order.status.result'].search([]).unlink()
        order_list = list(range(self.range_from,self.range_to+1,1))
        order_maps = self.env['connector.order.mapping'].search([('odoo_order_id.id','in',order_list),('instance_id','=',self.instance_id.id)])
        prestashp = False
        try:
            config_id = self.instance_id
            url=config_id.user
            key=config_id.pwd
            prestashop = PrestaShopWebServiceDict(url,key)
        except:
            return self.env['message.wizard'].genrated_message("Error in Connection")
        for order_map in order_maps:
            mismatch = 'yes'
            odoo_invoiced = False
            odoo_delivered = False
            odoo_cancelled = False
            odoo_order_status = 'none'
            if order_map:
                if order_map.odoo_order_id.is_invoiced:
                    odoo_invoiced = True
                    odoo_order_status = 'invoiced'
                if order_map.odoo_order_id.is_shipped:
                    odoo_delivered = True
                    odoo_order_status = 'delivered'
                if odoo_invoiced and odoo_delivered:
                    odoo_order_status = 'both'
                if order_map.odoo_order_id.state == 'cancel':
                    odoo_cancelled=True
                    odoo_order_status = 'cancelled'
                if prestashop:
                    order_status_his = prestashop.get('order_histories',options={'display': '[id,id_order,id_order_state]','filter[id_order]':order_map.ecommerce_order_id})
                    self.create_order_status(order_status_his,odoo_order_status,order_map)
        return self.create_tree_view()
                

    def create_order_status(self,order_status_his, odoo_order_status, order_map):
        presta_invoiced = False
        presta_delivered = False
        presta_cancelled = False
        presta_order_status = 'none'
        mismatch = 'yes'
        if isinstance(order_status_his['order_histories']['order_history'],dict):
            order_status_his['order_histories']['order_history'] = [order_status_his['order_histories']['order_history'],]
        for order_status in order_status_his['order_histories']['order_history']:
            if int(order_status['id_order_state']) in [4,5]:
                presta_delivered = True
                if presta_invoiced:
                    presta_order_status = 'both'
                else:
                    presta_order_status = 'delivered'
            if int(order_status['id_order_state']) in [2,12]:
                presta_invoiced = True
                if presta_delivered:
                    presta_order_status = 'both'
                else:
                    presta_order_status = 'invoiced'
            if int(order_status['id_order_state']) == 6:
                presta_cancelled = True
                presta_order_status = 'cancelled'
        if odoo_order_status == presta_order_status:
            mismatch = 'no'
        self.env['order.status.result'].create({'reference':order_map.name,
                                                        'erp_order':order_map.odoo_order_id.id,
                                                        'presta_order':order_map.ecommerce_order_id,
                                                        'presta_order_status':presta_order_status,
                                                        'odoo_order_status':odoo_order_status,
                                                        'mismatch':mismatch})
    def create_tree_view(self):
        view_ref = self.env['ir.model.data'].get_object_reference('pob', 'order_status_result_view_form')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': _('Order Status Result'),
                'res_model': 'order.status.result',
                'res_id': self._ids[0],
                'view_mode': 'tree',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
                }
    

class OrderStatusResult(models.Model):
    _name = "order.status.result"

    name = fields.Char(string="name")
    reference = fields.Char(string="Order Reference")
    erp_order = fields.Many2one('sale.order',string='Odoo Order')
    presta_order = fields.Char(string = 'Prestashop Order')
    presta_order_status = fields.Selection(selection=[('none',"None"),('invoiced','Invoiced'),('delivered','Delivered'),('cancelled','Cancelled'),('both','Invoiced & Delivered')],string='Prestashop Order Status',default='none')
    odoo_order_status = fields.Selection(selection=[('none',"None"),('invoiced','Invoiced'),('delivered','Delivered'),('cancelled','Cancelled'),('both','Invoiced & Delivered')],string='Odoo Order Status',
    default='none',
    )
    mismatch = fields.Selection(selection=[('no','No'),('yes','Yes')],string="Mismatch")

    def sync_presta_status(self):
        for rec in self:
            if rec.odoo_order_status == 'none':
                raise UserError("Status Can't be updated")
            if rec.odoo_order_status == 'invoiced' and not (rec.presta_order_status == 'invoiced') and not (rec.presta_order_status == 'both'):
                rec.erp_order.manual_prestashop_paid()

    def sync_odoo_status(self):
        pass