from django import forms
from model_share.models import CongViec

class XuLyCongViecForm(forms.ModelForm):
    class Meta:
        model = CongViec
        fields = ['MoTa', 'FileDinhKem']
        widgets = {
            'MoTa': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập mô tả hoặc ghi chú khi xử lý công việc'
}),
        }
TRANG_THAI_CHOICES = [
    ('', 'Tất cả'),
    ('Đang xử lý', 'Đang xử lý'),
    ('Chờ phê duyệt', 'Chờ phê duyệt'),
    ('Hoàn thành', 'Hoàn thành'),
    ('Yêu cầu sửa',"Yêu cầu sửa")
]

class CongViecFilterForm(forms.Form):
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
        choices=TRANG_THAI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Trạng Thái"
    )

    TieuDe = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề công việc'}),
        label="Tiêu Đề"
    )
