from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from model_share.models import VanBanDen, PhongBan, CongViec, NguoiXuLy, Notification
from vanbanden.forms import VanBanDenFilterForm, YeuCauSuaForm
from congviec.forms import CongViecFilterForm
from django.core.exceptions import PermissionDenied

def send_notification(user, title, message):
    if user:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )

# 1. VĂN BẢN CHỜ XỬ LÝ
@login_required
def van_ban_cho_xu_ly(request):
   form = VanBanDenFilterForm(request.GET or None)
   vanbans = VanBanDen.objects.filter(TrangThai='Chờ xử lý', NguoiNhan=request.user).order_by('-NgayDen')

   if form.is_valid():
       q = form.cleaned_data.get('q')
       tu_ngay = form.cleaned_data.get('tu_ngay')
       den_ngay = form.cleaned_data.get('den_ngay')
       trang_thai = form.cleaned_data.get('trang_thai')

       if q:
           vanbans = vanbans.filter(
               Q(SoKyHieu__icontains=q) |
               Q(TrichYeu__icontains=q) |
               Q(CoQuanBanHanh__icontains=q)
           )
       if tu_ngay:
           vanbans = vanbans.filter(NgayDen__gte=tu_ngay)
       if den_ngay:
           vanbans = vanbans.filter(NgayDen__lte=den_ngay)
       if trang_thai:
           vanbans = vanbans.filter(TrangThai=trang_thai)

   return render(request, 'vanbanden/vanban_cho_xuly.html', {
       'vanbans': vanbans,
       'form': form,
   })

# 3. THEO DÕI XỬ LÝ (Ban lãnh đạo)
@login_required
def theodoi_xuly(request):
   form = CongViecFilterForm(request.GET or None)
   cong_viecs = CongViec.objects.select_related('MaVanBanDen') .filter(MaVanBanDen__NguoiNhan=request.user) .exclude(TrangThai="Hoàn thành") .order_by('-HanXuLy')

   if form.is_valid():
       TieuDe = form.cleaned_data.get('TieuDe')
       TrangThai = form.cleaned_data.get('TrangThai')
       TuNgay = form.cleaned_data.get('TuNgay')
       DenNgay = form.cleaned_data.get('DenNgay')

       if TieuDe:
           cong_viecs = cong_viecs.filter(
               Q(TieuDe__icontains=TieuDe) |
               Q(MaVanBanDen__TrichYeu__icontains=TieuDe)
           )
       if TrangThai:
           cong_viecs = cong_viecs.filter(TrangThai=TrangThai)
       if TuNgay:
           cong_viecs = cong_viecs.filter(HanXuLy__gte=TuNgay)
       if DenNgay:
           cong_viecs = cong_viecs.filter(HanXuLy__lte=DenNgay)

   return render(request, 'vanbanden/theodoi_xuly.html', {
       'form': form,
       'cong_viecs': cong_viecs,
   })

# 4. TRA CỨU VĂN BẢN
@login_required
def tracuu_vanbanden(request):
   form = VanBanDenFilterForm(request.GET or None)
   
   vanban_list = VanBanDen.objects.filter(NguoiNhan=request.user).order_by('-NgayDen')
   if form.is_valid():
       q = form.cleaned_data.get('q')
       tu_ngay = form.cleaned_data.get('tu_ngay')
       den_ngay = form.cleaned_data.get('den_ngay')
       trang_thai = form.cleaned_data.get('trang_thai')

       if q:
           vanban_list = vanban_list.filter(
               Q(SoKyHieu__icontains=q) |
               Q(TrichYeu__icontains=q) |
               Q(CoQuanBanHanh__icontains=q)
           )
       if tu_ngay:
           vanban_list = vanban_list.filter(NgayDen__gte=tu_ngay)
       if den_ngay:
           vanban_list = vanban_list.filter(NgayDen__lte=den_ngay)
       if trang_thai:
           vanban_list = vanban_list.filter(TrangThai=trang_thai)

   return render(request, 'vanbanden/tracuu_vanbanden.html', {
       'form': form,
       'vanban_list': vanban_list,
   })

# 5. CHI TIẾT VĂN BẢN
@login_required
def vanban_detail(request, vanban_id):
    vanban = get_object_or_404(VanBanDen, pk=vanban_id)
    if request.user != vanban.NguoiNhan and not request.user.is_superuser:
        raise PermissionDenied("Bạn không có quyền xem văn bản này.")
    return render(request, 'vanbanden/vanban_detail.html', {'vanban': vanban})

# 6. PHÂN CÔNG (Lãnh đạo)
@login_required
def phan_cong_van_ban(request, pk):
   vanban = get_object_or_404(VanBanDen, pk=pk)
   phongbans = PhongBan.objects.all()
   phongban_canbos = {}
   for pb in phongbans:
       canbos = User.objects.filter(userprofile__phong_ban=pb)
       phongban_canbos[pb] = canbos

   if request.method == 'POST':
       canbo_ids = request.POST.getlist('canbos')
       noi_dung = request.POST.get('noi_dung')
       han_xu_ly = request.POST.get('han_xu_ly')

       if canbo_ids:
           # Cập nhật trạng thái văn bản
           vanban.HanXuLy = han_xu_ly
           vanban.TrangThai = 'Đang xử lý'
           vanban.save()

           nguoi_chinh_id = request.POST.get('nguoi_chinh')
           main_id = nguoi_chinh_id if (nguoi_chinh_id in canbo_ids) else canbo_ids[0]
           main_user = User.objects.filter(pk=main_id).first()
           # Tạo công việc mới
           cong_viec = CongViec.objects.create(
               TieuDe=noi_dung,
               NgayNhan=timezone.now().date(),
               HanXuLy=han_xu_ly,
               TrangThai='Chờ xử lý',
               MaVanBanDen=vanban,
               NguoiXuLyChinh=main_user
           )

           for canbo_id in canbo_ids:
               user = User.objects.get(pk=canbo_id)
               vai_tro = request.POST.get(f'vaitro_{canbo_id}', 'Phối hợp xử lý')
               NguoiXuLy.objects.create(
                   CongViec=cong_viec,
                   NguoiDung=user,
                   VaiTro=vai_tro
               )
               send_notification(
                   user=user,
                   title="Bạn được giao công việc mới",
                   message=f"Bạn được giao xử lý công việc: {noi_dung}"
               )

           messages.success(request, "Phân công công việc thành công!")
           return redirect('theodoi_xuly')

   return render(request, 'vanbanden/phancong_vanban.html', {
       'vanban': vanban,
       'phongban_canbos': phongban_canbos,
   })

# 6.1 PHÂN CÔNG LẠI (Lãnh đạo)
@login_required
def phan_cong_lai(request, pk, cv_pk):
    vanban = get_object_or_404(VanBanDen, pk=pk)
    cong_viec = get_object_or_404(CongViec, pk=cv_pk, MaVanBanDen=vanban)

    phongbans = PhongBan.objects.all()
    phongban_canbos = {pb: User.objects.filter(userprofile__phong_ban=pb) for pb in phongbans}

    if request.method == "POST":
        noi_dung = request.POST.get('noi_dung', '').strip()
        han_xu_ly_str = request.POST.get('han_xu_ly')
        canbo_ids = request.POST.getlist('canbos')
        nguoi_chinh_id = request.POST.get('nguoi_chinh')

        if not canbo_ids:
            messages.error(request, "Vui lòng chọn ít nhất một cán bộ xử lý.")
        else:
            han_xu_ly = parse_date(han_xu_ly_str)
            cong_viec.TieuDe = noi_dung or cong_viec.TieuDe
            cong_viec.HanXuLy = han_xu_ly

            main_id = nguoi_chinh_id if (nguoi_chinh_id in canbo_ids) else canbo_ids[0]
            main_user = User.objects.filter(pk=main_id).first() or cong_viec.NguoiXuLyChinh
            cong_viec.NguoiXuLyChinh = main_user

            cong_viec.TrangThai = 'Chờ xử lý'
            cong_viec.save()

            vanban.HanXuLy = han_xu_ly
            vanban.TrangThai = 'Đang xử lý'
            vanban.save()

            # thay người xử lý: xóa rồi bulk_create
            NguoiXuLy.objects.filter(CongViec=cong_viec).delete()
            nx_objs = []
            for cb_id in canbo_ids:
                u = User.objects.filter(pk=cb_id).first()
                if not u:
                    continue
                vaitro = request.POST.get(f'vaitro_{cb_id}', 'Phối hợp xử lý')
                nx_objs.append(NguoiXuLy(CongViec=cong_viec, NguoiDung=u, VaiTro=vaitro))

                send_notification(
                    user=u,
                    title="Bạn được phân công công việc",
                    message=f"Công việc '{cong_viec.TieuDe}' đã được phân công cho bạn."
                )
            if nx_objs:
                NguoiXuLy.objects.bulk_create(nx_objs)

            messages.success(request, "Phân công lại công việc thành công.")
            return redirect("theodoi_xuly")

    # chuẩn bị dữ liệu hiển thị
    nx_dict = {nx.NguoiDung.id: nx for nx in NguoiXuLy.objects.filter(CongViec=cong_viec)}
    return render(request, "vanbanden/phancong_vanban.html", {
        "instance": cong_viec,
        "vanban": vanban,
        "phongban_canbos": phongban_canbos,
        "nx_dict": nx_dict,
    })

# 7. DUYỆT CÔNG VIỆC (Lãnh đạo)
@login_required
def duyet_cong_viec(request, pk):
   cong_viec = get_object_or_404(CongViec, pk=pk)
   if request.method == 'POST':
       action = request.POST.get('action')
       if action == 'approve':
           cong_viec.TrangThai = "Hoàn thành"
           send_notification(
               user=cong_viec.NguoiXuLyChinh,
               title="Công việc đã được phê duyệt",
               message=f"Công việc '{cong_viec.TieuDe}' đã được lãnh đạo phê duyệt."
           )
       elif action == 'reject':
           cong_viec.TrangThai = "Đang xử lý"
           send_notification(
               user=cong_viec.NguoiXuLyChinh,
               title="Công việc bị từ chối",
               message=f"Lãnh đạo yêu cầu bạn xử lý lại công việc: {cong_viec.TieuDe}"
           )
       cong_viec.save()
       return redirect('theodoi_xuly')
   return render(request, 'vanbanden/duyet_cong_viec.html', {'cong_viec': cong_viec})

# 8. YÊU CẦU SỬA (Lãnh đạo)
@login_required
def yeu_cau_sua_create(request, cong_viec_id):
   cong_viec = get_object_or_404(CongViec, pk=cong_viec_id)
   van_ban = cong_viec.MaVanBanDen

   if request.method == "POST":
       form = YeuCauSuaForm(request.POST, request.FILES)
       if form.is_valid():

           yeu_cau = form.save(commit=False)
           yeu_cau.NguoiYeuCau = request.user
           yeu_cau.CongViecLienQuan = cong_viec
           yeu_cau.VanBanLienQuan = van_ban
           yeu_cau.save()

           cong_viec.TrangThai = "Yêu cầu sửa"
           cong_viec.save()

           send_notification(
               user=cong_viec.NguoiXuLyChinh,
               title="Yêu cầu sửa công việc",
               message=f"Lãnh đạo yêu cầu sửa công việc: {cong_viec.TieuDe}"
           )

           messages.success(request, "Đã gửi yêu cầu xử lý lại và cập nhật trạng thái công việc thành công.")
           return redirect('theodoi_xuly')
   else:
       form = YeuCauSuaForm()

   return render(request, 'vanbanden/yeu_cau_sua_form.html', {
       'form': form,
       'cong_viec': cong_viec,
       'van_ban': van_ban,
   })