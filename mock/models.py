from django.db import models

# Create your models here.

class Mock_interfaces(models.Model):
    '''
    mock接口模型
    service：服务名
    interface_name：接口名
    interface_path:接口url
    interface_mock_id:当前的mockid(m默认为0，为0则随机mock)
    is_delete:是否删除
    '''
    id=models.AutoField("接口id",primary_key=True)
    service_name=models.CharField("服务名",max_length=50)
    interface_name=models.CharField("接口名",max_length=50)
    interface_url=models.CharField("接口url",max_length=300,unique=True)
    interface_mock_id=models.IntegerField("接口mock数据，为0为随机mock",default=0)
    is_delete=models.SmallIntegerField("是否删除:0-正常；1-删除",default=0)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'mcok_interfaces'


class Mock_lists(models.Model):
    '''
    mock接口模型
    mock_name：mock名
    interface_id：接口id
    mock_data:mock数据
    is_delete:是否删除
    '''
    id=models.AutoField("mockid",primary_key=True)
    mock_name = models.CharField("mock名称", max_length=30)
    mock_data = models.CharField("mock数据", max_length=3000)
    mock_interface_id = models.IntegerField('mock接口id')
    is_delete=models.SmallIntegerField("是否删除:0-正常；1-删除",default=0)
    create_time = models.DateField('创建时间', auto_now_add=True)
    update_time = models.DateField('更新时间', auto_now=True)
    class Meta:
        db_table = 'mcok_lists'