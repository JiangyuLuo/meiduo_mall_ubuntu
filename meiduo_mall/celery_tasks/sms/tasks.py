# 生产者 -- 任务, 函数
# 1. 这个函数必须要让celery的实例的task装饰器装饰
# 2. 需要celery自动检测指定包的任务
from ronglian_sms_sdk import SmsSDK
from celery_tasks.main import app


@app.task()
def celery_send_sms_code(tid, mobile, datas):
    '''

        :param tid: 容联云通讯创建的模板
        :param mobile: 手机号
        :param datas: sms_code和有效时间, 元组或列表
        :return: None
        '''
    # accId = '容联云通讯分配的主账号ID'
    accId = '8a216da8762cb4570176a1e566f42a15'
    # accToken = '容联云通讯分配的主账号TOKEN'
    accToken = '88a3e1f036604961a26046513fcad6b9'
    # appId = '容联云通讯分配的应用ID'
    appId = '8a216da8762cb4570176a1e567d52a1c'

    sdk = SmsSDK(accId, accToken, appId)
    # tid = '容联云通讯创建的模板'
    resp = sdk.sendMessage(tid, mobile, datas)
    # print(resp)