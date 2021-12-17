from django.db import models

# 自己定义的模型
# class User(models.Model):
#     username = models.CharField(max_length=20, unique=True)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=11, unique=True)

# 2. django自带一个用户模型
# 这个用户模型 有密码的加密, 和密码的验证
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # mobile = models.CharField(max_length=11, unique=True)
    # email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
    #                                     on_delete=models.SET_NULL, verbose_name='默认地址')

    # ===============================================================
    # 开发时把手机号换成unique=False
    mobile = models.CharField(max_length=11, unique=False)

    # ===============================================================

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
