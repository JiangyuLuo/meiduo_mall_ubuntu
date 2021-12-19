# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# elery不支持在Windows环境下运行任务, 需要借助eventlet来完成
# 在Ubuntu环境下也需要借助eventlet
# pip install eventlet
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

'''
生产者(任务, 函数)
    @app.task()
    def celery_send_sms_code(mobile, code):
        send_message(1, mobile, (code, 5))

    app.autodiscover_tasks(['celery_tasks.sms'])


消费者()
    celery -A proj worker -l info -P eventlet
    在虚拟环境下执行指令
    celery -A celery实例的脚本路径 worker -l info -P eventlet

队列(中间人, 经纪人)
    # 通过加载配置文件夹设置broker
    app.config_from_object('celery_tasks.config')

    # 配置信息 key=value
    # 我们指定redis为我们的broker(中间人, 经纪人, 队列)
    broker_url = "redis://127.0.0.1:6379/15"  # 端口号不写的话默认为6379

Celery -- 将这3者实现了
    # 0. 为celery的运行 设置Django的环境
    import os
    # 为celery使用django配置文件进行设置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

    # 1. 创建3个实例
    # celery启动文件
    from celery import Celery
    # 参数1: main设置脚本路径就可以了, 脚本路径是唯一的
    app = Celery('celery_tasks')
'''

# 0. 为celery的运行 设置Django的环境
import os

# 为celery使用django配置文件进行设置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 1. 创建3个实例
# celery启动文件
from celery import Celery

# 参数1: main设置脚本路径就可以了, 脚本路径是唯一的
app = Celery('celery_tasks')

# 2. 设置broker
# 通过加载配置文件夹设置broker
app.config_from_object('celery_tasks.config')

# 3. 需要celery自动洁厕指定包的任务
# autodiscover_tasks 参数是列表
# 列表中的元素是tasks的路径
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
