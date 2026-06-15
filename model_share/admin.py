from django.contrib import admin
from django.contrib.auth.models import User
from model_share.models import CongViec, VanBanDen, PhongBan, UserProfile, NguoiXuLy,YeuCauSua

# Đổi tiêu đề, header, title của site mặc định
admin.site.site_title = "CHÀO"
admin.site.site_header = "QUẢN LÝ VĂN BẢN"
admin.site.index_title = "QUẢN LÝ VĂN BẢN"

# --- Đăng ký models ---
@admin.register(PhongBan)
class PhongBanAdmin(admin.ModelAdmin):
    list_display = ("MaPB", "TenPB", "MoTa")
    search_fields = ("TenPB",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phong_ban")
    search_fields = ("user__username", "phong_ban__TenPB")

@admin.register(VanBanDen)
class VanBanDenAdmin(admin.ModelAdmin):
    list_display = ("SoKyHieu", "TrichYeu", "SoDen", "NgayDen", "CoQuanBanHanh", "NguoiXuLyChinh", "HanXuLy", "TrangThai")
    list_filter = ("TrangThai", "LoaiVanBan", "DoKhan", "DoMat")
    search_fields = ("SoKyHieu", "TrichYeu", "CoQuanBanHanh")
@admin.register(CongViec)
class CongViecAdmin(admin.ModelAdmin):
    list_display = ("TieuDe", "NgayNhan", "TrangThai", "HanXuLy", "NguoiXuLyChinh")
    list_filter = ("TrangThai",)
    search_fields = ("TieuDe", "MoTa")

@admin.register(NguoiXuLy)
class NguoiXuLyAdmin(admin.ModelAdmin):
    list_display = ("CongViec", "NguoiDung", "VaiTro")
    search_fields = ("CongViec__TieuDe", "NguoiDung__username")

@admin.register(YeuCauSua)
class YeuCauSuaAdmin(admin.ModelAdmin):
    list_display = ("TieuDe", "NguoiYeuCau", "NgayTao", "CongViecLienQuan", "VanBanLienQuan")
    search_fields = ("TieuDe", "NoiDung", "NguoiYeuCau__username")
    list_filter = ("NgayTao",)
