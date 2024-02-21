# -*- coding: utf-8 -*-
from odoo import _
from odoo import http
from odoo.http import Controller, route, request, Response
import json


"""
    karena tidak disebutkan apa auth-nya, untuk sementara kita buat public dulu semua ya.
    next, saya rekomendasikan pakai JWT-Auth.
    untuk berkomunikasi dengan frontend baik mobile app, maupun web, atau yang lain, biasanya paling umum digunakan.
"""
class MaterialController(http.Controller):
    # dipisah jadi 1 function sendiri aja, biar enggak mengulang code
    # DRY = Do not Repeat Your code.
    def get_material(self, domain):
        list_materials = request.env['product.template'].sudo().search_read(domain, fields=['name','material_code','material_type','buy_vendor_id','buy_price','buy_currency_id'])
        return list_materials


    # kita lupakan dulu pagination dll ya
    # hanya untuk kebutuhan test kerja saja
    @route(['/api/material'],
           type='json',
           auth='public',
           methods=['GET'])
    def do_material_all(self, **kw):
        list_materials = self.get_material([('is_material','=',True)])
        return list_materials
    
    @route(['/api/material/<int:material_id>'],
           type='json',
           auth='public',
           methods=['GET'],
           website=True,
           csrf=False)
    def do_material_one(self, material_id, **kw):
        list_materials = self.get_material([('id','=',material_id),('is_material','=',True)])
        if list_materials:
            mat = list_materials[0] #pasti hanya ada 1, kan search by ID
            return mat
        else:
            return {'error': _('Material is not found')}

    @route(['/api/material'],
           type='json',
           auth='public',
           methods=['POST'],
           csrf=False)
    def do_material_create(self, **kw):
        data = json.loads(request.httprequest.data)
        print("data form: ", data)

        material = request.env['product.template'].sudo().create(data)
        return {'id': material.id}

    @route(['/api/material/<int:material_id>'],
           type='json',
           auth='public',
           methods=['PUT'],
           csrf=False)    
    def do_material_update(self, material_id, **kw):
        data = json.loads(request.httprequest.data)
        partner = request.env['product.template'].sudo().browse(material_id)
        if partner:
            partner.write(data)
            return {'success': True}
        else:
            return {'error': 'Material is not found'}

    # demi keamanan, data tidak dihapus
    # cukup di archive saja
    @route(['/api/material/<int:material_id>'],
           type='json',
           auth='public',
           methods=['DELETE'],
           csrf=False)    
    def do_material_delete(self, material_id, **kw):
        partner = request.env['product.template'].sudo().browse(material_id)
        if partner:
            partner.update({
                'active': False,
            })
            return {'success': True}
        else:
            return {'error': 'Material is not found'}