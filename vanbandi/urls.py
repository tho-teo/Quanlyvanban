from django.urls import path
from . import views

urlpatterns = [
    path('', views.trang_chu, name='trang_chu'),
    path('lap_du_thao/', views.lap_du_thao, name='lap_du_thao'),
    path('van_ban_cho_ban_hanh/', views.van_ban_cho_ban_hanh, name='van_ban_cho_ban_hanh'),
    path('van_ban_ca_nhan/', views.van_ban_di_ca_nhan, name='van_ban_di_ca_nhan'),
    path('tra_cuu_van_ban_di/', views.tra_cuu_van_ban_di, name='tra_cuu_van_ban_di'),
    path('duyet/<int:pk>/', views.duyet_van_ban, name='duyet_van_ban'),
    path('yeu_cau_sua/<int:pk>/', views.yeu_cau_sua_vbdi, name='yeu_cau_sua_vbdi'),
    path('sua_van_ban/<int:pk>/', views.sua_van_ban_di, name='sua_van_ban_di'),
    path('vanbanden/', views.vanbanden_list, name='vanbanden_list'),
    path('vanbanden/create/', views.vanbanden_create, name='vanbanden_create'),
    path('vanbanden/<int:pk>/', views.vanbanden_detail, name='vanbanden_detail'),
]