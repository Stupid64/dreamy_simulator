import sys
import os

missing = []
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing.append("PySide6 或 PyQt5")
try:
    import pandas
except ImportError:
    missing.append("pandas")
try:
    import openpyxl
except ImportError:
    missing.append("openpyxl")

if missing:
    print("缺少以下依赖，请安装：")
    for m in missing:
        print(f"  pip install {m.split()[0]}")
    sys.exit(1)

from utils.data_loader import load_monsters, load_equipments, load_skills
from views.select_window import SelectWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        monsters = load_monsters()
        equipments = load_equipments()
        skills = load_skills()
    except Exception as e:
        print(f"数据加载失败: {e}")
        sys.exit(1)

    select = SelectWindow(monsters, equipments, skills)
    select.show()
    sys.exit(app.exec())