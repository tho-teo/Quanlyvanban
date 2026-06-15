from django.urls import path
from . import views

urlpatterns = [
    path('cong_viec_cho_xu_ly/', views.cong_viec_cho_xu_ly, name='cong_viec_cho_xu_ly'),
    path('xu_ly_cong_viec/<int:ma_cv>/', views.xu_ly_cong_viec, name='xu_ly_cong_viec'),
    path('cong_viec_dang_xu_ly/', views.cong_viec_dang_xu_ly, name='cong_viec_dang_xu_ly'),
    path('cong_viec_da_hoan_thanh/', views.cong_viec_da_hoan_thanh, name='cong_viec_da_hoan_thanh'),
    path('cong_viec/<int:ma_cv>/', views.cong_viec_detail, name='cong_viec_detail'),
    path('cong_viec_da_hoan_thanh_detail/<int:ma_cv>/', views.cong_viec_da_hoan_thanh_detail, name='cong_viec_da_hoan_thanh_detail'),
    path('nhan_cong_viec/<int:ma_cv>/', views.nhan_cong_viec, name='nhan_cong_viec'),
]

