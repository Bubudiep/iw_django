from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db import transaction
from django.db.models import Max,Sum
from rest_framework.permissions import IsAuthenticated
from django.utils.functional import cached_property

class LenmonRegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    zalo_name = serializers.CharField(required=False)
    zalo_phone = serializers.CharField(required=False)
    zalo_avatar = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'email','zalo_name','zalo_phone','zalo_avatar']
    def create(self, validated_data):
        # Lấy các thông tin zalo_name và zalo_id từ dữ liệu đã xác thực
        zalo_name = validated_data.pop('zalo_name', None)
        zalo_id = f"GUEST-{uuid.uuid4().hex.upper()}"
        zalo_phone = validated_data.pop('zalo_phone',None)
        zalo_avatar = validated_data.pop('zalo_avatar',None)
        # create_profile
        print(zalo_name)
        if zalo_name is not None:
            qs_zalo_id=Profile.objects.filter(zalo_id=zalo_id).count()
            if qs_zalo_id==0:
                user = User.objects.create_user(username=validated_data['username'],
                                                password=validated_data['password'],
                                                email=validated_data['email'])
                Profile.objects.create(
                    user=user,
                    zalo_name=zalo_name,
                    zalo_id=zalo_id,
                    zalo_phone=zalo_phone,
                    zalo_avatar=zalo_avatar,
                )
            else:
                raise serializers.ValidationError({
                    'zalo_id': f"Zalo ID {zalo_id} đã tồn tại!"
                })
        return user
    
class RegisterSerializer(serializers.ModelSerializer):
    # Bạn có thể thêm các trường zalo_name và zalo_id vào đây
    zalo_name = serializers.CharField(required=False)
    zalo_id = serializers.CharField(required=False)
    zalo_phone = serializers.CharField(required=False)
    zalo_avatar = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'email','zalo_name','zalo_id','zalo_phone','zalo_avatar']

    def create(self, validated_data):
        # Lấy các thông tin zalo_name và zalo_id từ dữ liệu đã xác thực
        zalo_name = validated_data.pop('zalo_name', None)
        zalo_id = validated_data.pop('zalo_id',None)
        zalo_phone = validated_data.pop('zalo_phone',None)
        zalo_avatar = validated_data.pop('zalo_avatar',None)
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
                    zalo_id=zalo_id,
                    zalo_phone=zalo_phone,
                    zalo_avatar=zalo_avatar,
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
    
class ProfileLenmonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "user","zalo_phone",
            "avatar",
            "wallpaper",
            "zalo_id",
            "zalo_name",
            "zalo_avatar"
        ]
  
class UserLenmonSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    def get_profile(self, user):
        try:
            qs_user=Profile.objects.get(user=user)
            return ProfileLenmonSerializer(qs_user,many=False).data
        except:
            return []
    class Meta:
        model = User
        fields = ['first_name','groups','email','date_joined','profile']
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


class Phong2Serializer(serializers.ModelSerializer):
    tenTang = serializers.CharField(source='tang.tenTang', read_only=True)
    tiendien = serializers.SerializerMethodField(read_only=True)
    tiennuoc = serializers.SerializerMethodField(read_only=True)
    tienrac = serializers.SerializerMethodField(read_only=True)
    tienkhac = serializers.SerializerMethodField(read_only=True)
    nguoitro = serializers.SerializerMethodField(read_only=True)
    wifi = serializers.SerializerMethodField()
    dieuhoa = serializers.SerializerMethodField()
    nonglanh = serializers.SerializerMethodField()
    tienphong = serializers.SerializerMethodField(read_only=True)
    def get_tiendien(self, qs):
        return qs.giaDien if qs.giaDien is not None else qs.tang.nhaTro.tiendien
    def get_tiennuoc(self, qs):
        return qs.giaNuoc if qs.giaNuoc is not None else qs.tang.nhaTro.tiennuoc
    def get_tienrac(self, qs):
        return qs.giaRac if qs.giaRac is not None else qs.tang.nhaTro.tienrac
    def get_tienkhac(self, qs):
        return qs.giaKhac if qs.giaKhac is not None else qs.tang.nhaTro.tienkhac
    def get_tienphong(self, qs):
        return qs.giaPhong if qs.giaPhong is not None else qs.tang.nhaTro.tienphong
    def get_dieuhoa(self, qs):
        return qs.dieuhoa if qs.dieuhoa is not None else qs.tang.nhaTro.dieuhoa
    def get_wifi(self, qs):
        return qs.wifi if qs.wifi is not None else qs.tang.nhaTro.wifi
    def get_nonglanh(self, qs):
        return qs.nonglanh if qs.nonglanh is not None else qs.tang.nhaTro.nonglanh
    def get_nguoitro(self, qs):
        qs_nguoi=LichsuNguoitro.objects.filter(phong=qs,isOnline=True)
        return len(qs_nguoi)
    class Meta:
        model = Phong
        fields = ['dieuhoa','nonglanh','wifi','nguoitro','tiendien','tiennuoc','tienrac'
                  ,'tienkhac','soPhong','tenTang','tienphong']

class NhatroNoiquySerializer(serializers.ModelSerializer):
    class Meta:
        model = NhatroNoiquy
        fields = '__all__'

class TangPhong2Serializer(serializers.ModelSerializer):
    Phong = serializers.SerializerMethodField(read_only=True)
    def get_Phong(self, qs):
        qs_Phong=Phong.objects.filter(tang=qs)
        return Phong2Serializer(qs_Phong,many=True).data
    class Meta:
        model = Tang
        fields = '__all__'

class Nhatro_thongtinSerializer(serializers.ModelSerializer):
    Tang = serializers.SerializerMethodField(read_only=True)
    Noiquy = serializers.SerializerMethodField(read_only=True)
    def get_Tang(self, qs):
        qs_tang=Tang.objects.filter(nhaTro=qs)
        return TangPhong2Serializer(qs_tang,many=True).data
    def get_Noiquy(self, qs):
        qs_noiquy=NhatroNoiquy.objects.filter(nhaTro=qs)
        return NhatroNoiquySerializer(qs_noiquy,many=True).data
    class Meta:
        model = Nhatro
        fields = '__all__'
        
class RestaurantSocketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_socket
        fields = ['id', 'name', 'is_active', 'description', 'QRKey', 'created_at', 'updated_at']
class RestaurantMenuMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_menu_marks
        fields = ['id', 'name']  # Adjust based on the fields you need from the Restaurant_menu_marks model

class RestaurantMenuGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_menu_groups
        fields = ['id', 'name']
        
class Restaurant_menu_itemsLTESerializer(serializers.ModelSerializer):
    mark = RestaurantMenuMarksSerializer(many=True)  # Serialize 'mark' (ManyToMany)
    group = RestaurantMenuGroupsSerializer(many=True)  # Serialize 'group' (ManyToMany)
    class Meta:
        model = Restaurant_menu_items
        fields = [
            'id', 'mark', 'group', 'name', 'price', 
            'is_hot', 'is_new', 'is_online', 'is_ship', 
            'is_available',
            'is_active', 'image64_mini', 'short_description'
        ]
    
class Restaurant_menu_itemsLTESSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_menu_items
        fields = [
            'id','price','name','image64_mini','is_active',
            'is_available','is_delete'
        ]
    
class Restaurant_menu_itemsRCMSerializer(serializers.ModelSerializer):
    restaurant = serializers.SerializerMethodField(read_only=True)
    paidQTY = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Restaurant_menu_items
        fields = [
            'id', 'name', 'price', 'image64_mini', 'short_description','restaurant','paidQTY'
        ]
    def get_paidQTY(self, obj):
        qs_order=Restaurant_order_items.objects.filter(items=obj,Order__is_paided=True
                                        ).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        return qs_order
    def get_restaurant(self, obj):
        res=obj.menu.restaurant
        return {
            "avatar":res.avatar,
            "name":res.name
        }
    
class Restaurant_menu_itemsSTSerializer(serializers.ModelSerializer):
    restaurant = serializers.SerializerMethodField(read_only=True)
    paidQTY = serializers.SerializerMethodField(read_only=True)
    totalRate = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Restaurant_menu_items
        fields = [
            'id', 'name', 'price', 'image64_mini', 
            'short_description','restaurant','paidQTY','totalRate'
        ]
    def get_totalRate(self, obj):
        return 0
    def get_paidQTY(self, obj):
        qs_order=Restaurant_order_items.objects.filter(items=obj,Order__is_paided=True
                                        ).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        return qs_order
    def get_restaurant(self, obj):
        res=obj.menu.restaurant
        return {
            "avatar":res.avatar,
            "name":res.name,
            "address":res.address_details
        }
    
class RestaurantMenuItemsSerializer(serializers.ModelSerializer):
    group = serializers.ListField(child=serializers.CharField(), write_only=True)
    mark = serializers.ListField(child=serializers.CharField(), write_only=True)
    group_names = serializers.SerializerMethodField(read_only=True)
    mark_names = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Restaurant_menu_items
        fields = ['id','is_ship','is_validate',
            'menu', 'name', 'price', 'is_hot', 'is_new', 'is_online','is_active',
            'image64_mini', 'image64_full', 'short_description', 'description', 
            'is_available', 'group', 'mark', 'group_names', 'mark_names','is_delete'
        ]
    def get_group_names(self, obj):
        return [group.name for group in obj.group.all()]

    def get_mark_names(self, obj):
        return [mark.name for mark in obj.mark.all()]

    def create(self, validated_data):
        group_names = validated_data.pop('group', None)
        mark_names = validated_data.pop('mark', None)
        menu_item = Restaurant_menu_items.objects.create(**validated_data)
        self.set_groups_and_marks(menu_item, group_names, mark_names)
        return menu_item
    def update(self, instance, validated_data):
        group_names = validated_data.pop('group', None)
        mark_names = validated_data.pop('mark', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self.set_groups_and_marks(instance, group_names, mark_names)
        return instance
    def set_groups_and_marks(self, menu_item, group_names, mark_names):
        if group_names is not None:
            groups = []
            for name in group_names:
                group, created = Restaurant_menu_groups.objects.get_or_create(name=name,
                                                                              menu=menu_item.menu)
                groups.append(group)
            menu_item.group.set(groups)
        if mark_names is not None:
            marks = []
            for name in mark_names:
                mark, created = Restaurant_menu_marks.objects.get_or_create(name=name,
                                                                            menu=menu_item.menu)
                marks.append(mark)
            menu_item.mark.set(marks)
     
class Restaurant_menu_groupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_menu_groups
        fields = '__all__'
        
class Restaurant_menu_marksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_menu_marks
        fields = '__all__'
        
class Restaurant_menuSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()  # Use SerializerMethodField to filter items
    group = Restaurant_menu_groupsSerializer(many=True, source='restaurant_menu_groups_set')  # Adjust source if needed
    mark = Restaurant_menu_marksSerializer(many=True, source='restaurant_menu_marks_set')  # Adjust source if needed
    def get_items(self, obj):
        active_items = obj.restaurant_menu_items_set.filter(is_delete=False)
        return RestaurantMenuItemsSerializer(active_items, many=True).data
    class Meta:
        model = Restaurant_menu
        fields = ['id', 'items', 'group', 'mark', 'name', 'is_online', 'description']
        
class Restaurant_menuViewSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()  # Use SerializerMethodField to filter items
    def get_items(self, obj):
        active_items = obj.restaurant_menu_items_set.filter(
            is_delete=False,
            is_active=True,
            name__isnull=False, # phải có tên
            image64_mini__isnull=False, #phải có ảnh đại diện
            is_validate=True, # phải được phê duyệt
        )
        return Restaurant_menu_itemsLTESSerializer(active_items, many=True).data
    class Meta:
        model = Restaurant_menu
        fields = ['id', 'items', 'name', 'is_online', 'description']
        
class RestaurantSpaceSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    class Meta:
        model = Restaurant_space
        fields = ['id', 'name','group_name','is_inuse','user_use', 'is_active', 'is_ordering', 'description', 'created_at', 'updated_at']

class RestaurantSpaceGroupSerializer(serializers.ModelSerializer):
    spaces = RestaurantSpaceSerializer(many=True, source='restaurant_space_set')  # Đảm bảo trường liên kết đúng

    class Meta:
        model = Restaurant_space_group
        fields = ['id', 'name', 'is_active', 'is_ordering', 'description', 'created_at', 'updated_at', 'spaces']

class RestaurantLayoutSerializer(serializers.ModelSerializer):
    groups = RestaurantSpaceGroupSerializer(many=True, source='restaurant_space_group_set')  # Đảm bảo trường liên kết đúng

    class Meta:
        model = Restaurant_layout
        fields = ['id', 'name', 'is_active', 'description', 'created_at', 'updated_at', 'groups']

class RestaurantCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_counpon
        fields = [
            'id', 'is_percent', 'value', 'max_discount', 'min_of_all_order',
            'min_of_this_order', 'max_for_person', 'is_for_first_order',
            'max_use', 'start_use', 'end_use', 'title', 'description',
            'description_short', 'created_at', 'updated_at'
        ]
  
class RestaurantDetailsLTESerializer(serializers.ModelSerializer):
    coupons = RestaurantCouponSerializer(many=True, source='restaurant_counpon_set')  # Đảm bảo lấy tất cả các coupon liên kết
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'address', 'phone_number', 'avatar', 'Oder_online',
            'Takeaway', 'isRate', 'isChat', 'is_active', 'description', 'created_at',
            'coupons', 'address_details'
        ]
    
class RestaurantViewsSerializer(serializers.ModelSerializer):
    coupons = RestaurantCouponSerializer(many=True, source='restaurant_counpon_set')  # Đảm bảo lấy tất cả các coupon liên kết
    layouts = RestaurantLayoutSerializer(many=True, source='restaurant_layout_set')  # Đảm bảo lấy tất cả các layout liên kết
    menu = Restaurant_menuViewSerializer(many=True, source='restaurant_menu_set')  # Đảm bảo lấy tất cả các coupon liên kết
    isLike=serializers.SerializerMethodField(read_only=True)
    totalLike=serializers.SerializerMethodField(read_only=True)
    isFollow=serializers.SerializerMethodField(read_only=True)
    totalFollow=serializers.SerializerMethodField(read_only=True)
    myOrder=serializers.SerializerMethodField(read_only=True)
    mySpace=serializers.SerializerMethodField(read_only=True)
    
    @cached_property
    def user(self):
        return self.context['request'].user
    def get_myOrder(self, obj):
        if self.user.is_authenticated:
            qs_order=Restaurant_order.objects.filter(user_order=self.user,
                                                     restaurant=obj)
            return Restaurant_order_detailsSerializer(qs_order,many=True).data
        return []
    
    def get_mySpace(self, obj):
        if self.user.is_authenticated:
            qs_space=Restaurant_order.objects.filter(user_order=self.user,
                restaurant=obj,is_clear=True,space__isnull=False).exclude(status="CANCEL")
            if len(qs_space)>0:
                return {
                    "space":qs_space[0].space.id,
                    "group":qs_space[0].group.id
                }
            else:
                return False
        return False
    
    def get_totalLike(self, obj):
        return UserLikeLog.objects.filter(
            restaurant_item=obj,
            action_type="like"
        ).count()
    def get_isLike(self, obj):
        if self.user.is_authenticated:
            return UserLikeLog.objects.filter(
                user=self.user,
                restaurant_item=obj,
                action_type="like"
            ).exists()
        return False
    def get_isFollow(self, obj):
        if self.user.is_authenticated:
            return UserLikeLog.objects.filter(
                user=self.user,
                restaurant_item=obj,
                action_type="follow"
            ).exists()
        return False
    def get_totalFollow(self, obj):
        return UserLikeLog.objects.filter(
            restaurant_item=obj,
            action_type="follow"
        ).count()


    class Meta:
        model = Restaurant
        fields = [
            'id', 'name','myOrder', 'address', 'phone_number', 
            'avatar','wallpaper', 'Oder_online','totalLike',
            'Takeaway', 'isRate', 'isChat', 'is_active', 'description', 
            'created_at','totalFollow',
            'coupons', 'address_details','layouts','mohinh',
            'menu','isLike','isFollow','mySpace'
        ]
class RestaurantMenuItemsDetailsSerializer(serializers.ModelSerializer):
    group_names = serializers.SerializerMethodField(read_only=True) #Danh mục trong menu
    mark_names = serializers.SerializerMethodField(read_only=True) #Loại
    restaurant = serializers.SerializerMethodField(read_only=True)
    isLike=serializers.SerializerMethodField(read_only=True)
    totalLike=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Restaurant_menu_items
        fields = ['id','is_ship',
            'menu', 'name', 'price', 'is_hot', 'is_new', 'is_online','is_active',
            'image64_mini', 'image64_full', 'short_description', 'description', 
            'is_available', 'group', 'mark', 'group_names', 'mark_names','image64_sub1',
            'image64_sub2','image64_sub3','restaurant','isLike','totalLike'
        ]
    
    @cached_property
    def user(self):
        return self.context['request'].user
    def get_totalLike(self, obj):
        return UserLikeLog.objects.filter(
            menu_item=obj,
            action_type="like"
        ).count()
    def get_isLike(self, obj):
        if self.user.is_authenticated:
            return UserLikeLog.objects.filter(
                user=self.user,
                menu_item=obj,
                action_type="like"
            ).exists()
        return False
    
    def get_group_names(self, obj):
        return [group.name for group in obj.group.all()]

    def get_mark_names(self, obj):
        return [mark.name for mark in obj.mark.all()]
    
    def get_restaurant(self, obj):
        rest=obj.menu.restaurant
        return RestaurantDetailsLTESerializer(rest,many=False).data
  
class Restaurant_orderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_order
        fields = '__all__'
     
class Restaurant_order_itemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant_order_items
        fields = '__all__'
     
class Restaurant_order_detailsSerializer(serializers.ModelSerializer):
    items = Restaurant_order_itemsSerializer(many=True, source='order_items')
    space_name = serializers.CharField(source='space.name', read_only=True, allow_null=True)
    is_inuse = serializers.CharField(source='space.is_inuse', read_only=True, allow_null=True)
    class Meta:
        model = Restaurant_order
        fields = '__all__'
        
class RestaurantDetailsSerializer(serializers.ModelSerializer):
    sockets = RestaurantSocketSerializer(many=True, source='restaurant_socket_set')  # Đảm bảo lấy tất cả các socket liên kết
    layouts = RestaurantLayoutSerializer(many=True, source='restaurant_layout_set')  # Đảm bảo lấy tất cả các layout liên kết
    coupons = RestaurantCouponSerializer(many=True, source='restaurant_counpon_set')  # Đảm bảo lấy tất cả các coupon liên kết
    menu = Restaurant_menuSerializer(many=True, source='restaurant_menu_set')  # Đảm bảo lấy tất cả các coupon liên kết
    orders = Restaurant_order_detailsSerializer(many=True, source='restaurant_order_set')  # Đảm bảo lấy tất cả các coupon liên kết
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'address', 'phone_number', 'avatar','wallpaper', 'Oder_online','menu',
            'Takeaway', 'isRate', 'isChat', 'is_active', 'description', 'created_at',
            'updated_at', 'sockets', 'layouts', 'coupons', 'address_details','orders'
        ]
    def to_representation(self, instance):
        if instance.restaurant_menu_set.count() == 0:
            menu=Restaurant_menu.objects.create(restaurant=instance,name="Default")
            # Tạo các "mark" (đánh dấu)
            marks = [
                Restaurant_menu_marks(menu=menu, name="Mới"),
                Restaurant_menu_marks(menu=menu, name="Tiêu biểu"),
            ]
            Restaurant_menu_marks.objects.bulk_create(marks)
            # Tạo các "group" (nhóm)
            groups = [
                Restaurant_menu_groups(menu=menu, name="Món chính"),
                Restaurant_menu_groups(menu=menu, name="Món phụ"),
                Restaurant_menu_groups(menu=menu, name="Món gọi thêm"),
                Restaurant_menu_groups(menu=menu, name="Nước uống"),
                Restaurant_menu_groups(menu=menu, name="Ăn vặt"),
                Restaurant_menu_groups(menu=menu, name="Món gọi kèm"),
                Restaurant_menu_groups(menu=menu, name="Khác"),
            ]
            Restaurant_menu_groups.objects.bulk_create(groups)
        return super().to_representation(instance)
  