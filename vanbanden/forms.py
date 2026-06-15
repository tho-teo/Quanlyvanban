from django import forms
from model_share.models import YeuCauSua, CongViec, VanBanDen, PhongBan, UserProfile
from django.utils import timezone

class YeuCauSuaForm(forms.ModelForm):
    class Meta:
        model = YeuCauSua
        fields = ['TieuDe', 'NoiDung']
        labels = {
            'TieuDe': 'Tiêu đề yêu cầu',
            'NoiDung': 'Nội dung cần xử lý lại',
        }
        widgets = {
            'TieuDe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề yêu cầu'
            }),
            'NoiDung': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mô tả nội dung cần xử lý lại'
            }),
        }


class VanBanDenFilterForm(forms.Form):
    """Form lọc dùng cho các trang: Văn bản chờ xử lý, Tra cứu văn bản"""
    q = forms.CharField(
        label="Từ khóa tìm kiếm",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập trích yếu, số ký hiệu hoặc cơ quan ban hành...'
        })
    )
    tu_ngay = forms.DateField(
        label="Từ ngày",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    den_ngay = forms.DateField(
        label="Đến ngày",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    trang_thai = forms.ChoiceField(
        label="Trạng thái",
        required=False,
        choices=[('', 'Tất cả')] + list(VanBanDen.TRANG_THAI_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class PhanCongForm(forms.ModelForm):
    class Meta:
        model = CongViec
        fields = ['TieuDe', 'HanXuLy', 'TrangThai']
        widgets = {
            'HanXuLy': forms.DateInput(attrs={'type': 'date'}),
        }