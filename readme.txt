//统一安装插件
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
//初始化orm模型命令：
python3 manage.py makemigrations
python3 manage.py migrate

###创建模块
python3 manage.py startapp 模块名

###生成requirements
python3 -m pip freeze > requirements.txt
python3 -m pip install -r requirements.txt