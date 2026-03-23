import sys
import os

# 项目路径
project_home = '/home/JialinGuo/voyago'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 导入 Flask 应用
from app import app as application

# 配置日志
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
