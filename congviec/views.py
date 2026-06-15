from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from model_share.models import CongViec, VanBanDen, UserProfile, Notification, YeuCauSua
from .forms import XuLyCongViecForm, CongViecFilterForm

# Hàm gửi thông báo

def send_notification(user, title, message):
    if user:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )

# Lọc công việc theo form

def filter_cong_viec(queryset, form):
    if form.is_valid():
        TuNgay = form.cleaned_data.get('TuNgay')
        DenNgay = form.cleaned_data.get('DenNgay')
        TieuDe = form.cleaned_data.get('TieuDe')
        TrangThai = form.cleaned_data.get('TrangThai', None)

        if TuNgay:
            queryset = queryset.filter(HanXuLy__gte=TuNgay)
        if DenNgay:
            queryset = queryset.filter(HanXuLy__lte=DenNgay)
        if TieuDe:
            queryset = queryset.filter(TieuDe__icontains=TieuDe)
        if TrangThai:
            queryset = queryset.filter(TrangThai=TrangThai)
    return queryset


# Công việc chờ xử lý

@login_required(login_url='/accounts/login/')
def cong_viec_cho_xu_ly(request):
    today = timezone.localdate()
    form = CongViecFilterForm(request.GET or None)

    cv_list = CongViec.objects.filter(
        TrangThai="Chờ xử lý"
    ).filter(
        Q(NguoiXuLyChinh=request.user) | Q(nguoi_phoi_hop__NguoiDung=request.user)
    ).distinct().order_by("HanXuLy")

    cv_list = filter_cong_viec(cv_list, form)

    for cv in cv_list:
        cv.nguoi_phoi_hop_list = cv.nguoi_phoi_hop.exclude(NguoiDung=cv.NguoiXuLyChinh).all()
        delta = (cv.HanXuLy - today).days
        cv.con_lai = delta
        cv.con_lai_abs = abs(delta)

    return render(request, "congviec/cong_viec_cho_xu_ly.html", {
        'cong_viec_list': cv_list,
        'form': form
    })


# Nhận công việc

@login_required(login_url='/accounts/login/')
def nhan_cong_viec(request, ma_cv):
    cv = get_object_or_404(CongViec, MaCV=ma_cv)
    if cv.MaVanBanDen and cv.MaVanBanDen.NguoiNhan == request.user:
        messages.warning(request, "Bạn chỉ có quyền xem công việc này, không thể nhận.")
        return redirect('cong_viec_cho_xu_ly')
    cv.TrangThai = "Đang xử lý"
    cv.save()

    if cv.MaVanBanDen and cv.MaVanBanDen.NguoiNhan:
        send_notification(
            user=cv.MaVanBanDen.NguoiNhan,
            title="Thông báo nhận công việc",
            message=f"{request.user.get_full_name()} đã nhận công việc: {cv.TieuDe}",
        )

    messages.success(request, "Bạn đã nhận công việc!")
    return redirect("cong_viec_cho_xu_ly")

# Xử lý công việc
@login_required(login_url='/accounts/login/')
def xu_ly_cong_viec(request, ma_cv):
    cv = get_object_or_404(CongViec, MaCV=ma_cv)
    vanban = cv.MaVanBanDen

    if vanban and vanban.user == request.user:
        messages.warning(request, "Bạn chỉ có quyền xem công việc này.")
        return render(request, 'congviec/xu_ly_cong_viec.html', {
            'cv': cv,
            'vanban': vanban,
            'read_only': True,
        })

    form = XuLyCongViecForm(request.POST or None, request.FILES or None, instance=cv)
    if request.method == 'POST' and form.is_valid():
        form.save()

        if request.FILES.get('FileDinhKem'):
            cv.TrangThai = 'Chờ phê duyệt'
            if vanban:
                vanban.TrangThai = 'Đang xử lý'
                vanban.save()
            if vanban and vanban.NguoiNhan:
                send_notification(
                    user=vanban.NguoiNhan,
                    title="Công việc chờ phê duyệt",
                    message=f"Công việc {cv.TieuDe} đã được cập nhật và cần phê duyệt.",
                )

            cv.save()
            messages.success(request, "Cập nhật thành công! Công việc đã chuyển sang trạng thái 'Chờ phê duyệt'.")
        else:
            messages.warning(request, "Bạn chưa đính kèm file. Mô tả đã được lưu.")

        return redirect('xu_ly_cong_viec', ma_cv=ma_cv)

    return render(request, 'congviec/xu_ly_cong_viec.html', {
        'cv': cv,
        'vanban': vanban,
        'form': form
    })


# Công việc đang xử lý

@login_required(login_url='/accounts/login/')
def cong_viec_dang_xu_ly(request):
    today = timezone.localdate()
    form = CongViecFilterForm(request.GET or None)

    cv_list = CongViec.objects.filter(
        TrangThai__in=["Đang xử lý", "Chờ phê duyệt", "Yêu cầu sửa"]
    ).filter(
        Q(NguoiXuLyChinh=request.user) | Q(nguoi_phoi_hop__NguoiDung=request.user)
    ).distinct().order_by("HanXuLy")

    cv_list = filter_cong_viec(cv_list, form)

    for cv in cv_list:
        cv.nguoi_phoi_hop_list = cv.nguoi_phoi_hop.exclude(NguoiDung=cv.NguoiXuLyChinh).all()
        delta = (cv.HanXuLy - today).days
        cv.con_lai = delta
        cv.con_lai_abs = abs(delta)

    return render(request, 'congviec/cong_viec_dang_xu_ly.html', {
        'cong_viec_dang_xu_ly': cv_list,
        'form': form
    })

# Chi tiết công việc

@login_required(login_url='/accounts/login/')
def cong_viec_detail(request, ma_cv):
    cv = get_object_or_404(CongViec, MaCV=ma_cv)
    vanban = cv.MaVanBanDen
    yeu_cau_sua = YeuCauSua.objects.filter(CongViecLienQuan=cv)
    return render(request, 'congviec/cong_viec_detail.html', {
        'cv': cv,
        'vanban': vanban,
        'yeu_cau_sua': yeu_cau_sua,
    })

# Công việc đã hoàn thành

@login_required(login_url='/accounts/login/')
def cong_viec_da_hoan_thanh(request):
    form = CongViecFilterForm(request.GET or None)

    cv_list = CongViec.objects.filter(
        TrangThai="Hoàn thành"
    ).filter(
        Q(NguoiXuLyChinh=request.user) | Q(nguoi_phoi_hop__NguoiDung=request.user)
    ).distinct().order_by("-HanXuLy")

    cv_list = filter_cong_viec(cv_list, form)

    for cv in cv_list:
        cv.nguoi_phoi_hop_list = cv.nguoi_phoi_hop.exclude(NguoiDung=cv.NguoiXuLyChinh).all()

    return render(request, 'congviec/cong_viec_da_hoan_thanh.html', {
        'cong_viec_da_hoan_thanh': cv_list,
        'form': form
    })

@login_required(login_url='/accounts/login/')
def cong_viec_da_hoan_thanh_detail(request, ma_cv):
    cv = get_object_or_404(CongViec, MaCV=ma_cv)
    vanban = cv.MaVanBanDen
    return render(request, 'congviec/cong_viec_da_hoan_thanh_detail.html', {
        'cv': cv,
        'vanban': vanban,
    })

# Profile người dùng
@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    cv_dang_xu_ly = CongViec.objects.filter(
        TrangThai__in=["Đang xử lý", "Yêu cầu sửa", "Chờ phê duyệt"]
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    cv_cho_xu_ly = CongViec.objects.filter(
        TrangThai="Chờ xử lý"
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    cv_hoan_thanh = CongViec.objects.filter(
        TrangThai="Hoàn thành"
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    return render(request, "profile.html", {
        "user": user,
        "cv_dang_xu_ly": cv_dang_xu_ly,
        "cv_cho_xu_ly": cv_cho_xu_ly,
        "cv_hoan_thanh": cv_hoan_thanh,
        "user_profile": user_profile,
        "profile": user_profile,
    })

# Thông báo

@login_required(login_url='/accounts/login/')
def mark_all_as_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    return redirect('thong_bao_list')

@login_required(login_url='/accounts/login/')
def thong_bao_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/thong_bao_list.html', {'notifications': notifications})
