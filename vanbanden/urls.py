from django.urls import path
from . import views

urlpatterns = [
    path('van_ban_cho_xu_ly/', views.van_ban_cho_xu_ly, name='vanban_cho_xuly'),
    path('van_ban_cho_xu_ly/<int:vanban_id>/', views.vanban_detail, name='vanban_detail'),
    path('van_ban_cho_xu_ly/<int:pk>/phancong/new/', views.phan_cong_van_ban, name='phan_cong_van_ban'),
    path('van_ban_cho_xu_ly/<int:pk>/phancong/<int:cv_pk>/', views.phan_cong_lai, name='phan_cong_lai'),

    path('theo_doi_xu_ly/', views.theodoi_xuly, name='theodoi_xuly'),
    path('theo_doi_xu_ly/<int:pk>/duyet/', views.duyet_cong_viec, name='duyet_cong_viec'),
    path('yeu-cau-sua/<int:cong_viec_id>/', views.yeu_cau_sua_create, name='yeu_cau_sua_create'),
    path('tra_cuu_van_ban_den/', views.tracuu_vanbanden, name='tracuu_vanbanden'),
]
