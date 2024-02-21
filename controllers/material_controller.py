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
        material = request.env['product.template'].sudo().browse(material_id)
        if not material:
            return {'error': _('Material is not found')}

        #ini khusus jika ada edit vendor, maka akan diupdate seller_ids
        if 'buy_vendor_id' in data:
            if 'buy_price' not in data:
                return {'error': _('edit buy_vendor_id must with buy_price too')}
            
        if 'buy_price' in data:
            if 'buy_vendor_id' not in data:
                return {'error': _('edit buy_price must with buy_vendor_id too')}

        if 'buy_vendor_id' in data:
            buy_vendor_id = data.get('buy_vendor_id')
            buy_price = data.get('buy_price')

            data.pop('buy_vendor_id', None)
            data.pop('buy_price', None)

            vendor = request.env['res.partner'].sudo().browse(buy_vendor_id)
            if not vendor:
                return {'error': _('buy_vendor_id is not found')}
            
            if not material.seller_ids:
                data['seller_ids'] = [(0, 0, {'name': buy_vendor_id, 'price': buy_price})]

            else:
                material.seller_ids[0].sequence = 10 #gapapa hardcoded, yang penting bukan sequence = 0

                need_to_create = True
                for seller in material.seller_ids:
                    if seller.name.id == buy_vendor_id:
                        seller.sequence == 0
                        need_to_create = False

                if need_to_create:
                    data['seller_ids'] = [(0, 0, {'name': buy_vendor_id, 'price': buy_price, 'sequence': 0})]

        if material:
            material.sudo().write(data)
            # material.env.cr.commit()
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
        material = request.env['product.template'].sudo().browse(material_id)
        if material:
            material.update({
                'active': False,
            })
            return {'success': True}
        else:
            return {'error': 'Material is not found'}