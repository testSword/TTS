import json
import logging
import os
import random

from django.http import request, JsonResponse

# Create your views here.
# coding:utf-8
from common.Log import logger
from common.http_resp import resp
from interface_define.Validation_interface import validate_interface
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
            req_path = req_path[:-1]
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
                    if len(interface_mock_datas) > 0:
                        interface_mock_data = interface_mock_datas[0].mock_data
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
        "service_name":"",  //非必输
        "interface_name":"", //非必输
        "interface_path":"",  //非必输
        "page":"",   //非必输
        "page_num":"",   //非必输
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

        # 如果传过来的字段包含"interface_name"
        elif "interface_name" in reqdata.keys():
            interface_list = Mock_interfaces.objects.filter(interface_name=reqdata["interface_name"])
            all_counts = len(interface_list)

        # 如果传过来的字段包含"interface_path"
        elif "interface_path" in reqdata.keys():
            interface_list = Mock_interfaces.objects.filter(interface_url=reqdata["interface_path"])
            all_counts = len(interface_list)

        # 如果传过来的值为空，则默认查询所有
        else:
            interface_list = Mock_interfaces.objects.all()
            all_counts = len(interface_list)
        # 分页
        if all_counts - ((page - 1) * page_num) < page_num:
            interface_list = interface_list[(page - 1) * page_num:]
        elif all_counts - ((page - 1) * page_num) >= page_num:
            interface_list = interface_list[(page - 1) * page_num, page_num]

        for item in interface_list:
            interface = {
                "service_name": item.service_name,
                "interface_name": item.interface_name,
                "interface_path": item.interface_url,
                "interface_id":item.id
            }
            interface_lists.append(interface)

        res_data = {
            "counts": all_counts,
            "interface_lists": interface_lists
        }
        res = resp.Resp(data=res_data)
        return JsonResponse(res)

    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "{}".format(e), "code": 999999})


# 提供mock接口添加能力
def add_mock_interface(request):
    reqdata = json.loads(request.body.decode("utf8"))
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
    try:
        interface = Mock_interfaces(service_name=service_name, interface_name=interface_name, interface_url=interface_path)
        interface.save()
        res = resp.Resp(data="添加成功")
        return JsonResponse(res)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message":"{}".format(e), "code": 999999})



# 1、提供mock接口更新能力,根据接口id跟新

def update_mock_interface(request):
    reqdata = json.loads(request.body.decode("utf8"))
    '''
        {
            "interface_id":""//必传
            "service_name":"", //必传
            "interface_name":"", //必传
            "interface_path":"", //必传
        }
        '''
    logger.info(reqdata)
    keyword=["interface_id","service_name","interface_name","interface_path"]
    for key in keyword:
        if key not in reqdata.keys():
            return JsonResponse(resp.error(code="999999",message="缺失必需字段{}".format(key)))
        if reqdata[key] == "":
            return JsonResponse(resp.error(code="99999", message="{}字段不能为空".format(key)))

    interface_list = Mock_interfaces.objects.filter(id=reqdata["interface_id"])
    if not interface_list:
        return JsonResponse(resp.error(message="接口不存在或已被删除"))
    if Mock_interfaces.objects.filter(interface_url=reqdata["interface_path"]) and Mock_interfaces.objects.filter(
        interface_url=reqdata["interface_path"]).first().id !=reqdata["interface_id"]:
        return JsonResponse(resp.error(code="99999", message="已存在相同接口路径{}".format(reqdata["interface_path"])))
    try:
        interface=interface_list.first()
        interface.service_name=reqdata["service_name"]
        interface.interface_name=reqdata["interface_name"]
        interface.interface_url=reqdata["interface_path"]
        interface.save()
        return JsonResponse(resp.Resp())
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "{}".format(e), "code": 999999})

# 1、、提供mock接口删除能力
def delete_mock_interface(request):
    reqdata = json.loads(request.body.decode("utf8"))
    '''
        {
            "interface_id":""//必传
        }
        '''
    logger.info("reqdata:{}".format(reqdata))
    if "interface_id" in reqdata.keys() and reqdata["interface_id"]  !=None:
        interface=Mock_interfaces.objects.filter(id=reqdata["interface_id"])
        if interface:
            interface[0].is_delete=1
            interface[0].save()
        return JsonResponse(resp.Resp())
    else:
        return JsonResponse(resp.error(message="interface_id缺失或为空"))


@validate_interface(service="mock",interface_name="select_mock_data")
def select_mock_data(request):
    reqdata = json.loads(request.body.decode("utf8"))
    "根据接口id查对应的mock数据"
    '''
     "mock_interface_id":"",
    '''
    mock_data_list=Mock_lists.objects.filter(mock_interface_id=reqdata["mock_interface_id"])
    # 返回的mock数据为：mock_list
    mock_list=[]
    try:
        for item in mock_data_list:
            mock={
                "mock_interface_id":item.mock_interface_id,
                "mock_name": item.mock_name,
                "mock_data": item.mock_data,
                "mock_id":item.id
            }
            mock_list.append(mock)
    except Exception as e:
        logger.info(e)
    ##查询当前启用的mock数据
    if Mock_interfaces.objects.filter(id=reqdata["mock_interface_id"]):
        now_mock_id=Mock_interfaces.objects.filter(id=reqdata["mock_interface_id"])[0].interface_mock_id
        resp_data={
            "now_mock_id":now_mock_id,
            "mock_list":mock_list
        }
        return JsonResponse(resp.Resp(data=resp_data))
    else:
        return JsonResponse(resp.error(message="该接口不存在或已删除"))

# 5、提供mock数据添加能力
def add_mock_data(request):
    reqdata = json.loads(request.body.decode("utf8"))
    '''
        {
            "mock_name":"",
            "mock_data":"",
            "mock_interface_id":"",
        }
        '''
    # 判断字段是都存在，字段都必需
    keyword = ["mock_name", "mock_data", "mock_interface_id"]
    for key in keyword:
        if key not in reqdata.keys():
            return JsonResponse(resp.error(code="999999", message="缺失必需字段{}".format(key)))
        if reqdata[key] == "":
            return JsonResponse(resp.error(code="99999", message="{}字段不能为空".format(key)))

    # 判断如果该接口存在相同mockname的数据，就返回报错
    # 判断该接口mock是否存在
    if Mock_interfaces.objects.filter(id=reqdata["mock_interface_id"]).filter(is_delete=0):
        mock_list= Mock_lists.objects.filter(mock_interface_id=reqdata["mock_interface_id"])
        if mock_list.filter(mock_name=reqdata["mock_name"]).filter(is_delete=0):
            return JsonResponse(resp.error(code="110001",message="已有相同mock名称的mock数据"))
        try:
            mock = Mock_lists(mock_name=reqdata["mock_name"], mock_data=reqdata["mock_data"],
                                        mock_interface_id=reqdata["mock_interface_id"])
            mock.save()
            res = resp.Resp(data="添加成功")
            return JsonResponse(res)
        except Exception as e:
            logger.error(e)
            return JsonResponse({"message": "{}".format(e), "code": 999999})
    else:
        return JsonResponse(resp.error(code="1000002",message="该mock接口不存在或已删除,无法添加mock"))

# # # 6、提供mock数据编辑能力
def edit_mock_data(request):
    reqdata = json.loads(request.body.decode("utf8"))
    '''
        {
            "mock_name":"",
            "mock_data":"",
            "mock_interface_id":"",
        }
        '''
    # 判断字段是都存在，字段都必需
    keyword = ["mock_name", "mock_data", "mock_interface_id"]
    for key in keyword:
        if key not in reqdata.keys():
            return JsonResponse(resp.error(code="999999", message="缺失必需字段{}".format(key)))
        if reqdata[key] == "":
            return JsonResponse(resp.error(code="99999", message="{}字段不能为空".format(key)))

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
def confirm_mock_data():
    '''
    params:接口path、mockdata编号（yaml文件里的data的index）；
    :return:
    '''
    reqdata = request.json
    return "reqdata"
