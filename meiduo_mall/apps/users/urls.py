from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, RegisterView, LoginView, LogoutView

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

]
