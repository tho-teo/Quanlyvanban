from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import TraoDoiNoiBo
from model_share.models import PhongBan, Notification
from django.db.models import Q
from .forms import SoanTinForm, TraoDoiFilterForm, TinNhapForm

@login_required(login_url='/accounts/login/')
def soan_tin(request):
    form = SoanTinForm(request.POST or None, request.FILES or None)

    # Lấy tất cả phòng ban và nhân viên thuộc từng phòng ban
    phongbans = PhongBan.objects.all()
    don_vi_canbos = {}
    for pb in phongbans:
        canbos = User.objects.filter(userprofile__phong_ban=pb).exclude(id=request.user.id)
        if canbos.exists():
            don_vi_canbos[pb] = canbos

    # Lấy danh sách người nhận đã chọn (dạng list id string)
    nguoi_nhan_ids = request.POST.getlist("NguoiNhanCheckbox") if request.method == "POST" else []

    if request.method == "POST":
        if form.is_valid():
            tin = form.save(commit=False)
            tin.NguoiGui = request.user

            if "btn_send" in request.POST:
                tin.LaTinNhap = False
                tin.TrangThai = "Đã gửi"
                messages.success(request, "Tin nhắn đã được gửi thành công!")



            elif "btn_save_draft" in request.POST:
                tin.LaTinNhap = True
                tin.TrangThai = "Nháp"
                messages.success(request, "Đã lưu vào tin nháp!")

            tin.save()

            # Gán người nhận nếu có
            if nguoi_nhan_ids:
                tin.NguoiNhan.set(nguoi_nhan_ids)

                # thông báo
                if "btn_send" in request.POST:
                    from .views import send_notification  # hoặc import đầu file

                    for uid in nguoi_nhan_ids:
                        user = User.objects.get(id=uid)
                        send_notification(
                            user=user,
                            title="Bạn có tin nhắn nội bộ mới",
                            message=f"{request.user.get_full_name()} đã gửi: {tin.TieuDe}",
                        )

            form.save_m2m()
            return redirect("soan_tin")  # redirect để tránh submit lại khi F5



    return render(request, "traodoinoibo/soan_tin.html", {
        "form": form,
        "don_vi_canbos": don_vi_canbos,
        "nguoi_nhan_ids": nguoi_nhan_ids,
    })




@login_required(login_url='/accounts/login/')
def tin_den(request):

    form = TraoDoiFilterForm(request.GET)

    danh_sach_tin = (
        TraoDoiNoiBo.objects
        .filter(NguoiNhan=request.user, DaXoa=False)
        .select_related("NguoiGui", "DonViTrucThuoc")
        .order_by("-ThoiGianGui")
    )

    # --- ÁP DỤNG BỘ LỌC ---
    if form.is_valid():
        tu_ngay = form.cleaned_data.get("TuNgay")
        den_ngay = form.cleaned_data.get("DenNgay")
        tieu_de = form.cleaned_data.get("TieuDe")

        # Lọc theo ngày
        if tu_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__gte=tu_ngay)

        if den_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__lte=den_ngay)

        # Lọc theo tiêu đề
        if tieu_de:
            danh_sach_tin = danh_sach_tin.filter(TieuDe__icontains=tieu_de)

    # --- Lấy danh sách người gửi (Phục vụ lọc dropdown nếu cần) ---
    danh_sach_nguoi_gui = User.objects.filter(
        id__in=danh_sach_tin.values_list("NguoiGui_id", flat=True)
    ).distinct()

    return render(request, "traodoinoibo/tin_den.html", {
        "form": form,
        "danh_sach_tin": danh_sach_tin,
        "danh_sach_nguoi_gui": danh_sach_nguoi_gui,
    })

@login_required(login_url='/accounts/login/')
def tin_detail_tin_den(request, pk):
    tin = get_object_or_404(TraoDoiNoiBo, pk=pk)
    return render(request, 'traodoinoibo/tin_detail_tin_den.html', {'tin': tin})


@login_required
def tin_da_gui(request):

    form = TraoDoiFilterForm(request.GET)

    # CHỈ LẤY TIN MÌNH GỬI VÀ CHƯA XÓA
    danh_sach_tin = TraoDoiNoiBo.objects.filter(
        NguoiGui=request.user,
        TrangThai= 'Đã gửi',
        DaXoa=False,
    ).order_by('-ThoiGianGui')

    if form.is_valid():
        tu_ngay = form.cleaned_data.get("TuNgay")
        den_ngay = form.cleaned_data.get("DenNgay")
        tieu_de = form.cleaned_data.get("TieuDe")
        trang_thai = form.cleaned_data.get("TrangThai")

        if tu_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__gte=tu_ngay)

        if den_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__lte=den_ngay)

        if tieu_de:
            danh_sach_tin = danh_sach_tin.filter(TieuDe__icontains=tieu_de)

        if trang_thai:
            danh_sach_tin = danh_sach_tin.filter(TrangThai=trang_thai)

    return render(request, 'traodoinoibo/tin_da_gui.html', {
        'danh_sach_tin': danh_sach_tin,
        'form': form,
    })

@login_required(login_url='/accounts/login/')
def tin_detail_tin_da_gui(request, pk):
    tin = get_object_or_404(TraoDoiNoiBo, pk=pk)
    return render(request, 'traodoinoibo/tin_detail_tin_da_gui.html', {'tin': tin})


@login_required(login_url='/accounts/login/')
def tin_nhap(request):
    # Khởi tạo form với dữ liệu GET
    form = TraoDoiFilterForm(request.GET)

    # Lấy danh sách tin nháp ban đầu
    danh_sach_tin = TraoDoiNoiBo.objects.filter(
        NguoiGui=request.user,
        LaTinNhap=True,
        TrangThai= "Nháp",
        DaXoa=False,
    ).order_by('-ThoiGianGui')

    # Nếu form hợp lệ thì lấy dữ liệu đã clean
    if form.is_valid():
        tu_ngay = form.cleaned_data.get("TuNgay")
        den_ngay = form.cleaned_data.get("DenNgay")
        tieu_de = form.cleaned_data.get("TieuDe")

        # --- Lọc theo ngày ---
        if tu_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__gte=tu_ngay)

        if den_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__lte=den_ngay)

        # --- Lọc theo tiêu đề ---
        if tieu_de:
            danh_sach_tin = danh_sach_tin.filter(TieuDe__icontains=tieu_de)

    # Render ra template
    return render(request, 'traodoinoibo/tin_nhap.html', {
        'danh_sach_tin': danh_sach_tin,
        'form': form,
    })

@login_required(login_url='/accounts/login/')
def tin_detail_tin_nhap(request, pk):
    tin = get_object_or_404(TraoDoiNoiBo, pk=pk, TrangThai='Nháp')

    if request.method == "POST":

        # -------- NÚT LƯU NHÁP ----------
        if "luu_nhap" in request.POST:
            form = TinNhapForm(request.POST, request.FILES, instance=tin)
            if form.is_valid():
                form.save()
                messages.success(request, "Tin nháp đã được lưu.")
            return redirect('tin_detail_tin_nhap', pk=tin.pk)

        # -------- NÚT GỬI TIN ----------
        elif "gui_tin" in request.POST:
            form = TinNhapForm(request.POST, request.FILES, instance=tin)
            if form.is_valid():
                tin = form.save(commit=False)
                tin.TrangThai = "Đã gửi"
                tin.ThoiGianGui = timezone.now()
                tin.save()
                # 🔔 Gửi thông báo tại đây
                nguoi_nhan_list = tin.NguoiNhan.all()
                from .views import send_notification

                for user in nguoi_nhan_list:
                    send_notification(
                        user=user,
                        title="Bạn có tin nội bộ mới",
                        message=f"{request.user.get_full_name()} đã gửi: {tin.TieuDe}"
                    )
                messages.success(request, "Tin đã được gửi thành công.")
                return redirect('tin_nhap')

    else:
        form = TinNhapForm(instance=tin)

    return render(request, 'traodoinoibo/tin_detail_tin_nhap.html', {
        'tin': tin,
        'form': form
    })

@login_required
def tin_da_xoa(request):
    form = TraoDoiFilterForm(request.GET)

    # LẤY TIN ĐÃ XÓA ĐÚNG 2 TRƯỜNG HỢP
    danh_sach_tin = (
        TraoDoiNoiBo.objects
        .filter(
            Q(DaXoa=True) &
            (Q(NguoiGui=request.user) | Q(NguoiNhan=request.user))
        )
        .select_related('NguoiGui', 'DonViTrucThuoc')  # chỉ dùng cho ForeignKey
        .prefetch_related('NguoiNhan')                  # dùng cho ManyToMany
        .order_by('-ThoiGianGui')
    )

    # Nếu form hợp lệ thì lấy dữ liệu đã clean
    if form.is_valid():
        tu_ngay = form.cleaned_data.get("TuNgay")
        den_ngay = form.cleaned_data.get("DenNgay")
        tieu_de = form.cleaned_data.get("TieuDe")

        # --- Lọc theo ngày ---
        if tu_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__gte=tu_ngay)

        if den_ngay:
            danh_sach_tin = danh_sach_tin.filter(ThoiGianGui__date__lte=den_ngay)

        # --- Lọc theo tiêu đề ---
        if tieu_de:
            danh_sach_tin = danh_sach_tin.filter(TieuDe__icontains=tieu_de)

    return render(request, 'traodoinoibo/tin_da_xoa.html', {
        'danh_sach_tin': danh_sach_tin,
        'form': form,
    })


@login_required(login_url='/accounts/login/')
def tin_detail_tin_da_xoa(request, pk):
    tin = get_object_or_404(TraoDoiNoiBo, pk=pk)
    return render(request, 'traodoinoibo/tin_detail_tin_da_xoa.html', {'tin': tin})


def delete_message(request, MaTin):
    tin = get_object_or_404(TraoDoiNoiBo, MaTin=MaTin)

    if tin.NguoiGui == request.user or tin.NguoiNhan == request.user:
        tin.DaXoa = True
        tin.TrangThai = "Đã xóa"
        tin.save()

    return redirect("tin_den")

@login_required
def action_tin_xoa(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")

        if not ids:
            return redirect("tin_da_xoa")

        # XÓA VĨNH VIỄN
        if "btn_delete" in request.POST:
            TraoDoiNoiBo.objects.filter(
                MaTin__in=ids,
                DaXoa=True
            ).delete()

            messages.success(request, "Đã xóa vĩnh viễn các tin đã chọn!")
            return redirect("tin_da_xoa")

        # KHÔI PHỤC
        if "btn_restore" in request.POST:

            danh_sach = TraoDoiNoiBo.objects.filter(
                MaTin__in=ids,
                DaXoa=True
            ).filter(
                Q(NguoiGui=request.user) | Q(NguoiNhan=request.user)
            )

            for tin in danh_sach:

                # Khôi phục tin nháp (chỉ thuộc người gửi)
                if tin.TrangThai == "Nháp" and tin.NguoiGui == request.user:
                    tin.DaXoa = False
                    tin.TrangThai = "Nháp"
                    tin.LaTinNhap = True  # <<< THÊM DÒNG NÀY

                # Khôi phục tin đã gửi (người gửi)
                elif tin.NguoiGui == request.user:
                    tin.DaXoa = False
                    tin.TrangThai = "Đã gửi"
                    tin.LaTinNhap = False  # <<< ĐỂ CHẮC CHẮN

                # Khôi phục tin đến (người nhận)
                elif request.user in tin.NguoiNhan.all():
                    tin.DaXoa = False
                    tin.TrangThai = "Đã gửi"
                    tin.LaTinNhap = False

                tin.save()

            messages.success(request, "Khôi phục tin nhắn thành công!")
            return redirect("tin_da_xoa")


@login_required
def xoa_tin_da_gui(request, MaTin):
    tin = get_object_or_404(TraoDoiNoiBo, MaTin=MaTin, NguoiGui=request.user)

    tin.DaXoa = True
    tin.TrangThai = "Đã xóa"
    tin.save()
    messages.success(request, "Tin này đã chuyển vào mục Tin đã xóa.")
    return redirect("tin_da_gui")


@login_required
def xoa_tin_den(request, MaTin):
    tin = get_object_or_404(
        TraoDoiNoiBo,
        MaTin=MaTin,
        NguoiNhan=request.user
    )

    tin.DaXoa = True
    tin.TrangThai = "Đã xóa"
    tin.save()
    messages.success(request, "Tin này đã chuyển vào mục Tin đã xóa.")
    return redirect("tin_den")


@login_required

def xoa_tin_nhap(request, MaTin):
    tin = get_object_or_404(
        TraoDoiNoiBo,
        MaTin=MaTin,
        NguoiGui=request.user,   # CHÍNH XÁC: tin nháp do người gửi tạo ra
        LaTinNhap=True
    )

    tin.DaXoa = True
    tin.save()
    messages.success(request, "Tin này đã chuyển vào mục Tin đã xóa.")
    return redirect("tin_nhap")

def gui_tin(request, pk):
    tin = get_object_or_404(TraoDoiNoiBo, MaTin=pk, NguoiGui=request.user)

    if tin.TrangThai == 'Nháp':
        tin.TrangThai = 'Đã gửi'
        tin.ThoiGianGui = timezone.now()
        tin.save()
        messages.success(request, "Tin nháp đã được gửi thành công!")
    else:
        messages.warning(request, "Tin này đã được gửi rồi.")

    return redirect('tin_nhap')


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

# Hàm gửi thông báo

def send_notification(user, title, message):
    if user:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )







