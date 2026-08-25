import os
import sys

# 获取程序真实的运行目录（EXE 所在文件夹或脚本所在文件夹）
if getattr(sys, 'frozen', False):
    # 打包后的 EXE 环境
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    # 普通 Python 脚本环境
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, "data")
IMAGE_DIR = os.path.join(ROOT_DIR, "images")  # 预留

EXCEL_FILE = os.path.join(DATA_DIR, "game_data.xlsx")