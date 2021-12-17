from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView

urlpatterns = [
    # 用户名校验
    path('usernames/<username>/count/', UsernameCountView.as_view()),
    # 手机号校验
    path('mobiles/<mobile>/count/', MobileCountView.as_view()),

]
