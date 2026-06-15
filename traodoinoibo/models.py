from django.db import models
from django.contrib.auth.models import User
from model_share.models import PhongBan

class TraoDoiNoiBo(models.Model):
    MaTin = models.AutoField(primary_key=True)
    NguoiGui = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='tin_da_gui'
    )
    NguoiNhan = models.ManyToManyField(
        User, blank=True, related_name='tin_den'
    )
    DonViTrucThuoc = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True, blank=True)
    TieuDe = models.CharField(max_length=255)
    NoiDung = models.TextField()
    FileDinhKem = models.FileField(upload_to='uploads/', null=True, blank=True)
    ThoiGianGui = models.DateTimeField(auto_now_add=True)
    TrangThai = models.CharField(
        max_length=100,
        choices=[
            ('Đã gửi', 'Đã gửi'),
            ('Nháp', 'Nháp'),
            ('Đã xóa', 'Đã xóa')
        ],
        default='Nháp'
    )

    DaXoa = models.BooleanField(default=False)
    LaTinNhap= models.BooleanField(default=False)
    def __str__(self):
        nguoi_gui = self.NguoiGui.username if self.NguoiGui else "Không rõ"
        nguoi_nhan = self.NguoiNhan.username if self.NguoiNhan else "Không rõ"
        return f"{self.TieuDe} ({nguoi_gui} ➜ {nguoi_nhan})"
