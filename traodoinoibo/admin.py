from django.contrib import admin
from django.contrib.auth.models import User
from .models import TraoDoiNoiBo



@admin.register(TraoDoiNoiBo)
class TraoDoiNoiBoAdmin(admin.ModelAdmin):
    list_display = ("MaTin", "NguoiGui", "DonViTrucThuoc", "TieuDe", "NoiDung", "FileDinhKem", "ThoiGianGui","TrangThai")
    list_filter = ("TrangThai", "DonViTrucThuoc", "ThoiGianGui")
    search_fields = ("TieuDe", "NoiDung", "NguoiNhan", "NguoiGui")
    ordering = ('-ThoiGianGui',)

