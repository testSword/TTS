import json
import logging
import random

from django.http import request, JsonResponse

# Create your views here.
# coding:utf-8
from common.Log import logger
from common.http_resp import resp
from mock.models import Mock_interfaces, Mock_lists

'''
1、提供接口查询能力
2、提供mock接口添加能力
3、提供mock接口更新能力
4、提供mock接口删除能力
5、提供mock数据添加能力
6、提供mock数据编辑能力
7、提供mock数据删除能力
8、提供mock数据打散（随机能力）
9.批量导入接口

'''


# 总的mock入口，所有的第三方请求会有nginx重定向到该接口，由该接口返回对应的响应mock
def mock_tts(request):
    if request.method in ["GET", "POST"]:
        # GET请求
        req_data = request.body.decode("utf8")
        # 处理请求头里的Referer参数获取原始的请求路径----注意：端口好8101为nginx配置的监听转发的端口号，两边需保持同步
        req_path = request.headers["Referer"].split("8101")[-1]
        if req_path.endswith("/"):
            req_path=req_path[:-1]
        logger.info("请求路径：{}".format(req_path))
        logger.info("请求参数：{}".format(req_data))
        # 返回数据
        try:
            interface = Mock_interfaces.objects.filter(interface_url=req_path).filter(is_delete=0)
            if len(interface) > 0:
                interface_mock = interface[0].interface_mock_id
                # 如果mock_id为0,则随机返回
                if interface_mock == 0:
                    mock_lists = Mock_lists.objects.filter(mock_interface_id=interface.id).filter(is_delete=0)
                    mock_data_list = []
                    for item in mock_lists:
                        mock_data_list.append(item.mock_data)
                    interface_mock_data = random.choice(mock_data_list)
                # 否则根据mock_id返回对应的mock_data
                else:
                    interface_mock_datas = Mock_lists.objects.filter(id=interface_mock).filter(is_delete=0)
                    if len(interface_mock_datas)>0:
                        interface_mock_data=interface_mock_datas[0].mock_data
                    else:
                        return JsonResponse({"message": "id为{}的mock规则不存在".format(interface_mock), "code": 100002})
                # 根据请url返回对应的mock
                return JsonResponse(json.loads(interface_mock_data))
            else:
                return JsonResponse({"message": "该接口未维护", "code": 100001})
        except Exception as e:
            logger.error(e)
            return JsonResponse({"message": "服务异常", "code": 500})


# 查询接口
def select_mock_interface(request):
    reqdata = json.loads(request.body.decode("utf8"))
    # 参数：查询域里的查询字段；
    # 入参：查询字段，分页条数。如果不传，默认查10条，排序为按创建时间倒叙
    interface_lists = []
    '''
    {
        "service_name":"",
        "interface_name":"",
        "interface_path":"",
        "page":"",
        "page_num":"",
    }
    '''
    if "page" in reqdata.keys() and "page_num" in reqdata.keys():
        page = reqdata["page"]
        page_num = reqdata["page_num"]
    else:
        page = 1
        page_num = 10
    try:
        # 如果传过来的字段包含"service_name"
        if "service_name" in reqdata.keys():
            logger.info(reqdata["service_name"])
            interface_list = Mock_interfaces.objects.filter(service_name=reqdata["service_name"])
            all_counts = len(interface_list)
            # 分页
            if all_counts - ((page - 1) * page_num) < page_num:
                interface_list = interface_list[(page - 1) * page_num:]
            elif all_counts - ((page - 1) * page_num) >= page_num:
                interface_list = interface_list[(page - 1) * page_num, page_num]

        # 如果传过来的字段包含"interface_name"
        if "interface_name" in reqdata.keys():
            interface_list = Mock_interfaces.objects.filter(interface_name = reqdata["interface_name"])
            all_counts = len(interface_list)
            # 分页
            if all_counts - ((page - 1) * page_num) < page_num:
                interface_list = interface_list[(page - 1) * page_num:]
            elif all_counts - ((page - 1) * page_num) >= page_num:
                interface_list = interface_list[(page - 1) * page_num, page_num]
        # 如果传过来的字段包含"interface_path"
        if "interface_path" in reqdata.keys():
            interface_list = Mock_interfaces.objects.filter(interface_url = reqdata["interface_path"])
            all_counts = len(interface_list)
            # 分页
            if all_counts-((page - 1) * page_num) <page_num:
                interface_list=interface_list[(page - 1) * page_num:]
            elif all_counts-((page - 1) * page_num) >=  page_num:
                interface_list=interface_list[(page - 1) * page_num, page_num]

        for item in interface_list:
            interface = {
                "service_name": item.service_name,
                "interface_name": item.interface_name,
                "interface_path": item.interface_url,
            }
            interface_lists.append(interface)

        res_data={
            "counts":all_counts,
            "interface_lists":interface_lists
        }
        res = resp.Resp(data=res_data)
        return JsonResponse(res)

    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "系统异常", "code": 500})


# 1、提供mock接口添加能力
def add_mock_interface(request):
    reqdata = request.json
    '''
    {
        "service_name":"",
        "interface_name":"",
        "interface_path":"",
    }
    '''
    service_name = reqdata["service_name"]
    interface_name = reqdata["interface_name"]
    interface_path = reqdata["interface_path"]
    interface = Mock_interfaces(service=service_name, interface_name=interface_name, interface_path=interface_path)

    res = resp.Resp(data="添加成功")
    return res


# 1、提供mock接口更新能力
def update_mock_interface():
    reqdata = request.json
    return "reqdata"


# 1、、提供mock接口删除能力

def delete_mock_interface():
    reqdata = request.json

    return "reqdata"


# 5、提供mock数据添加能力

def add_mock_data():
    reqdata = request.json

    return "reqdata"


# # # 6、提供mock数据编辑能力

def edit_mock_data():
    reqdata = request.json

    return "reqdata"


# # # 7、提供mock数据删除能力
def delete_mock_data():
    reqdata = request.json

    return "reqdata"


# # # 8、提供mock数据打散（随机能力）
def shuffle_mock_data():
    reqdata = request.json
    return "reqdata"


# # # 8、确认mock数据数据（指定mock数据）
def shuffle_mock_data():
    '''
    params:接口path、mockdata编号（yaml文件里的data的index）；
    :return:
    '''
    reqdata = request.json
    return "reqdata"
