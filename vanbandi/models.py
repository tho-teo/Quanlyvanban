from django.db import models
from django.contrib.auth.models import User
from model_share.models import VanBanDen

class VanBanDi(models.Model):
    TRANG_THAI_CHOICES = [
        ("Mới", "Mới (Draft)"),
        ("Chờ duyệt", "Chờ Cấp trên duyệt"),
        ("Đã ban hành", "Đã Ban hành"),
        ("Bị từ chối", "Bị Từ chối/Yêu cầu sửa"),
    ]
    trich_yeu = models.TextField(null=True, blank=True)
    han_xu_ly = models.DateField(null=True, blank=True)
    so_van_ban = models.CharField(max_length=50, unique=True)
    co_quan_ban_hanh = models.CharField(max_length=255, null=True, blank=True)
    ngay_tao = models.DateField(auto_now_add=True)
    loai_van_ban = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default="Mới")
    file_du_thao = models.FileField(upload_to='du_thao/', null=True, blank=True)
    file_lien_quan = models.FileField(upload_to='lien_quan/', null=True, blank=True)
    nguoi_lap = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='drafted_documents')
    nguoi_duyet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_outgoing_documents')
    nguoi_nhan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='received_outgoing_documents')
    van_ban_den_lien_quan = models.ForeignKey(
        VanBanDen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.so_van_ban