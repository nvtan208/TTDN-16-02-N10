# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Bảng chứa thông tin chấm công nhân viên'
    _rec_name = 'ngay'
    _order = 'ngay desc'

    # Cấu hình mặc định
    GIO_CHECKIN_CHUAN = 8.0  # 8h00
    GIO_CHECKOUT_CHUAN = 17.0  # 17h00
    GIO_NGHI_BAT_DAU = 12.0  # 12h00
    GIO_NGHI_KET_THUC = 13.0  # 13h00
    THOI_GIAN_NGHI = 1.0  # 1 giờ

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True, ondelete='cascade')
    ngay = fields.Date("Ngày chấm công", required=True, default=fields.Date.today)
    
    gio_vao = fields.Float("Giờ vào", required=True, help="Giờ vào (dạng decimal, ví dụ: 8.5 = 8h30)")
    gio_ra = fields.Float("Giờ ra", required=True, help="Giờ ra (dạng decimal, ví dụ: 17.5 = 17h30)")
    
    so_gio_lam = fields.Float("Số giờ làm", compute="_compute_so_gio_lam", store=True, readonly=True)
    trang_thai = fields.Selection([
        ('co_mat', 'Có mặt'),
        ('di_muon', 'Đi muộn'),
        ('ve_som', 'Về sớm'),
        ('di_muon_ve_som', 'Đi muộn & Về sớm'),
    ], string='Trạng thái', compute="_compute_trang_thai", store=True, readonly=True)
    
    ghi_chu = fields.Text("Ghi chú")
    
    # SQL Constraint để không cho phép duplicate
    _sql_constraints = [
        ('cham_cong_unique', 'unique(nhan_vien_id, ngay)', 'Nhân viên không thể chấm công 2 lần trong cùng 1 ngày!')
    ]
    
    # Thông tin chi tiết trạng thái
    di_muon = fields.Boolean("Đi muộn", compute="_compute_trang_thai", store=True)
    ve_som = fields.Boolean("Về sớm", compute="_compute_trang_thai", store=True)
    thoi_gian_di_muon = fields.Float("Thời gian đi muộn (phút)", compute="_compute_trang_thai", store=True)
    thoi_gian_ve_som = fields.Float("Thời gian về sớm (phút)", compute="_compute_trang_thai", store=True)
    
    # Tính OT và mức trừ/tiền thưởng theo quy tắc
    ot_gio = fields.Float("Giờ OT", compute="_compute_ot_va_tru", store=True, readonly=True)
    ot_tien = fields.Float("Tiền OT", compute="_compute_ot_va_tru", store=True, readonly=True)
    tru_muon = fields.Float("Tiền trừ đi muộn", compute="_compute_ot_va_tru", store=True, readonly=True)
    tru_vesom = fields.Float("Tiền trừ về sớm", compute="_compute_ot_va_tru", store=True, readonly=True) 

    @api.depends('gio_vao', 'gio_ra')
    def _compute_so_gio_lam(self):
        """Tính số giờ làm hiệu quả chỉ tính trong khoảng làm việc chính (8h-17h), trừ thời gian nghỉ trưa.
        Ví dụ: Làm 7:00-16:00 => chỉ tính 8:00-16:00 = 8h, trừ 1h nghỉ => 7h (<= 1 công)."""
        for record in self:
            if record.gio_vao and record.gio_ra:
                # Xác định phần giao nhau giữa thời gian làm và khoảng giờ chuẩn (8-17)
                start = max(record.gio_vao, self.GIO_CHECKIN_CHUAN)
                end = min(record.gio_ra, self.GIO_CHECKOUT_CHUAN)
                if end <= start:
                    record.so_gio_lam = 0.0
                    continue

                so_gio = end - start
                # Trừ giờ nghỉ trưa (nếu phần làm có giao nhau với giờ nghỉ)
                if start < self.GIO_NGHI_KET_THUC and end > self.GIO_NGHI_BAT_DAU:
                    so_gio -= self.THOI_GIAN_NGHI

                record.so_gio_lam = max(0.0, so_gio)
            else:
                record.so_gio_lam = 0.0

    @api.depends('gio_vao', 'gio_ra')
    def _compute_trang_thai(self):
        """Xác định trạng thái chấm công"""
        for record in self:
            di_muon = False
            ve_som = False
            thoi_gian_di_muon = 0.0
            thoi_gian_ve_som = 0.0
            
            if record.gio_vao and record.gio_ra:
                # Chuyển đổi giờ decimal sang phút để tính toán chính xác
                gio_vao_minute = self._gio_to_minute(record.gio_vao)
                gio_checkin_chuan_minute = self._gio_to_minute(self.GIO_CHECKIN_CHUAN)
                
                gio_ra_minute = self._gio_to_minute(record.gio_ra)
                gio_checkout_chuan_minute = self._gio_to_minute(self.GIO_CHECKOUT_CHUAN)
                
                # Kiểm tra đi muộn (vào sau 8h00)
                if gio_vao_minute > gio_checkin_chuan_minute:
                    di_muon = True
                    thoi_gian_di_muon = gio_vao_minute - gio_checkin_chuan_minute
                
                # Kiểm tra về sớm (ra trước 17h00)
                if gio_ra_minute < gio_checkout_chuan_minute:
                    ve_som = True
                    thoi_gian_ve_som = gio_checkout_chuan_minute - gio_ra_minute
                
                # Xác định trạng thái
                if di_muon and ve_som:
                    trang_thai = 'di_muon_ve_som'
                elif di_muon:
                    trang_thai = 'di_muon'
                elif ve_som:
                    trang_thai = 've_som'
                else:
                    trang_thai = 'co_mat'
            else:
                trang_thai = 'co_mat'
                di_muon = False
                ve_som = False
            
            record.trang_thai = trang_thai
            record.di_muon = di_muon
            record.ve_som = ve_som
            record.thoi_gian_di_muon = thoi_gian_di_muon
            record.thoi_gian_ve_som = thoi_gian_ve_som

    @api.depends('gio_vao', 'gio_ra', 'thoi_gian_di_muon', 'thoi_gian_ve_som')
    def _compute_ot_va_tru(self):
        """Tính giờ OT và tính tiền OT/trừ theo quy tắc:
           - Đi muộn: tính theo số giờ muộn × 50.000 VND/giờ
           - Về sớm: tính theo số giờ về sớm × 50.000 VND/giờ
           - Về sau 17h: tính OT theo giờ × 100.000 VND/giờ
           (Các giá trị có thể là số thập phân, tính theo phút/giờ)
        """
        for record in self:
            record.ot_gio = 0.0
            record.ot_tien = 0.0
            record.tru_muon = 0.0
            record.tru_vesom = 0.0
            if record.gio_vao and record.gio_ra:
                # OT: chỉ tính thời gian ra sau giờ chốt
                if record.gio_ra > self.GIO_CHECKOUT_CHUAN:
                    record.ot_gio = max(0.0, record.gio_ra - self.GIO_CHECKOUT_CHUAN)
                    record.ot_tien = record.ot_gio * 100000.0
                # Tính tiền trừ theo số giờ muộn / về sớm (thời gian đang lưu là phút)
                if record.thoi_gian_di_muon and record.thoi_gian_di_muon > 0:
                    hours = record.thoi_gian_di_muon / 60.0
                    record.tru_muon = hours * 50000.0
                if record.thoi_gian_ve_som and record.thoi_gian_ve_som > 0:
                    hours = record.thoi_gian_ve_som / 60.0
                    record.tru_vesom = hours * 50000.0

    def _gio_to_minute(self, gio_decimal):
        """Chuyển đổi giờ dạng decimal sang phút"""
        gio = int(gio_decimal)
        phut = int((gio_decimal - gio) * 60)
        return gio * 60 + phut

    @api.constrains('gio_vao', 'gio_ra')
    def _check_gio_vao_ra(self):
        """Kiểm tra giờ vào phải nhỏ hơn giờ ra"""
        for record in self:
            if record.gio_vao and record.gio_ra:
                if record.gio_vao >= record.gio_ra:
                    raise ValidationError("Giờ vào phải nhỏ hơn giờ ra!")
                
                # Kiểm tra giờ hợp lý (7h-20h)
                if record.gio_vao < 7 or record.gio_ra > 20:
                    raise ValidationError("Giờ chấm công phải trong khoảng 7h-20h!")
