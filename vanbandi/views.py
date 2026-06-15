from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from .models import VanBanDi
from model_share.models import VanBanDen, NguoiXuLy, CongViec, Notification

@login_required
def lap_du_thao(request):
    if request.method == "POST":
        so_van_ban = request.POST.get("so_van_ban")
        trich_yeu = request.POST.get("trich_yeu")
        co_quan_ban_hanh = request.POST.get("co_quan_ban_hanh")
        loai_van_ban = request.POST.get("loai_van_ban")
        file_du_thao = request.FILES.get("file_du_thao")
        file_lien_quan = request.FILES.get("file_lien_quan")
        nguoi_duyet_id = request.POST.get("nguoi_duyet")
        nguoi_nhan_id = request.POST.get("nguoi_nhan")
        han_xu_ly = request.POST.get("han_xu_ly")
        try:
            if not so_van_ban:
                raise ValueError("Chưa nhập Số văn bản")
            nguoi_duyet_user = None
            if nguoi_duyet_id:
                nguoi_duyet_user = User.objects.get(id=nguoi_duyet_id)

            nguoi_nhan_user = None
            if nguoi_nhan_id:
                nguoi_nhan_user = User.objects.get(id=nguoi_nhan_id)
            vbdi = VanBanDi.objects.create(
                so_van_ban=so_van_ban,
                trich_yeu=trich_yeu,
                han_xu_ly=han_xu_ly,
                co_quan_ban_hanh=co_quan_ban_hanh,
                loai_van_ban=loai_van_ban,
                file_du_thao=file_du_thao,
                file_lien_quan=file_lien_quan,
                ngay_tao=timezone.now().date(),
                nguoi_lap=request.user,
                nguoi_duyet=nguoi_duyet_user,
                nguoi_nhan=nguoi_nhan_user,
                trang_thai="Chờ duyệt"
            )
            if nguoi_duyet_user:
                Notification.objects.create(
                    user=nguoi_duyet_user,
                    title="Dự thảo mới cần duyệt",
                    message=f"{request.user.get_full_name()} đã trình dự thảo số {so_van_ban}. Vui lòng xem xét.",
                    type='duyet_van_ban')
            messages.success(request, f"Đã trình dự thảo thành công.")
            return redirect('lap_du_thao')

        except IntegrityError:
            messages.error(request, f"Lỗi! Số văn bản '{so_van_ban}' đã tồn tại.")
        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {e}")

    nguoi_xu_ly_list = User.objects.filter(is_active=True)
    return render(request, 'vanbandi/lap_du_thao.html', {
        'nguoi_xu_ly_list': nguoi_xu_ly_list
    })

@login_required
def sua_van_ban_di(request, pk):
    vbdi = get_object_or_404(VanBanDi, pk=pk)

    if vbdi.nguoi_lap != request.user:
        messages.error(request, "Bạn không có quyền sửa văn bản này.")
        return redirect('lap_du_thao')

    if vbdi.trang_thai not in ['Mới', 'Bị từ chối', 'Chờ duyệt']:
        messages.warning(request, "Văn bản đã ban hành không thể chỉnh sửa.")
        return redirect('lap_du_thao')

    if request.method == "POST":
        try:
            vbdi.so_van_ban = request.POST.get("so_van_ban")
            vbdi.trich_yeu = request.POST.get("trich_yeu")
            vbdi.co_quan_ban_hanh = request.POST.get("co_quan_ban_hanh")
            vbdi.loai_van_ban = request.POST.get("loai_van_ban")
            vbdi.han_xu_ly = request.POST.get("han_xu_ly")

            if request.FILES.get("file_du_thao"):
                vbdi.file_du_thao = request.FILES.get("file_du_thao")
            if request.FILES.get("file_lien_quan"):
                vbdi.file_lien_quan = request.FILES.get("file_lien_quan")
            new_duyet_id = request.POST.get("nguoi_duyet")
            if new_duyet_id:
                vbdi.nguoi_duyet = User.objects.get(id=new_duyet_id)
            new_nhan_id = request.POST.get("nguoi_nhan")
            if new_nhan_id:
                vbdi.nguoi_nhan = User.objects.get(id=new_nhan_id)
            vbdi.trang_thai = "Chờ duyệt"
            vbdi.save()
            if vbdi.nguoi_duyet:
                Notification.objects.create(
                    user=vbdi.nguoi_duyet,
                    title="Dự thảo đã được sửa lại",
                    message=f"{request.user.get_full_name()} đã cập nhật và trình lại dự thảo số {vbdi.so_van_ban}.",
                    type='duyet_van_ban')
            messages.success(request, "Đã cập nhật và trình lại dự thảo.")
            return redirect('lap_du_thao')
        except IntegrityError:
            messages.error(request, "Số văn bản bị trùng.")

    return render(request, 'vanbandi/lap_du_thao.html', {
        'vbdi_edit': vbdi,
        'nguoi_xu_ly_list': User.objects.filter(is_active=True)
    })

@login_required
def van_ban_cho_ban_hanh(request):
    van_ban_list = VanBanDi.objects.filter(trang_thai='Chờ duyệt').order_by('han_xu_ly')

    q = request.GET.get('q')
    tu_ngay = request.GET.get('tu_ngay')
    den_ngay = request.GET.get('den_ngay')
    han_xu_ly = request.GET.get('han_xu_ly')

    if tu_ngay:
        van_ban_list = van_ban_list.filter(ngay_tao__gte=tu_ngay)
    if den_ngay:
        van_ban_list = van_ban_list.filter(ngay_tao__lte=den_ngay)
    if q:
        van_ban_list = van_ban_list.filter(
            Q(so_van_ban__icontains=q) |
            Q(nguoi_lap__username__icontains=q) |
            Q(trich_yeu__icontains=q)
        )

    today = timezone.localtime(timezone.now()).date()
    if han_xu_ly:
        if han_xu_ly == 'hom_nay':
            van_ban_list = van_ban_list.filter(han_xu_ly=today)
        elif han_xu_ly == 'qua_han':
            van_ban_list = van_ban_list.filter(han_xu_ly__lt=today)
        elif han_xu_ly == 'sap_den_han':
            future_date = today + timedelta(days=3)
            van_ban_list = van_ban_list.filter(han_xu_ly__gte=today, han_xu_ly__lte=future_date)

    return render(request, 'vanbandi/van_ban_cho_ban_hanh.html', {
        'van_ban_list': van_ban_list,
        'request': request,
        'today': today
    })


@login_required
def duyet_van_ban(request, pk):
    vbdi = get_object_or_404(VanBanDi, pk=pk)
    if vbdi.nguoi_duyet != request.user:
        messages.error(request, "Bạn không có quyền duyệt văn bản này.")
        return redirect('van_ban_cho_ban_hanh')
    try:
        vbdi.trang_thai = "Đã ban hành"
        last_vbden = VanBanDen.objects.order_by('-MaVanBanDen').first()
        so_den_moi = (last_vbden.SoDen + 1) if last_vbden else 1
        notification_receiver = None
        target_username = ""
        target_fullname = ""

        if vbdi.nguoi_nhan:
            notification_receiver = vbdi.nguoi_nhan
            target_username = vbdi.nguoi_nhan.username
            target_fullname = vbdi.nguoi_nhan.get_full_name() or vbdi.nguoi_nhan.username
        else:
            notification_receiver = request.user
            target_username = request.user.username
            target_fullname = request.user.get_full_name() or request.user.username
        vbden = VanBanDen.objects.create(
            SoDen=so_den_moi,
            SoKyHieu=vbdi.so_van_ban,
            TrichYeu=vbdi.trich_yeu,
            HanXuLy=vbdi.han_xu_ly,
            NgayDen=timezone.now().date(),
            NgayBanHanh=timezone.now().date(),
            user=request.user,
            CoQuanBanHanh=vbdi.co_quan_ban_hanh or "Ban Giám Hiệu",
            LoaiVanBan=vbdi.loai_van_ban or "Văn bản đi",
            NguoiKy=vbdi.nguoi_duyet.get_full_name() if vbdi.nguoi_duyet else "Lãnh đạo",
            NguoiNhan=notification_receiver,
            NguoiDuyet=request.user.username,
            DoKhan="Thường",
            DoMat="Thường",
            FileDinhKem = vbdi.file_du_thao
        )
        vbdi.van_ban_den_lien_quan = vbden
        vbdi.save()
        if notification_receiver:
            Notification.objects.create(
                user=notification_receiver,
                title="Bạn có văn bản đến mới",
                message=f"Văn bản số {vbdi.so_van_ban} vừa được ban hành và chuyển đến bạn. Vui lòng xử lý.",
                type='van_ban_den',
                related_id=vbden.MaVanBanDen
            )
        if vbdi.nguoi_lap:
            Notification.objects.create(
                user=vbdi.nguoi_lap,
                title="Dự thảo đã được duyệt",
                message=f"Dự thảo số {vbdi.so_van_ban} đã được {request.user.get_full_name()} duyệt và ban hành.",
                type='phan_hoi_van_ban',
                related_id=vbdi.id
            )
        messages.success(request,
                         f"Đã duyệt và ban hành văn bản số {vbdi.so_van_ban}. Hệ thống đã chuyển tiếp cho: {target_fullname}.")
    except Exception as e:
        messages.error(request, f"Lỗi khi duyệt: {e}")

    return redirect('van_ban_cho_ban_hanh')

@login_required
def yeu_cau_sua_vbdi(request, pk):
    vbdi = get_object_or_404(VanBanDi, pk=pk)

    if vbdi.nguoi_duyet != request.user:
        messages.error(request, "Bạn không có quyền thao tác.")
        return redirect('van_ban_cho_ban_hanh')

    vbdi.trang_thai = "Bị từ chối"
    vbdi.save()
    if vbdi.nguoi_lap:
        Notification.objects.create(
            user=vbdi.nguoi_lap,
            title="Yêu cầu chỉnh sửa dự thảo",
            message=f"Dự thảo số {vbdi.so_van_ban} đã bị từ chối. Vui lòng kiểm tra và chỉnh sửa.",
            type='phan_hoi_van_ban'
        )
    messages.warning(request, f"Đã trả lại văn bản {vbdi.so_van_ban} để yêu cầu chỉnh sửa.")
    return redirect('van_ban_cho_ban_hanh')

@login_required
def van_ban_di_ca_nhan(request):
    vb_list = VanBanDi.objects.filter(nguoi_lap=request.user).order_by('-ngay_tao')

    trang_thai_loc = request.GET.get('trang_thai_loc')
    q = request.GET.get('q')

    if trang_thai_loc and trang_thai_loc != 'tat_ca':
        vb_list = vb_list.filter(trang_thai=trang_thai_loc)

    if q:
        vb_list = vb_list.filter(
            Q(so_van_ban__icontains=q) |
            Q(trich_yeu__icontains=q)
        )

    return render(request, 'vanbandi/van_ban_di_ca_nhan.html', {
        'vb_list': vb_list,
        'trang_thai_loc': trang_thai_loc,
        'q': q
    })


@login_required
def tra_cuu_van_ban_di(request):
    vb_list = VanBanDi.objects.filter(trang_thai='Đã ban hành').order_by('-ngay_tao')

    q = request.GET.get('q')
    tu_ngay = request.GET.get('tu_ngay')
    den_ngay = request.GET.get('den_ngay')

    if tu_ngay:
        vb_list = vb_list.filter(ngay_tao__gte=tu_ngay)
    if den_ngay:
        vb_list = vb_list.filter(ngay_tao__lte=den_ngay)
    if q:
        vb_list = vb_list.filter(
            Q(so_van_ban__icontains=q) |
            Q(trich_yeu__icontains=q) |
            Q(nguoi_lap__username__icontains=q)
        )

    return render(request, 'vanbandi/tra_cuu_van_ban_di.html', {
        'vb_list': vb_list,
        'q': q,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay
    })

@login_required
def trang_chu(request):
    user = request.user
    cv_dang_xu_ly = CongViec.objects.filter(
        TrangThai__in=["Đang xử lý", "Yêu cầu sửa", "Chờ phê duyệt"]
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    cv_cho_xu_ly = CongViec.objects.filter(
        TrangThai="Chờ xử lý"
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    cv_hoan_thanh = CongViec.objects.filter(
        TrangThai="Hoàn thành"
    ).filter(Q(NguoiXuLyChinh=user) | Q(nguoi_phoi_hop__NguoiDung=user)).distinct().count()

    return render(request, "trang_chu.html", {
        "user": user,
        "cv_dang_xu_ly": cv_dang_xu_ly,
        "cv_cho_xu_ly": cv_cho_xu_ly,
        "cv_hoan_thanh": cv_hoan_thanh,
    })


@login_required
def vanbanden_list(request):
    vb_list = VanBanDen.objects.all().order_by('-NgayDen')
    return render(request, 'vanbandi/vanbanden_list.html', {'vb_list': vb_list})


@login_required
def vanbanden_create(request):
    nguoi_xu_ly_list = User.objects.filter(is_active=True)
    return render(request, 'vanbandi/vanbanden_create.html', {'nguoi_xu_ly_list': nguoi_xu_ly_list})


@login_required
def vanbanden_detail(request, pk):
    vbden = get_object_or_404(VanBanDen, pk=pk)
    return render(request, 'vanbandi/vanbanden_detail.html', {'vbden': vbden})