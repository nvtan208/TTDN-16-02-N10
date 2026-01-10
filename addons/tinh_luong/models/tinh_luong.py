# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class TinhLuong(models.Model):
    _name = 'tinh_luong'
    _description = 'Bảng tính lương nhân viên'
    _rec_name = 'thang'
    _order = 'thang desc'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True, ondelete='cascade')
    thang = fields.Date("Tháng", required=True, help="Chọn bất kỳ ngày trong tháng; hệ thống sẽ tự động chuẩn hóa về ngày 1 của tháng")
    
    # Lương cơ bản - lấy từ nhân viên tại thời điểm tính lương
    luong_co_ban = fields.Float("Lương cơ bản", related='nhan_vien_id.luong_co_ban', readonly=True)
    
    # Trạng thái tính lương
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_chot', 'Đã chốt'),
    ], string='Trạng thái', default='nhap', required=True)
    
    # Các thành phần lương
    thuong = fields.Float("Thưởng", default=0.0)
    phat = fields.Float("Phạt", default=0.0)
    # Lấy phụ cấp ăn/xăng trực tiếp từ nhân viên, không được sửa ở bảng lương
    an = fields.Float("Ăn trưa", related='nhan_vien_id.phu_cap_an', readonly=True, store=True)
    xang = fields.Float("Xăng xe", related='nhan_vien_id.phu_cap_xang', readonly=True, store=True)

    ot = fields.Float("Tổng OT", compute="_compute_thanh_toan", store=True, readonly=True)
    tru_muon = fields.Float("Tổng trừ muộn", compute="_compute_thanh_toan", store=True, readonly=True)
    tru_vesom = fields.Float("Tổng trừ về sớm", compute="_compute_thanh_toan", store=True, readonly=True)
    luong = fields.Float("Lương", compute="_compute_thanh_toan", store=True, readonly=True, help="Lương theo công: (Lương cơ bản / 26) × Số công")
    luong_gop = fields.Float("Lương gộp", compute="_compute_thanh_toan", store=True, readonly=True)
    bao_hiem = fields.Float("Bảo hiểm", compute="_compute_thanh_toan", store=True, readonly=True)
    tong = fields.Float("TỔNG", compute="_compute_thanh_toan", store=True, readonly=True)
    
    # Lương tính toán
    so_cong = fields.Float("Số công", compute="_compute_so_cong", store=True, readonly=True, digits=(16,6),
                           help="Số công = Tổng giờ làm trong tháng / 8 giờ/ngày (không làm tròn; giữ nguyên số thập phân)")
    
    tong_gio_lam = fields.Float("Tổng giờ làm", compute="_compute_tong_gio_lam", store=True, readonly=True,
                                help="Tính từ bảng chấm công")
    
    luong_cuoi_cung = fields.Float("Lương cuối cùng", compute="_compute_luong_cuoi_cung", store=True, readonly=True)
    
    ghi_chu = fields.Text("Ghi chú")

    # Không dùng SQL unique constraint để cho phép nhiều bản nháp,
    # nhưng ngăn tạo/chốt nếu đã có bản 'da_chot' cho cùng nhân viên+tháng

    @api.model
    def create(self, vals):
        """Ngăn tạo mới nếu đã tồn tại bản đã chốt cùng nhân viên và tháng"""
        nhan_vien = vals.get('nhan_vien_id')
        thang_val = vals.get('thang')
        # Normalize thang to first day of month if provided
        if thang_val:
            ngay = None
            if isinstance(thang_val, str):
                try:
                    ngay = datetime.strptime(thang_val, '%Y-%m-%d').date()
                except Exception:
                    ngay = None
            else:
                # likely a date object
                try:
                    ngay = thang_val
                except Exception:
                    ngay = None

            if ngay:
                ngay = ngay.replace(day=1)
                # store normalized date string back to vals so DB stores first day
                vals['thang'] = ngay.strftime('%Y-%m-%d')

        if nhan_vien and vals.get('thang'):
            try:
                ngay_check = datetime.strptime(vals.get('thang'), '%Y-%m-%d').date()
            except Exception:
                ngay_check = None
            if ngay_check:
                existed = self.search([('nhan_vien_id', '=', int(nhan_vien)), ('thang', '=', ngay_check), ('trang_thai', '=', 'da_chot')], limit=1)
                if existed:
                    raise ValidationError('Đã tồn tại bảng lương đã chốt cho nhân viên và tháng này. Không thể tạo mới.')
        return super().create(vals)

    def write(self, vals):
        """Không cho phép chỉnh sửa khi đã chốt lương.
        Nếu đang cố gắng đổi trạng thái sang 'da_chot', kiểm tra xem đã có bản 'da_chot' khác chưa.
        """
        # If updating thang, normalize it to first day of month
        if 'thang' in vals and vals.get('thang'):
            thang_val = vals.get('thang')
            ngay = None
            if isinstance(thang_val, str):
                try:
                    ngay = datetime.strptime(thang_val, '%Y-%m-%d').date()
                except Exception:
                    ngay = None
            else:
                ngay = thang_val
            if ngay:
                ngay = ngay.replace(day=1)
                vals['thang'] = ngay.strftime('%Y-%m-%d')

        for record in self:
            # Nếu bản này đã chốt thì không cho chỉnh sửa
            if record.trang_thai == 'da_chot':
                raise ValidationError("Không thể chỉnh sửa lương khi đã chốt! Vui lòng tạo bản ghi mới.")

            # Nếu update yêu cầu chuyển sang đã chốt, đảm bảo không có bản khác đã chốt
            if vals.get('trang_thai') == 'da_chot':
                # determine month to check: prefer updated vals thang else current record.thang
                thang_check = vals.get('thang') if vals.get('thang') else record.thang
                try:
                    if isinstance(thang_check, str):
                        thang_check_date = datetime.strptime(thang_check, '%Y-%m-%d').date()
                    else:
                        thang_check_date = thang_check
                except Exception:
                    thang_check_date = record.thang

                existed = self.search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('thang', '=', thang_check_date),
                    ('trang_thai', '=', 'da_chot'),
                    ('id', '!=', record.id),
                ], limit=1)
                if existed:
                    raise ValidationError('Đã tồn tại bản lương đã chốt cho nhân viên và tháng này. Không thể chốt thêm.')
        return super().write(vals)

    def action_chot_luong(self):
        """Chốt lương (đổi trạng thái từ nháp sang đã chốt)
        Trước khi chốt kiểm tra không có bản đã chốt khác cho cùng nhân viên+tháng.
        """
        for record in self:
            if record.trang_thai == 'nhap':
                existed = self.search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('thang', '=', record.thang),
                    ('trang_thai', '=', 'da_chot'),
                    ('id', '!=', record.id),
                ], limit=1)
                if existed:
                    raise ValidationError('Đã tồn tại bản lương đã chốt cho nhân viên và tháng này. Không thể chốt thêm.')
                record.trang_thai = 'da_chot'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.depends('nhan_vien_id', 'thang')
    def _compute_tong_gio_lam(self):
        """
        Tính tổng giờ làm trong tháng từ bảng chấm công
        """
        for record in self:
            if record.nhan_vien_id and record.thang:
                # Lấy ngày đầu tiên và ngày cuối cùng của tháng
                ngay_dau_thang = record.thang
                ngay_cuoi_thang = (record.thang + relativedelta(months=1)) - timedelta(days=1)
                
                # Tìm tất cả bản ghi chấm công trong tháng
                cham_cong_records = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay', '>=', ngay_dau_thang),
                    ('ngay', '<=', ngay_cuoi_thang)
                ])
                
                # Tính tổng giờ làm
                tong_gio = sum([cc.so_gio_lam for cc in cham_cong_records])
                record.tong_gio_lam = tong_gio
            else:
                record.tong_gio_lam = 0.0

    @api.depends('tong_gio_lam')
    def _compute_so_cong(self):
        """
        Tính số công từ tổng giờ làm
        Công thức: Số công = Tổng giờ làm / 8 giờ
        1 ngày làm đủ 8 tiếng = 1 công
        """
        for record in self:
            # 1 ngày làm đủ 8 tiếng = 1 công
            record.so_cong = record.tong_gio_lam / 8.0 if record.tong_gio_lam > 0 else 0.0

    @api.depends('nhan_vien_id', 'thang', 'thuong', 'phat', 'an', 'xang', 'tong_gio_lam', 'so_cong', 'luong_co_ban')
    def _compute_luong_cuoi_cung(self):
        """
        Cập nhật lương cuối cùng bằng công thức tổng hợp mới (TỔNG)
        """
        for record in self:
            # đảm bảo các giá trị chi tiết được tính
            record._compute_thanh_toan()
            record.luong_cuoi_cung = record.tong

    @api.depends('nhan_vien_id', 'thang', 'thuong', 'phat', 'an', 'xang', 'tong_gio_lam', 'so_cong', 'luong_co_ban')
    def _compute_thanh_toan(self):
        """Tính các thành phần: OT, trừ muộn/về sớm, lương, bảo hiểm và tổng"""
        for record in self:
            record.ot = 0.0
            record.tru_muon = 0.0
            record.tru_vesom = 0.0
            record.luong = 0.0
            record.luong_gop = 0.0
            record.bao_hiem = 0.0
            record.tong = 0.0

            if record.nhan_vien_id and record.thang:
                ngay_dau_thang = record.thang
                ngay_cuoi_thang = (record.thang + relativedelta(months=1)) - timedelta(days=1)

                cham_cong_records = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay', '>=', ngay_dau_thang),
                    ('ngay', '<=', ngay_cuoi_thang)
                ])

                # Tổng các khoản OT và trừ theo chấm công
                record.ot = sum([cc.ot_tien for cc in cham_cong_records])
                record.tru_muon = sum([cc.tru_muon for cc in cham_cong_records])
                record.tru_vesom = sum([cc.tru_vesom for cc in cham_cong_records])

                # Lương theo công: (lương cơ bản / 26) × số công
                if record.luong_co_ban:
                    record.luong = (record.luong_co_ban / 26.0) * record.so_cong

                # Lương gộp (bao gồm trừ về sớm)
                record.luong_gop = record.luong + record.thuong + record.ot + record.an + record.xang - record.tru_muon - record.tru_vesom - record.phat

                # Bảo hiểm theo lương cơ bản × (bhyt + bhxh + bhtn) / 100
                bhyt = record.nhan_vien_id.bhyt or 0.0
                bhxh = record.nhan_vien_id.bhxh or 0.0
                bhtn = record.nhan_vien_id.bhtn or 0.0
                record.bao_hiem = record.luong_co_ban * (bhyt + bhxh + bhtn) / 100.0

                # TỔNG
                record.tong = record.luong_gop - record.bao_hiem

    @api.constrains('thang')
    def _check_thang(self):
        """Không yêu cầu chọn ngày 1; cho phép chọn bất kỳ ngày trong tháng.
        Đây chỉ là ràng buộc tồn tại giá trị thang.
        """
        for record in self:
            if not record.thang:
                raise ValidationError("Vui lòng chọn tháng cần tính lương.")

    @api.constrains('thuong', 'phat')
    def _check_thuong_phat(self):
        """Kiểm tra thưởng và phạt không được âm"""
        for record in self:
            if record.thuong < 0:
                raise ValidationError("Thưởng không được âm!")
            if record.phat < 0:
                raise ValidationError("Phạt không được âm!")
