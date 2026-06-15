from django.db import models
from django.contrib.auth.models import User
class PhongBan(models.Model):
    MaPB = models.AutoField(primary_key=True)
    TenPB = models.CharField(max_length=255, default="Chưa xác định")
    MoTa = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.TenPB


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phong_ban = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True)
    anh_dai_dien = models.ImageField(upload_to='anh_dai_dien/', blank=True)
    vai_tro = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username


class VanBanDen(models.Model):
    TRANG_THAI_CHOICES = [
        ("Đang xử lý", "Đang xử lý"),
        ("Chờ phê duyệt", "Chờ phê duyệt"),
        ("Chờ xử lý", "Chờ xử lý"),
    ]

    DO_KHAN_CHOICES = [
        ("Thường", "Thường"),
        ("Khẩn", "Khẩn"),
    ]

    DO_MAT_CHOICES = [
        ("Thường", "Thường"),
        ("Mật", "Mật"),
    ]
    MaVanBanDen = models.AutoField(primary_key=True)
    SoDen = models.IntegerField()
    NgayDen = models.DateField()
    SoKyHieu = models.CharField(max_length=255, unique=True)
    TrichYeu = models.CharField(max_length=255)
    CoQuanBanHanh = models.CharField(max_length=100)

    NguoiXuLyChinh = models.CharField(max_length=255, null=True, blank=True)
    NguoiXuLy = models.CharField(max_length=255, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    HanXuLy = models.DateField(null=True, blank=True)
    LoaiVanBan = models.CharField(max_length=100)
    TrangThai = models.CharField(max_length=100, choices=TRANG_THAI_CHOICES, default="Chờ xử lý")
    DoKhan = models.CharField(max_length=50, choices=DO_KHAN_CHOICES, default="Thường")
    DoMat = models.CharField(max_length=50, choices=DO_MAT_CHOICES, default="Thường")
    NguoiKy = models.CharField(max_length=255)
    NguoiDuyet = models.CharField(max_length=255)

    NgayBanHanh = models.DateField(null=True, blank=True)
    FileDinhKem = models.FileField(upload_to='vanbanden/', null=True, blank=True)
    NguoiNhan = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vanbanden_nhan"
    )
    van_ban_di_lien_quan = models.ForeignKey(
        'vanbandi.VanBanDi',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.SoKyHieu} - {self.TrichYeu}"


class CongViec(models.Model):
    TRANG_THAI_CHOICES = [
        ("Chờ xử lý", "Chờ xử lý"),
        ("Đang xử lý", "Đang xử lý"),
        ("Yêu cầu sửa", "Yêu cầu sửa"),
        ("Chờ phê duyệt", "Chờ phê duyệt"),
        ("Hoàn thành", "Hoàn thành"),
    ]
    MaCV = models.AutoField(primary_key=True)
    TieuDe = models.CharField(max_length=255)
    MoTa = models.CharField(max_length=255, null=True, blank=True)
    NgayNhan = models.DateField()
    HanXuLy = models.DateField()
    TrangThai = models.CharField(max_length=100, choices=TRANG_THAI_CHOICES, default="Chờ xử lý")
    FileDinhKem = models.FileField(upload_to="cong_viec/", null=True, blank=True)
    NgayHoanThanh = models.DateTimeField(null=True, blank=True)
    MaVanBanDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE)
    NguoiXuLyChinh = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.TieuDe


class NguoiXuLy(models.Model):
    CongViec = models.ForeignKey(CongViec, on_delete=models.CASCADE, related_name="nguoi_phoi_hop")
    NguoiDung = models.ForeignKey(User, on_delete=models.CASCADE)
    VaiTro = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.NguoiDung.username} - {self.CongViec.TieuDe}"


class YeuCauSua(models.Model):
    MaYeuCau = models.AutoField(primary_key=True)
    TieuDe = models.CharField(max_length=255)
    NoiDung = models.TextField()
    NgayTao = models.DateTimeField(auto_now_add=True)
    FileDinhKem = models.FileField(upload_to="yeu_cau_sua/", null=True, blank=True)
    NguoiYeuCau = models.ForeignKey(User, on_delete=models.CASCADE, related_name="yeu_cau_gui")
    CongViecLienQuan = models.ForeignKey('CongViec', on_delete=models.CASCADE)
    VanBanLienQuan = models.ForeignKey('VanBanDen', on_delete=models.CASCADE)

    def __str__(self):
        return f"Yêu cầu: {self.TieuDe}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    NOTI_TYPES = [
        ('duyet_van_ban', 'Duyệt văn bản đi'),
        ('phan_hoi_van_ban', 'Phản hồi văn bản đi'),
        ('van_ban_den', 'Văn bản đến'),
        ('cong_viec', 'Công việc'),
        ('trao_doi', 'Trao đổi nội bộ'),
    ]
    type = models.CharField(max_length=50, choices=NOTI_TYPES, default='cong_viec')
    related_id = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"{self.title} - {self.user.username}"