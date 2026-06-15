from django.urls import path
from . import views

urlpatterns = [
    path('soan_tin/', views.soan_tin, name='soan_tin'),
    path('tin_den/', views.tin_den, name='tin_den'),
    path('tin_da_gui/', views.tin_da_gui, name='tin_da_gui'),
    path('tin_den/<int:pk>/', views.tin_detail_tin_den, name='tin_detail_tin_den'),
    path('tin_da_gui/<int:pk>/', views.tin_detail_tin_da_gui, name='tin_detail_tin_da_gui'),
    path('tin_nhap/<int:pk>/', views.tin_detail_tin_nhap, name='tin_detail_tin_nhap'),
    path('tin_da_xoa/<int:pk>/', views.tin_detail_tin_da_xoa, name='tin_detail_tin_da_xoa'),
    path('tin_nhap/', views.tin_nhap, name='tin_nhap'),
    path('tin_da_xoa/', views.tin_da_xoa, name='tin_da_xoa'),
    path('tin_nhan/xoa/<int:MaTin>/', views.delete_message, name='xoa_tin'),
    path('tin_da_xoa/action/', views.action_tin_xoa, name='action_tin_xoa'),
    path('xoa_tin_da_gui/<int:MaTin>/', views.xoa_tin_da_gui, name='xoa_tin_da_gui'),
    path('xoa_tin_den/<int:MaTin>/', views.xoa_tin_den, name='xoa_tin_den'),
    path('xoa_tin_nhap/<int:MaTin>/', views.xoa_tin_nhap, name='xoa_tin_nhap'),
    path('gui_tin/<int:pk>/', views.gui_tin, name='gui_tin'),

]
