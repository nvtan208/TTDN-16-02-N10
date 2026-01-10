# -*- coding: utf-8 -*-
{
    'name': "Tính lương",

    'summary': """
        Module quản lý tính lương nhân viên""",

    'description': """
        Module quản lý tính lương nhân viên với các chức năng:
        - Ghi nhận lương cơ bản cho nhân viên (mặc định 5 triệu)
        - Nhập thưởng và phạt
        - Tính toán lương tự động theo công thức: Số công = (Lương cơ bản / 26) + Thưởng - Phạt
        - Quản lý lương theo tháng (định dạng YYYY-MM)
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['base', 'nhan_su'],

    'data': [
        'security/ir.model.access.csv',
        'views/tinh_luong.xml',
        'views/menu.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}
