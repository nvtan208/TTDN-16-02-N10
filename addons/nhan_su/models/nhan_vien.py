from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)

    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách lịch sử công tác")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    anh = fields.Binary("Ảnh")
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách chứng chỉ bằng cấp")
    so_nguoi_bang_tuoi = fields.Integer("Số người bằng tuổi", 
                                        compute="so_nguoi_bang_tuoi",
                                        store=True
                                        )
    luong_co_ban = fields.Float("Lương cơ bản", default=5000000.0, help="Lương cơ bản (VND), mặc định 5 triệu")
    phu_cap_an = fields.Float("Phụ cấp ăn trưa", default=0.0, help="Phụ cấp ăn trưa hàng tháng (VND)")
    phu_cap_xang = fields.Float("Phụ cấp xăng xe", default=0.0, help="Phụ cấp xăng xe hàng tháng (VND)")
    bhyt = fields.Float("BHYT (%)", default=1.5, help="Tỷ lệ BHYT (phần trăm)")
    bhxh = fields.Float("BHXH (%)", default=8.0, help="Tỷ lệ BHXH (phần trăm)")
    bhtn = fields.Float("BHTN (%)", default=1.0, help="Tỷ lệ BHTN (phần trăm)")
    
    @api.depends("tuoi")
    def _compute_so_nguoi_bang_tuoi(self):
        for record in self:
            if record.tuoi:
                records = self.env['nhan_vien'].search(
                    [
                        ('tuoi', '=', record.tuoi),
                        ('ma_dinh_danh', '!=', record.ma_dinh_danh)
                    ]
                )
                record.so_nguoi_bang_tuoi = len(records)
    _sql_constrains = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất')
    ]

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = record.ho_ten_dem + ' ' + record.ten
    
    
    
                
    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = ''.join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
    
    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                year_now = date.today().year
                record.tuoi = year_now - record.ngay_sinh.year

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Tuổi không được bé hơn 18")
