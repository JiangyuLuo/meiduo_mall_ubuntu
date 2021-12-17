from django.http import JsonResponse, HttpResponse
from django.views import View

'''
前端： 
    拼接一个ieurl， 然后给img， img会发送请求
    url=http://ip:port/image_codes/uuid/

后端： 
    请求      接收路由中的uuid
    业务逻辑    生成图片验证码和图片二进制。 通过redis把图片验证码保存起来
    响应      返回图片二进制

    路由: GET image_codes/uuid/
    步骤： 
        1. 接收路由中的uuid
        2. 生成图片验证码和图片二进制
        3. 通过redis把图片验证码保存起来
        4. 返回图片二进制

'''


class ImageCodeView(View):
    def get(self, request, uuid):
        # 1. 接收路由中的uuid
        # 2. 生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 是图片验证码的内容 例如： xyzz
        # image是图片二进制
        text, image = captcha.generate_captcha()
        # 3. 通过redis把图片验证码保存起来
        # 3.1 进行redis链接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 指令操作
        # name, time, value
        redis_cli.setex(uuid, 100, text)
        # 4. 返回图片二进制
        # 因为图片是二进制， 我们不能返回JSON数据
        # content_type的语法形式是： 大类/小类
        # 图片： image/jped, image/gif, image/png
        # print('===================text==================', text)
        return HttpResponse(image, content_type='image/jpeg')


'''
前端：     
        当用户输入完手机号， 验证码之后， 前端发送一个axios请求
        /sms_codes/15839388864/?image_code=3HCY&image_code_id=c97d3197-923d-45a7-95b5-8bc311cef51e

后端： 
        请求： 接受请求， 获取请求参数（路由有手机号， 用户的图片验证码和UUID在查询字符串中）
        业务逻辑： 验证参数， 验证图片验证码， 生成短信验证码， 保存短信验证码， 发送短信验证码
        响应： 返回响应 {'code': 0, '': 'ok'}

        路由：GET /sms_codes/15839388864/?image_code=3HCY&image_code_id=c97d3197-923d-45a7-95b5-8bc311cef51e
        步骤: 
                1. 接收请求参数
                2. 验证参数
                3. 验证图片验证码
                4. 生成短信验证码
                5. 保存短信验证码
                6. 发送短信验证码
                7. 返回响应

debug模式 就是调试模式
debug + 断点配合使用 这个我们看到的过程
添加断点 在函数体的第一行添加
'''


class SMSCodeView(View):

    def get(self, request, mobile):
        # print(mobile)
        # 1. 接收请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2. 验证参数
        if not all([image_code, uuid]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数不全'
            })
        # 3. 验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.1 获取redis数据
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({
                'code': 400,
                'errmsg': '图片验证码已过期'
            })
        # 3.3 对比
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({
                'code': 400,
                'errmsg': '图片验证码错误'
            })
        # 提取发送信息的标记, 看看有没有
        send_flag = redis_cli.get(f'send_flag_{mobile}')
        if send_flag is not None:
            return JsonResponse({
                'code': 400,
                'errmsg': '不要频繁发送短信'
            })

        # 4. 生成短信验证码
        from random import randint
        sms_code = '%06d' % randint(0, 999999)

        # 管道3步
        # a. 新建一个管道, 创建Redis管道
        pipeline = redis_cli.pipeline()
        # b. 管道收集指令, 将Redis请求添加到队列
        pipeline.setex(mobile, 5 * 60, sms_code)
        # 添加一个发送标记, 有效期60秒, 内容什么都可以
        pipeline.setex(f'send_flag_{mobile}', 60, 1)

        # c. 管道执行指令
        pipeline.execute()

        # print(sms_code)
        #### 用pipline收集指令一并发送, 提高服务器的利用率, 减小服务器的压力
        # # 5. 保存短信验证码
        # redis_cli.setex(mobile, 5*60, sms_code)
        # # 添加一个发送标记, 有效期60秒, 内容什么都可以
        # redis_cli.setex(f'send_flag_{mobile}', 60, 1)
        # 6. 发送短信验证码
        # from utils.sms_sender import send_message
        # send_message(1, mobile, (sms_code, 5))
        #### Celery优化信息发送
        from celery_tasks.sms.tasks import celery_send_sms_code
        # delay的参数 等同于 任务(函数)的参数
        celery_send_sms_code.delay(1, mobile, (sms_code, 5))
        # 7. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'OK'
        })


'''
生产者
消费者
队列(中间人, 经纪人)
Celery -- 将这三者实现了
'''


