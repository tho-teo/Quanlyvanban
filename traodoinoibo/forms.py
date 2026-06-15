from django import forms
from .models import TraoDoiNoiBo
from django.contrib.auth.models import User
from model_share.models import PhongBan, UserProfile

class SoanTinForm(forms.ModelForm):

    class Meta:
        model = TraoDoiNoiBo
        fields = ['TieuDe', 'NoiDung', 'FileDinhKem']

        widgets = {
            'TieuDe': forms.TextInput(attrs={'class': 'form-control'}),
            'NoiDung': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'FileDinhKem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




class TraoDoiFilterForm(forms.Form):
    TuNgay = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Từ Ngày"
    )
    DenNgay = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Đến Ngày"
    )
    TrangThai = forms.ChoiceField(
        required=False,
        choices=[
            ('', '--- Tất cả ---'),
            ('Đã gửi', 'Đã gửi'),
            ('Nháp', 'Nháp'),
            ('Đã xóa', 'Đã xóa'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Trạng Thái"
    )

    TieuDe = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề'}),
        label="Tiêu Đề"
    )

class TinNhapForm(forms.ModelForm):
    class Meta:
        model = TraoDoiNoiBo
        fields = ['NguoiNhan', 'TieuDe', 'NoiDung', 'FileDinhKem']
