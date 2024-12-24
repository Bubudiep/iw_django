from django.urls import path, include
from rest_framework import routers
from . import api
router = routers.DefaultRouter()
router.register(r'employee', api.CompanyStaffViewSet, basename='employee')
router.register(r'employee_account', api.CompanyAccountViewSet, basename='employee_account')
router.register(r'department', api.CompanyDepartmentAdminViewSet, basename='department')
router.register(r'jobtitle', api.CompanyPossitionAdminViewSet, basename='jobtitle')
router.register(r'customers', api.CompanyCustomerViewSet, basename='customers')
router.register(r'suppliers', api.CompanySupplierViewSet, basename='suppliers')
router.register(r'vendors', api.CompanyVendorViewSet, basename='vendors')
router.register(r'company', api.CompanyViewSet, basename='company')
router.register(r'operators', api.CompanyOperatorViewSet, basename='operators')
router.register(r'operators_list', api.CompanyOperatorDetailsViewSet, basename='operators_list')
router.register(r'operators_details', api.CompanyOperatorMoreDetailsViewSet, basename='operators_details')
router.register(r'company_sublist', api.CompanySublistViewSet, basename='company_sublist')
urlpatterns = [
    path('my-info/', api.MyInfoAPIView.as_view(), name='my-info'),
    path('search/', api.SearchAPIView.as_view(), name='search'),
    path('login/', api.LoginOAuth2APIView.as_view(), name='login'),
    path('create-fxm/', api.StaffCreateMini.as_view(), name='create-fxm'),
    path('create-employee/', api.RegisterView.as_view(), name='create-employee'),
    path('congty/', api.GetCompanyAPIView.as_view(), name='congty'),
    path('db-employee/', api.GetCompanyDashboardAPIView.as_view(), name='db-employee'),
    path('user/', api.GetUserAPIView.as_view(), name='user'),
    path('', include(router.urls)),
]