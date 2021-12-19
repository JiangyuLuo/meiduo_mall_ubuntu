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


'''
需求:     1. 保存邮箱地址 2. 发送一份激活邮件   3. 用户激活邮件
前端:     
    当用户输入邮箱之后, 点击保存, 这个时候会发送ajax请求

后端: 

    请求:
    业务逻辑:
    响应: 

    路由      PUT
    步骤: 
        1. 接受请求
        2. 获取数据
        3. 保存邮箱地址
        4. 发送一份激活邮箱
        5. 返回响应

需求(要实现什么功能)  ==> 思路(请求, 业务逻辑, 响应)  ==> 步骤  ==> 代码实现
'''


class EmailView(LoginRequiredJsonMixin, View):

    def put(self, request):
        # 1. 接受请求
        # put post == body
        data = json.loads(request.body.decode())
        # 2. 获取数据
        email = data.get('email')
        # 验证数据
        # 正则

        # 3. 保存邮箱地址
        user = request.user
        # user/ request.user 就是登录用户的实例对象
        user.email = email
        user.save()

        # 4. 发送一份激活邮箱
        from django.core.mail import send_mail
        # subject: 主题
        # message: 信息内容
        # from_email: 发件人
        # recipient_list: 收件人列表
        subject = '主题'
        message = '稀土的招聘方式https://xitu.juejin.cn/jobs'
        from_email = 'liqipython@163.com'
        recipient_list = ['943215317@qq.com', ]

        # 4.1 对a标签的连接数据进行加密处理
        # user_id=1
        from utils.emailToken import generic_email_verify_token
        token = generic_email_verify_token(request.user.id)

        # 4.2 阻止我们的激活邮件
        # 如果邮件的内容是html这个时候使用html_message
        verify_url = f"http://www.geekshub.com:8080/success_verify_email.html?token={token}"
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s</a></p>' % (email, verify_url, verify_url)

        # send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, html_message=html_message)
        # 换成celery方法
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
                                html_message=html_message)
        # 5. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


'''
    1. 设置邮件服务器

    2. 设置邮件发送的配置信息(写在settings.py中)
        # 让django的哪个类发送邮件
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        # EMAIL_USE_TLS = False   #是否使用TLS安全传输协议(用于在两个通信应用程序之间提供保密性和数据完整性。)
        # EMAIL_USE_SSL = True    #是否使用SSL加密，qq企业邮箱要求使用
        EMAIL_HOST = 'smtp.163.com'   #发送邮件的邮箱 的 SMTP服务器，这里用了163邮箱
        EMAIL_PORT = 25     #发件箱的SMTP服务器端口
        EMAIL_HOST_USER = 'liqipython@163.com'    #发送邮件的邮箱地址
        EMAIL_HOST_PASSWORD = 'IJJMDXGHZPZEQBES'         #发送邮件的邮箱密码(这里使用的是授权码)
        # EMAIL_FROM = '罗大富<liqipython@163.com>'

    3. 调用 send_mail方法
'''

'''
需求: 
    激活用户的邮件
前端: 
    用户会点击那个激活连接. 那个激活连接携带了token
后端: 
    请求:     接收请求, 获取参数, 验证参数
    业务逻辑:   user_id, 根据用户id查询数据, 修改数据
    响应:     返回响应JSON

    路由:     PUT     emails/verification/ 说明token并没有在body里
    步骤: 
        1. 接收请求
        2. 获取参数
        3. 验证参数
        4. 获取user_id
        5. 根据用户id查询数据
        6. 修改数据
        7. 返回响应

'''


class EmailVerifyView(View):

    def put(self, request):
        # 1. 接收请求
        params = request.GET
        print(params)
        # 2. 获取参数
        token = params.get('token')
        # 3. 验证参数
        if token is None:
            return JsonResponse({
                'code': 400,
                'errmsg': '参数缺失'
            })
        # 4. 获取user_id
        from utils.emailToken import check_verify_token
        user_id = check_verify_token(token)
        print('USER_ID: ', user_id)
        if user_id is None:
            return JsonResponse({
                'code': 400,
                'errmsg': '参数错误'
            })
        # 5. 根据用户id查询数据
        user = User.objects.get(id=user_id)
        print('USER: ', user)
        # 6. 修改数据
        user.email_active = True
        user.save()
        # 7. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


'''
需求: 
    新增地址

前端: 
        当用户完成地址信息后, 前端应该发送一个axios请求, 会携带相关信息(POST -- body)

后端: 
    请求:         接收请求, 获取参数
    业务逻辑:      数据入库
    响应:         返回响应

    路由:     POST    /addresses/create/
    步骤: 
        1. 接收请求
        2. 获取参数, 验证参数
        3. 数据入库
        4. 返回响应
'''

from apps.users.models import Address


class AddressCreateView(LoginRequiredJsonMixin, View):

    def post(self, request):
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取参数, 验证参数
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        user = request.user
        # 验证参数
        # 2.1 验证必传参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        # 2.2 省市区的ID是否正确
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        # 2.3 详细地址的长度
        # 2.4 手机号
        # 2.5 固定电话
        # 2.6 邮箱
        # 3. 数据入库
        address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        # 新增地址成功, 将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 4. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': '新增地址成功',
            'address': address_dict
        })


# 对个人地址的增删改查
class AddressView(View):

    # 获取地址
    def get(self, request):
        # 1. 接收请求
        user = request.user
        # addresses = user.addresses
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 2. 获取参数, 验证参数
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        # 3. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'addresses': address_list
        })

    # 修改地址
    def put(self, request, address_id):
        # 1. 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2. 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})

        # 3. 判断地址是否存在并更新地址信息
        Address.objects.filter(id=address_id).update(
            user=request.user,
            # title没有更新的必要
            # title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )
        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({
            'code': 0,
            'errmsg': '更新地址成功',
            'address': address_dict
        })

    # 删除地址
    def delete(self, request, address_id):
        # 查询要删除的地址
        address = Address.objects.get(id=address_id)

        # 将地址逻辑删除设置为True
        address.is_deleted = True
        address.save()

        # 响应删除地址的结果
        return JsonResponse({
            'code': 0,
            'errmsg': '删除地址成功'
        })



# 设置默认地址
class DefaultAddressView(LoginRequiredJsonMixin, View):

    def put(self, request, address_id):
        '''设置默认地址'''
        # 1. 接收参数,查询地址
        address = Address.objects.get(id=address_id)

        # 2. 设置地址为默认地址
        request.user.default_address = address
        request.user.save()

        # 响应设置默认地址结果
        return JsonResponse({
            'code': 0,
            'errmsg': '设置默认地址成功'
        })


# 修改密码
class ChangePasswordView(LoginRequiredJsonMixin, View):

    def put(self, request):
        # 接收参数
        dict = json.loads(request.body.decode())
        old_password = dict.get('old_password')
        new_password = dict.get('new_password')
        new_password2 = dict.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数'
            })

        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({
                'code': 400,
                'errmsg': '原始密码不正确'
            })

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码最少8位, 最长20位'
            })
        if new_password != new_password2:
            return JsonResponse({
                'code': 400,
                'errmsg': '两次输入密码不一致'
            })
        # 验证密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'errmsg': 'OK'
            })

        # 清理状态保持信息
        logout(request)

        response = JsonResponse({
            'code': 0,
            'errmsg': 'OK'
        })
        response.delete_cookie('username')

        # 密码修改成功, 重定向到登录页面
        return response


# 修改地址标题
class UpdateTitleAddressView(LoginRequiredJsonMixin, View):

    def put(self, request, address_id):
        '''设置地址标题'''
        # 接收参数: 地址标题
        title = json.loads(request.body.decode()).get('title')
        address = Address.objects.get(id=address_id)
        print(address.title)
        address.title = title
        address.save()

        return JsonResponse({
            'code': 0,
            'errmsg': 'OK'
        })

