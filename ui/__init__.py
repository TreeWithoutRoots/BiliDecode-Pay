import sys
import os

# 将项目根目录加入 sys.path，确保子模块能 import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
