from django.contrib import admin
from .models import VanBanDi

@admin.register(VanBanDi)
class VanBanDiAdmin(admin.ModelAdmin):
    list_display = ("so_van_ban", "ngay_tao", "trang_thai", "nguoi_lap", "van_ban_den_lien_quan")
    search_fields = ("so_van_ban",)