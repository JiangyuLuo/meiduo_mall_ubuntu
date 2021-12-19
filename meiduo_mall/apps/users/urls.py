from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, RegisterView, LoginView, LogoutView, CenterView, \
    EmailVerifyView, EmailView, AddressCreateView, AddressView, DefaultAddressView, UpdateTitleAddressView, ChangePasswordView

urlpatterns = [
    # 用户名校验
    path('usernames/<username>/count/', UsernameCountView.as_view()),
    # 手机号校验
    path('mobiles/<mobile>/count/', MobileCountView.as_view()),
    # 注册
    path('register/', RegisterView.as_view()),
    # 登录
    path('login/', LoginView.as_view()),
    # 退出
    path('logout/', LogoutView.as_view()),
    # 用户基本信息
    path('info/', CenterView.as_view()),
    # 验证邮箱
    path('emails/', EmailView.as_view()),
    path('emails/verification/', EmailVerifyView.as_view()),
    # 创建新地址
    path('addresses/create/', AddressCreateView.as_view()),
    # 加载地址信息
    path('addresses/', AddressView.as_view()),
    # 删除和修改都是该接口, 但是请求方法不同
    path('addresses/<address_id>/', AddressView.as_view()),
    # 设置默认地址
    path('addresses/<address_id>/default/', DefaultAddressView.as_view()),
    # 修改地址标题
    path('addresses/<address_id>/title/', UpdateTitleAddressView.as_view()),
    # 修改密码
    path('password/', ChangePasswordView.as_view()),

]
