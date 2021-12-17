import json, re

from django.views import View
from apps.users.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django_redis import get_redis_connection

'''
判断用户名是否重复的功能
前端: 当用户输入用户名之后, 失去焦点, 发送一个异步请求,一般用axios
后端(思路): 
    请求: 接收用户名
    业务逻辑: 
        根据用户名查询数据库, 如果查询结果熟练等于0, 说明没有注册
        如果查询结果数量等于1, 说明有注册
    响应: JSON
        {code: 0, count: 0/1, errmsg: ok}

    路由  GET usernames/<username>/count
    步骤:  
        1. 接收用户名
        2. 根据用户名查询数据库
        3. 返回响应
'''


class UsernameCountView(View):

    def get(self, request, username):
        # 1. 接受用户名, 对这个用户名进行判断, 减少对数据库的请求次数
        # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({
        #         'code': 200,
        #         'errmsg': '用户名不满足需求'
        #     })
        # 2. 根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        # 3. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'OK',
            'count': count
        })


# 检查手机号是否存在
class MobileCountView(View):
    def get(self, request, mobile):
        '''
        判断手机号是否重复注册

        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        '''
        # 根据用户名查询数据库
        count = User.objects.filter(mobile=mobile).count()
        # 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'OK',
            'count': count
        })


'''
我们不相信前端提交的任何数据！！！因此前后端都需要验证数据
前端： 当用户输入用户名， 密码， 确认密码， 手机号， 同意之后， 点击注册按钮
    前端发起axios请求

后端： 
    请求: 接受请求（JSON），获取数据
    业务逻辑：验证数据， 数据入库
    响应： JSON {'code': 0, 'errmsg': 'ok}

    路由：POST register/
    步骤： 
        1. 接受请求（POST --- JSON)
        2. 获取数据
        3. 验证数据
            3.1 用户名， 密码， 确认密码， 手机号， 同意
            0表示成功， 400表示失败
            3.2 用户名满足规则， 用户名不能重复
            3.3 密码满足规则
            3.4 确认密码和密码要一致
            3.5 手机号满足规则， 手机号也不能重复
            3.6 需要统一协议
        4. 数据入库
        5. 返回响应
'''


class RegisterView(View):

    def post(self, request):
        # 1.接受请求（POST - -- JSON)
        # print('request POST: ', request.POST)
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)
        # 2.获取数据
        # username = body_dict['']  # 程序如果出现问题， 不会抛出异常， 因此最好使用get方法
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        sms_code = body_dict.get('sms_code')
        # 3.验证数据
        #   3.1 用户名， 密码， 确认密码， 手机号， 同意
        # all([xxx])
        # all就返回False, 否则就返回True
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        #   3.2 用户名满足规则， 用户名不能重复
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        #   3.3 密码满足规则, 判断密码是否是8-20
        if not re.match('^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': 'password格式有误！'})
        #   3.4 确认密码和密码要一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码不一致'})
        #   3.5 手机号满足规则， 手机号也不能重复
        if not re.match('^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': 'mobile格式有误！'})
        #   3.6 需要统一协议， 判断是否勾选用户协议
        if allow != True:
            return JsonResponse({'code': 400, 'errmsg': 'allow格式有误'})
        # 3.7 判断短信验证码是否正确: 跟图形验证码的验证一样的逻辑
        # 3.7.1 提取服务端存储的短信验证码: 以前怎么存储, 现在就怎么提取
        # redis_cli = get_redis_connection('code')
        # sms_code_server = redis_cli.get(mobile)
        # redis_conn = get_redis_connection('verify_code')
        # print(mobile, type(mobile))
        # print('sms_code: ', sms_code, '\n sms_code_redis: ', sms_code_server)
        # 4. 数据入库
        # ##方法1
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()
        #
        # ## 方法2
        # User.objects.create(username=username,
        #                     password=password,
        #                     mobile=mobile)

        # 以上两种方法都可以数据入库，但是有一个问题: 密码没有加密
        # 这种方法注册用户， 密码就加密了
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)
        # print(user)
        # Django为我们提供了 状态保持 的方法
        from django.contrib.auth import login
        login(request, user)
        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK'})


'''
如果需求是注册成功后即表示用户认证通过，那么此时可以在注册成功后实现状态保持（注册成功即已经登陆，用户方便的角度）
如果需求是注册成功后不表示用户认证通过， 那么此时不用在注册成功后实现状态保持（注册成功， 单独登录）

实现状态保持主要有两种方式：
    在客户端存储信息使用Cookie
    在服务器端存储信息使用Session
'''

'''
登录

前端: 
    当用户把用户名和密码输入完成后, 会点击登录按钮. 这个时候前端应该发送一个axios请求

后端: 
    请求: 接收数据, 验证数据
    业务逻辑: 验证用户名和密码是否正确, session
    响应: 返回JSON数据 0成功, 400失败

    POST        /login/
步骤: 
    1. 接收数据
    2. 验证数据
    3. 验证用户名和密码是否正确
    4. session
    5. 判断是否记住登录
    6. 返回响应

'''


class LoginView(View):

    def post(self, request):
        # 1. 接收数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 2. 验证数据
        if not all([username, password]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数不全'
            })

        # # 确定 我们是根据手机号查询 还是根据用户名查询
        # # USERNAME_FIELD 我们可以根据修改User. USERNAME_FIELD字段
        # # 来影响authenticate的查询
        # # authenticate就是根据USERNAME_FIELD来查询
        # if re.match('1[3-9]\d{9}', username):
        #     User.USERNAME_FIELD = 'mobile'
        # else:
        #     User.USERNAME_FIELD = 'username'

        # 3. 验证用户名和密码是否正确
        # 方式一 我们可以通过模型根据用户名来查询
        ## User.objects.get(username=username)
        # 方式二
        from django.contrib.auth import authenticate
        # authenticate 传递用户名和密码
        # 如果用户名和密码正确, 则返回User信息
        # 如果用户名和密码不正确, 则返回None
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({
                'code': 400,
                'errmsg': '账号或密码错误'
            })
        # 4. session
        from django.contrib.auth import login
        login(request, user)
        # 5. 判断是否记住登录
        if remembered:
            # 记住登录  -- 两周或者一个月 产品说了算
            request.session.set_expiry(None)
        else:
            # 不记住登录 -- 浏览器关闭 session过期
            request.session.set_expiry(0)
        # 6. 返回响应
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })

        # 为了首页显示用户信息
        response.set_cookie('username', username)
        return response


'''
退出登录

前端: 
        当用户点击退出按钮的时候, 前端发送一个axios delete请求
后端: 
        请求: 
        业务逻辑:   退出
        响应:     返回JSON数据

        DELETE      /logout/

'''
from django.contrib.auth import logout


class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response

# 用户中心, 也必须是登录用户
'''
LoginRequiredMixin 未登录的用户 会返回重定向. 重定向并不是JSON数据
我们需要是 返回JSON数据

'''
# 第一种方式
# 修改LoginRequiredMixin源代码
from django.contrib.auth.mixins import LoginRequiredMixin


# from django.contrib.auth.mixins import AccessMixin

# class LoginRequiredJsonMixin(AccessMixin):
#     """Verify that the current user is authenticated."""
#
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'code': 400, 'errmsg': '没有登录'})
#         return super().dispatch(request, *args, **kwargs)

# 第二种, 只覆盖相关方法
# 封装一个新的类, 继承重写
class LoginRequiredJsonMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '没有登录'})


class CenterView(LoginRequiredJsonMixin, View):

    def get(self, request):
        # request.user 就是已经登录的用户信息
        info_data = {
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active,
        }

        return JsonResponse({
            'code': 0,
            'errmsg': 'OK',
            'info_data': info_data
        })
