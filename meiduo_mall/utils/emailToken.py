from itsdangerous import TimedJSONWebSignatureSerializer as Ser
from meiduo_mall import settings


def generic_email_verify_token(user_id):
    # 1. 创建实例
    s = Ser(secret_key=settings.SECRET_KEY, expires_in=3600)
    # 2. 加密数据
    data = s.dumps({'user_id': user_id})
    # 3. 返回数据
    return data.decode()


def check_verify_token(token):
    # 创建实例
    s = Ser(secret_key=settings.SECRET_KEY, expires_in=3600 * 24)
    # 2. 解密数据 -- 可能有异常
    try:
        result = s.loads(token)
    except Exception as e:
        return None
    # 获取数据
    return result.get('user_id')
