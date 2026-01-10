# -*- coding: utf-8 -*-
{
    'name': "Chấm Công",

    'summary': """
        Module quản lý chấm công nhân viên""",

    'description': """
        Module quản lý chấm công nhân viên với các chức năng:
        - Ghi nhận thông tin chấm công (ngày, giờ vào, giờ ra)
        - Tính toán số giờ làm
        - Xác định trạng thái (có mặt, đi muộn, về sớm)
        - Cấu hình giờ chuẩn (8h-17h, nghỉ 12h-13h)
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['base', 'nhan_su'],

    'data': [
        'security/ir.model.access.csv',
        'views/cham_cong.xml',
        'views/menu.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}
