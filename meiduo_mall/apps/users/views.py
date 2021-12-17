from django.views import View
from apps.users.models import User
from django.http import JsonResponse

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