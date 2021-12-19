from django.views import View
from django.http import JsonResponse

from django.core.cache import cache

'''
需求: 
    获取省份信息
前端: 
    当页面加载的时候, 会发送axios请求, 来获取省份信息
后端: 
    请求:         不需要请求参数
    业务逻辑:      查询省份的信息
    响应:         JSON

    路由:     areas/
    步骤: 
        1. 查询省份信息
        2. 返回响应
'''

from apps.areas.models import Area


class AreaView(View):

    def get(self, request):
        # 先查询缓存数据
        province_list = cache.get('province')
        # 如果没有缓存, 则查询数据库, 并缓存数据
        if province_list is None:
            # 1. 查询省份信息
            provinces = Area.objects.filter(parent=None)
            # 2. 序列化省级数据
            province_list = []
            for province_model in provinces:
                province_list.append({
                    'id': province_model.id,
                    'name': province_model.name
                })

            # 保存缓存数据
            cache.set('province', province_list, 24 * 3600)

        # 3. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list
        })


'''
需求: 
    获取市, 区县信息
前端: 
    当页面修改省市的时候, 会发送axios请求, 来获取市, 区县信息
后端: 
    请求:         传递省份id, 市id
    业务逻辑:      根据id查询信息, 将查询结果集转换为字典列表
    响应:         JSON

    路由:     areas/id/
    步骤: 
        # 1. 查询省份信息
        # 2. 将对象转换为字典数据
        # 3. 返回响应
'''


class SubAreaView(View):

    def get(self, request, id):
        # 先获取缓存数据
        data_list = cache.get(f'city:{id}')
        if data_list is None:

            # 1. 查询省份信息
            # Area.objects.filter(parent_id=id)
            # Area.objects.filter(parent=id)
            up_level = Area.objects.get(id=id)
            down_level = up_level.subs.all()
            # 2. 将对象转换为字典数据
            data_list = []
            for item in down_level:
                data_list.append({
                    'id': item.id,
                    'name': item.name
                })
            # 缓存数据
            cache.set(f'city:{id}', data_list, 24 * 3600)
        # 3. 返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sub_data': {
                'subs': data_list
            }
        })


'''
不经常发生变化的数据, 我们最好缓存到redis中, 减少数据库的查询
'''
