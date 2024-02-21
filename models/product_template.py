# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.http import Controller, route, request, Response
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    """
        constraint ini ada kelemahan, jika is_material == false, seharusnya tidak usah dicek. 
        tapi oleh odoo pasti akan tetap di-cek.
        but it's ok, tidak ada requirement itu dalam test kali ini. 
        siftatnya hanya nice to have aja.
    """
    _sql_constraints = [
        ('material_code_uniq', 'unique (material_code)', _('Material Code exists already')),
    ]

    """
        is_material = True jika ini adalah material. 
            Kenapa perlu field ini? karena kita akan menggunakan model product.template, sharing dengan master produk. Agar tidak terjadi rancu, agar mempermudah filter data, maka kita gunakan field is_material
        
        material_code = adalah kode material 
        material_type = adalah selection, tipe material [Fabric, Jeans, Cotton]
    """
    is_material = fields.Boolean(default=False)
    material_code = fields.Char()
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ])


    """
        Ini adalah 3 default field untuk membeli barang, yaitu:
            buy_vendor_id   = default vendor yang akan dibuatkan PO otomatis untuk membeli barang 
            buy_price       = default harga yang akan digunakan 
            buy_currency_id = default currency yang digunakan 

        3 data ini sebenarnya sudah disimpan di dalam self.seller_ids dengan posisi paling atas (prioritas nomor 1), tapi karena bentuknya adalah One2Many, maka kita keluarkan menjadi 3 field sendiri, agar bisa langsung ditampilkan di form milik Frontend dengan mudah.
    """
    buy_vendor_id = fields.Many2one(
        'res.partner', 'Default Vendor',
        help="Default Vendor of this product", compute="compute_default_vendor")
    buy_price = fields.Float(
        'Default Buy Price', default=0.0, digits='Product Price',
        help="The price to purchase a product", compute="compute_default_vendor")
    buy_currency_id = fields.Many2one(
        'res.currency', 'Default Buy Currency'
        , compute="compute_default_vendor")
    

    """
        Odoo sudah punya field sequence yang digunakan untuk mengambil default vendor berdasarkan priority-nya.
        sequence semakin kecil, maka semakin prioritas.
        artinya; default vendor = sequence terkecil
    """
    @api.depends("seller_ids")
    def compute_default_vendor(self):
        for rec in self:
            #kalau engggak dapat, yaudah, kosong
            if not rec.seller_ids:
                rec.buy_vendor_id = False
                rec.buy_price = False
                rec.buy_currency_id = False

                continue

            """
                Odoo sudah meng-order otomatis by sequence. lihat model: _name = "product.supplierinfo"
                jadi kita bisa langsung aja ambil index = 0
            """
            seller = rec.seller_ids[0]
            rec.buy_vendor_id = seller.name
            rec.buy_price = seller.price
            rec.buy_currency_id = seller.currency_id
