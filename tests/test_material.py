from odoo import _
from odoo.tests import tagged, HttpCase, HOST
import odoo.tools

import json 

class TestMaterial(HttpCase):

    # biar gak ngulangin code, kita jadikan 1 function aja
    # DRY = Do not Repeat Your code 
    def go_http(self, url, method = 'get', data_json = "{}"):
        headers = {
            'Content-Type': 'application/json',
        }
        self.env['base'].flush()
        url = "http://%s:%s/%s" % (HOST, odoo.tools.config['http_port'], url)

        # coding ini jelek, harusnya mungkin bisa langsung pake .get(method=method) aja. 
        # nanti deh dicari, untuk sementara is ok
        if method == 'post':
            r = self.opener.post(url, data=data_json, headers=headers)
        elif method == 'put':
            r = self.opener.put(url, data=data_json, headers=headers)
        else:
            r = self.opener.get(url, data=data_json, headers=headers)

        return r

    #test untuk mengambil list seluruh material
    def test_material_list(self):
        r = self.go_http('/api/material')
        self.assertEqual(r.status_code, 200)
        list_material = r.json()
        print("list_material: ", list_material)

    #test untuk mengambil list 1 material by ID = 23
    def test_material_one(self):
        r = self.go_http('/api/material/23')
        self.assertEqual(r.status_code, 200)
        mat = r.json()
        print("material id 23: ", mat)


    # test untuk create new material 
    def test_material_create(self):
        #### yuk kita create material
        data = {
            'name': 'Test Material 01',
            'is_material': True,
            'material_code': 'T01',
            'material_type': 'fabric',
        }
        data_json = json.dumps(data)

        self.env['base'].flush()
        r = self.go_http('/api/material', 'post', data_json)

        self.assertEqual(r.status_code, 200)
        result = r.json().get('result')

        material_id = result.get('id')

        self.assertIsInstance(material_id, int, msg=_('Test create Material is failed'))
        print("new material id: ", material_id)

        #### yuk kita edit langsung 
        data = {
            'name': 'Test Material 01 - Updated',
        }
        data_json = json.dumps(data)
        r = self.go_http('/api/material/%s' % (material_id), 'put', data_json)
        self.assertEqual(r.status_code, 200)
        result = r.json().get('result')
        sukses = result.get('success') == True
        self.assertEqual(sukses, True)
        print("edit new material - succeeded")

        



