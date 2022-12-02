#coding:utf8
'''
本方法提供全局统一的接口入参合法性检验装饰器：字段必输性校验，字段类型校验
接口入参规范编写文档命名：interface_define/模块名_interface_define

'''
import json
from functools import wraps
from django.http import JsonResponse
from TTS.settings import MOCK
from common.Log import logger
from common.http_resp import resp


def validate_interface(service,interface_name):
    def wrapper(func):
        @wraps(func)
        def validate(request,*args, **kwargs):
            if service == "mock":
                interface_rule=MOCK[interface_name]
            reqdata = request.POST
            logger.info(reqdata)
            #根据服务名以及接口名获取接口入参规则（是否必输，以及字段类型）：
            # 找到必须字段
            keyword=[]
            # 字段必属性校验
            for item in interface_rule.keys():
                if interface_rule[item]["is_need"] == 0:
                    keyword.append(item)
            for key in keyword:
                if key not in reqdata.keys():
                    return JsonResponse(resp.error(code="999999", message="缺失必需字段{}".format(key)))
                if reqdata[key] == "":
                    return JsonResponse(resp.error(code="99999", message="{}字段不能为空".format(key)))
            # # 字段类型入参校验,取出req里的所有参数去匹配interface_rule里的参数类型
            # for item in reqdata.keys():
            #     if item in interface_rule.keys():
            #         if not isinstance(reqdata[item],eval(interface_rule[item]["type"])):
            #             return JsonResponse(resp.error(code="99999", message="{}字段类型不为{}".format(item,interface_rule[item]["type"])))
            return func(request,*args, **kwargs)
        return validate
    return wrapper

