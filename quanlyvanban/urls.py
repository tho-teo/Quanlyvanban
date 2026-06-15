from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from congviec import views
from django.contrib import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('congviec.urls')),
    path('',include('vanbanden.urls')),
    path('',include('vanbandi.urls')),
    path('',include('traodoinoibo.urls')),
    path("profile/", views.profile, name="profile"),
    path("accounts/", include(("django.contrib.auth.urls", "auth"), namespace="accounts")),
    path("accounts/password_reset/done/", auth.views.PasswordResetDoneView.as_view(), name="password_reset_done", ),
    path("accounts/reset/done/", auth.views.PasswordResetCompleteView.as_view(), name="password_reset_complete", ),
    path('thong_bao/', views.thong_bao_list, name='thong_bao_list'),
    path('thong_bao/mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)