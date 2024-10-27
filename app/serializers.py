from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.db.models import Max

class RegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    zalo_name = serializers.CharField(required=False)
    zalo_id = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'email','zalo_name','zalo_id']

    def create(self, validated_data):
        # Lấy các thông tin zalo_name và zalo_id từ dữ liệu đã xác thực
        zalo_name = validated_data.pop('zalo_name', None)
        zalo_id = validated_data.pop('zalo_id',None)
        # create_profile
        if zalo_id is not None:
            qs_zalo_id=Profile.objects.filter(zalo_id=zalo_id).count()
            if qs_zalo_id==0:
                user = User.objects.create_user(username=validated_data['username'],
                                                password=validated_data['password'],
                                                email=validated_data['email'])
                Profile.objects.create(
                    user=user,
                    zalo_name=zalo_name,
                    zalo_id=zalo_id
                )
            else:
                raise serializers.ValidationError({
                    'zalo_id': f"Zalo ID {zalo_id} đã tồn tại!"
                })
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    def get_profile(self, user):
        try:
            qs_user=Profile.objects.get(user=user)
            print(f"Profile: {qs_user}")
            return ProfileSerializer(qs_user,many=False).data
        except:
            return []
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'
        
class PhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ["id","filename","filesize","data_mini","created_at","updated_at"]
        read_only_fields = ['user']  # Make the user field read-only
    def update(self, instance, validated_data):
        instance.album = validated_data.get('album', instance.album)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_public = validated_data.get('is_public', instance.is_public)
        instance.save()
        return instance
    
        
class KieungaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Kieungay
        fields = ['id','tenloaingay','ghichu','ngaycuthe','ngaytrongtuan','cochuyencan']

class KieucaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kieuca
        fields = ['id','tenca','ghichu']

class HesoSerializer(serializers.ModelSerializer):
    loaingay = serializers.CharField(source='kieungay.tenloaingay',read_only=True)
    loaica = serializers.CharField(source='kieuca.tenca',read_only=True)
    class Meta:
        model = Heso
        fields = ['id','loaingay','loaica','batdau','ketthuc','heso']
    
class TutinhluongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutinhluong
        fields = '__all__'

class TutinhChuyencanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutinhChuyencan
        fields = '__all__'
    
class TuchamcongSerializer(serializers.ModelSerializer):
    hesos = serializers.SerializerMethodField(read_only=True)
    kieungays = serializers.SerializerMethodField(read_only=True)
    kieucas = serializers.SerializerMethodField(read_only=True)
    chuyencan = serializers.SerializerMethodField(read_only=True)
    bangluong = serializers.SerializerMethodField(read_only=True)
    def get_bangluong(self,qs_data):
        try:
            qs=Tutinhluong.objects.filter(tuchamcong=qs_data)
            return TutinhluongSerializer(qs,many=True).data
        except Exception as e:
            return []
    def get_chuyencan(self,qs_data):
        try:
            qs=TutinhChuyencan.objects.filter(tuchamcong=qs_data)
            return TutinhChuyencanSerializer(qs,many=True).data
        except Exception as e:
            return []
    def get_kieungays(self,qs_data):
        try:
            qs=Kieungay.objects.filter(tuchamcong=qs_data)
            return KieungaySerializer(qs,many=True).data
        except Exception as e:
            return []
    def get_kieucas(self,qs_data):
        try:
            qs=Kieuca.objects.filter(tuchamcong=qs_data)
            return KieucaSerializer(qs,many=True).data
        except Exception as e:
            return []
    def get_hesos(self,qs_data):
        try:
            qs=Heso.objects.filter(tuchamcong=qs_data)
            return HesoSerializer(qs,many=True).data
        except Exception as e:
            return []
        
    class Meta:
        model = Tuchamcong
        fields = [
            "id","tencongty","ngaybatdau","bophan","chucvu",
            "hesos","kieungays","kieucas","chuyencan","bangluong",
            "created_at","updated_at"
        ]
        read_only_fields = ['user', 'hesos', 'kieungays', 'kieucas']  # Make nested fields read-only

    def create(self, validated_data):
        with transaction.atomic():
            # Tạo đối tượng Tuchamcong
            qs_old=Tuchamcong.objects.filter(user=validated_data.get("user"))
            if len(qs_old)>=1:
                raise  serializers.ValidationError({
                    'Lỗi': f"Đã có dữ liệu!"
                })
            tuchamcong = Tuchamcong.objects.create(**validated_data)

            # Tạo lương cơ bản
            Tutinhluong.objects.create(
                tuchamcong=tuchamcong,
                tenluong="Lương cơ bản",
                tinhvaotangca=True,
                luong=5000000
            )

            # Tạo thưởng chuyên cần
            TutinhChuyencan.objects.create(
                tuchamcong=tuchamcong,
                socongyeucau=26,
                tienchuyencan=500000,
                nghi1ngay=90
            )

            # Tạo các kiểu ngày và lưu từng đối tượng
            kieungay_list = [
                Kieungay(
                    tuchamcong=tuchamcong,
                    tenloaingay="Ngày thường",
                    ghichu="Ngày đi làm bình thường",
                    ngaytrongtuan="[1,2,3,4,5,6]"
                ),
                Kieungay(
                    tuchamcong=tuchamcong,
                    tenloaingay="Ngày nghỉ",
                    ghichu="Ngày nghỉ hưởng 200%",
                    ngaytrongtuan="[0]"
                ),
                Kieungay(
                    tuchamcong=tuchamcong,
                    tenloaingay="Ngày lễ",
                    ghichu="Ngày lễ hưởng 300%",
                    ngaycuthe="""["01/01","02/01","03/01","04/01","10/03","30/04","01/05","02/09"]""",
                    cochuyencan=True
                )
            ]

            # Lưu từng đối tượng kieungay
            for kieungay in kieungay_list:
                kieungay.save()

            # Tạo kiểu ca
            kieuca = Kieuca.objects.create(
                tuchamcong=tuchamcong,
                tenca="Hành chính",
                ghichu="Đi làm hành chính"
            )

            # Tự động tạo các hệ số cho mỗi kiểu ngày
            for kieungay in kieungay_list:
                if kieungay.tenloaingay == "Ngày thường":
                    Heso.objects.bulk_create([
                        Heso(
                            tuchamcong=tuchamcong,
                            kieungay=kieungay,
                            kieuca=kieuca,
                            batdau="08:00:00",
                            ketthuc="17:00:00",
                            heso=1.0  # 100%
                        ),
                        Heso(
                            tuchamcong=tuchamcong,
                            kieungay=kieungay,
                            kieuca=kieuca,
                            batdau="17:00:00",
                            ketthuc="22:00:00",
                            heso=1.5  # 150%
                        )
                    ])
                elif kieungay.tenloaingay == "Ngày nghỉ":
                    Heso.objects.create(
                        tuchamcong=tuchamcong,
                        kieungay=kieungay,
                        kieuca=kieuca,
                        batdau="08:00:00",
                        ketthuc="22:00:00",
                        heso=2.0  # 200%
                    )
                elif kieungay.tenloaingay == "Ngày lễ":
                    Heso.objects.create(
                        tuchamcong=tuchamcong,
                        kieungay=kieungay,
                        kieuca=kieuca,
                        batdau="08:00:00",
                        ketthuc="22:00:00",
                        heso=3.0  # 300%
                    )

            # Trả về đối tượng Tuchamcong đã tạo
            return tuchamcong

class TuchamcongtaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tuchamcongtay
        fields = '__all__'

class KieungaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Kieungay
        fields = '__all__'

class KieucaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kieuca
        fields = '__all__'

class HesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heso
        fields = '__all__'

class CongtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Congty
        fields = [
            "id","tencongty","diachi","hotline",
            "loaihinhkinhdoanh","danhmuc",
            "created_at","updated_at"
        ]
        read_only_fields = ['user', 'daxacminh', 'doitac']  # Make nested fields read-only
    def create(self, validated_data):
        with transaction.atomic():
            # Tạo đối tượng Tuchamcong
            if validated_data.get("tencongty",None) is None:
                raise  serializers.ValidationError({
                    'Lỗi': f"Tên công ty không được để trống!"
                })
            if validated_data.get("diachi",None) is None:
                raise  serializers.ValidationError({
                    'Lỗi': f"Tên công ty không được để trống!"
                })
            if validated_data.get("hotline",None) is None:
                raise  serializers.ValidationError({
                    'Lỗi': f"Tên công ty không được để trống!"
                })
            if validated_data.get("loaihinhkinhdoanh",None) is None:
                raise  serializers.ValidationError({
                    'Lỗi': f"Tên công ty không được để trống!"
                })
            if validated_data.get("danhmuc",None) is None:
                raise  serializers.ValidationError({
                    'Lỗi': f"Tên công ty không được để trống!"
                })
            qs_old=Congty.objects.filter(user=validated_data.get("user"))
            if len(qs_old)>=1:
                raise  serializers.ValidationError({
                    'Lỗi': f"Đã có dữ liệu!"
                })
            congty = Congty.objects.create(**validated_data)
            return congty

class QuydinhSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quydinh
        fields = '__all__'

class ChiacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chiaca
        fields = '__all__'











class NguoitroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nguoitro
        fields = '__all__'

class NhatroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nhatro
        fields = '__all__'

class LichsuNguoitroSerializer(serializers.ModelSerializer):
    ThongtinNguoiTro = serializers.SerializerMethodField(read_only=True)
    SoPhong = serializers.CharField(source="phong.soPhong", allow_null=True)
    SoTang = serializers.CharField(source="phong.tang.tenTang", allow_null=True)
    def get_ThongtinNguoiTro(self, obj):
        return NguoitroSerializer(obj.nguoiTro, many=False).data

    class Meta:
        model = LichsuNguoitro
        fields = '__all__'

class ChiTietThanhToanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiTietThanhToan
        fields = '__all__'
class LichsuTieuThuSerializer(serializers.ModelSerializer):
    soDienBatDau = serializers.SerializerMethodField()
    soNuocBatDau = serializers.SerializerMethodField()
    def get_soDienBatDau(self, obj):
        previous_record = LichsuTieuThu.objects.filter(phong=obj.phong, id__lt=obj.id).order_by('-id').first()
        if previous_record:
            return previous_record.soDienKetthuc
        return 0  # Nếu không có bản ghi trước đó

    def get_soNuocBatDau(self, obj):
        previous_record = LichsuTieuThu.objects.filter(phong=obj.phong, id__lt=obj.id).order_by('-id').first()
        if previous_record:
            return previous_record.soNuocKetthuc
        return 0  # Nếu không có bản ghi trước đó
    class Meta:
        model = LichsuTieuThu
        fields = '__all__'
class LichsuThanhToanDetailsSerializer(serializers.ModelSerializer):
    Tieuthu = serializers.SerializerMethodField()
    Chitiet = serializers.SerializerMethodField()
    def get_Tieuthu(self, qs):
        try:
            qs_ct=LichsuTieuThu.objects.get(hoadon=qs)
            return LichsuTieuThuSerializer(qs_ct,many=False).data
        except Exception as e:
            return None
    def get_Chitiet(self, qs):
        try:
            qs_ct=ChiTietThanhToan.objects.filter(lichsu_thanh_toan=qs)
            return ChiTietThanhToanSerializer(qs_ct,many=True).data
        except Exception as e:
            return []
    class Meta:
        model = LichsuThanhToan
        fields = '__all__'

class PhongSerializer(serializers.ModelSerializer):
    tenTang = serializers.CharField(source='tang.tenTang', read_only=True)
    tiendien = serializers.SerializerMethodField(read_only=True)
    tiennuoc = serializers.SerializerMethodField(read_only=True)
    tienrac = serializers.SerializerMethodField(read_only=True)
    tienkhac = serializers.SerializerMethodField(read_only=True)
    Nguoitro = serializers.SerializerMethodField(read_only=True)
    DaTro = serializers.SerializerMethodField(read_only=True)
    Ngaybatdau = serializers.SerializerMethodField(read_only=True)
    wifi = serializers.SerializerMethodField()
    dieuhoa = serializers.SerializerMethodField()
    nonglanh = serializers.SerializerMethodField()
    giaPhong = serializers.SerializerMethodField(read_only=True)
    sodien = serializers.SerializerMethodField()
    sonuoc = serializers.SerializerMethodField()
    hoadon = serializers.SerializerMethodField(read_only=True)
    
    def update(self, instance, validated_data):
        sodien = validated_data.get('usodien',None)
        sonuoc = validated_data.get('usonuoc',None)
        print(f"{validated_data} {sodien} {sonuoc}")
        return instance
    
    def get_hoadon(self, qs):
        qs_hoadon=LichsuThanhToan.objects.filter(phong=qs)
        return LichsuThanhToanDetailsSerializer(qs_hoadon,many=True).data
    def get_sodien(self, obj):
        lich_su_moi_nhat = LichsuTieuThu.objects.filter(phong=obj).order_by('-created_at').first()
        if lich_su_moi_nhat:
            return lich_su_moi_nhat.soDienKetthuc
        return 0  # Trả về 0 nếu không có bản ghi
    
    def get_sonuoc(self, obj):
        lich_su_moi_nhat = LichsuTieuThu.objects.filter(phong=obj).order_by('-created_at').first()
        if lich_su_moi_nhat:
            return lich_su_moi_nhat.soNuocKetthuc
        return 0  # Trả về 0 nếu không có bản ghi
    
    def get_tiendien(self, qs):
        return qs.giaDien if qs.giaDien is not None else qs.tang.nhaTro.tiendien
    def get_tiennuoc(self, qs):
        return qs.giaNuoc if qs.giaNuoc is not None else qs.tang.nhaTro.tiennuoc
    def get_tienrac(self, qs):
        return qs.giaRac if qs.giaRac is not None else qs.tang.nhaTro.tienrac
    def get_tienkhac(self, qs):
        return qs.giaKhac if qs.giaKhac is not None else qs.tang.nhaTro.tienkhac
    def get_giaPhong(self, qs):
        return qs.giaPhong if qs.giaPhong is not None else qs.tang.nhaTro.tienphong
    def get_dieuhoa(self, qs):
        return qs.dieuhoa if qs.dieuhoa is not None else qs.tang.nhaTro.dieuhoa
    def get_wifi(self, qs):
        return qs.wifi if qs.wifi is not None else qs.tang.nhaTro.wifi
    def get_nonglanh(self, qs):
        return qs.nonglanh if qs.nonglanh is not None else qs.tang.nhaTro.nonglanh
    def get_Nguoitro(self, qs):
        qs_nguoi=LichsuNguoitro.objects.filter(phong=qs,isOnline=True)
        return LichsuNguoitroSerializer(qs_nguoi,many=True).data
    def get_DaTro(self, qs):
        qs_nguoi=LichsuNguoitro.objects.filter(phong=qs,isOnline=False)
        return LichsuNguoitroSerializer(qs_nguoi,many=True).data
    def get_Ngaybatdau(self, qs):
        qs_nguoi=LichsuNguoitro.objects.filter(phong=qs,isOnline=True).order_by('ngayBatdauO')
        if len(qs_nguoi)>0:
            return qs_nguoi[0].ngayBatdauO
        return None
    class Meta:
        model = Phong
        fields = '__all__'

class TangPhongSerializer(serializers.ModelSerializer):
    Chitiet = serializers.SerializerMethodField(read_only=True)
    def get_Chitiet(self, qs):
        qs_Phong=Phong.objects.filter(tang=qs)
        return PhongSerializer(qs_Phong,many=True).data
    class Meta:
        model = Tang
        fields = '__all__'

class NhatroDetailsSerializer(serializers.ModelSerializer):
    Thongtin = serializers.SerializerMethodField(read_only=True)
    def get_Thongtin(self, qs):
        qs_tang=Tang.objects.filter(nhaTro=qs)
        return TangPhongSerializer(qs_tang,many=True).data
    class Meta:
        model = Nhatro
        fields = '__all__'
class LichsuThanhToanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LichsuThanhToan
        fields = '__all__'

class DanhsachNhanvienSerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhsachNhanvien
        fields = '__all__'

class DanhsachCongtySerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhsachCongty
        fields = '__all__'

class DanhsachAdminSerializer(serializers.ModelSerializer):
    congty = DanhsachCongtySerializer()  # Changed to serialize a single instance
    class Meta:
        model = DanhsachAdmin
        fields = '__all__'
        
class DanhsachNhanvienSerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhsachNhanvien
        fields = '__all__'

class DanhsachnhanvienDilamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhsachnhanvienDilam
        fields = '__all__'


class DanhsachnhanvienDilamDetailsSerializer(serializers.ModelSerializer):
    manhanvien=DanhsachNhanvienSerializer()
    class Meta:
        model = DanhsachnhanvienDilam
        fields = '__all__'

class DanhsachnhanvienDilamSerializer(serializers.ModelSerializer):
    manhanvien = serializers.CharField(source="manhanvien.manhanvien", allow_null=True)
    def create(self, validated_data):
        manv = validated_data.pop('manhanvien', None)
        if manv:
            try:
                qs_manhanvien = DanhsachNhanvien.objects.get(manhanvien=manv)
                validated_data['manhanvien'] = qs_manhanvien
            except DanhsachNhanvien.DoesNotExist:
                raise serializers.ValidationError({'Error':f"Nhân viên với mã '{manv}' không tồn tại."})
        return super().create(validated_data)

    class Meta:
        model = DanhsachnhanvienDilam
        fields = '__all__'