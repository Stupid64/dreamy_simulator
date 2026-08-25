from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout,
                               QLineEdit, QSpinBox, QDoubleSpinBox, QVBoxLayout,
                               QLabel)


class CustomMonsterDialog(QDialog):
    """自定义怪物 新建/修改 对话框"""

    def __init__(self, parent=None, monster_data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑自定义怪物" if monster_data else "新建自定义怪物")
        self.resize(340, 280)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入怪物名字")
        form.addRow("名字：", self.name_edit)

        self.type_edit = QLineEdit()
        self.type_edit.setText("自定义")
        form.addRow("类型：", self.type_edit)

        self.attack_spin = QSpinBox()
        self.attack_spin.setRange(0, 99999999)
        form.addRow("攻击：", self.attack_spin)

        self.defense_spin = QSpinBox()
        self.defense_spin.setRange(0, 99999999)
        form.addRow("防御：", self.defense_spin)

        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 999999999)
        form.addRow("生命（血量）：", self.hp_spin)

        self.agility_spin = QSpinBox()
        self.agility_spin.setRange(0, 99999999)
        form.addRow("敏捷：", self.agility_spin)

        self.defend_chance_spin = QDoubleSpinBox()
        self.defend_chance_spin.setRange(0.0, 1.0)
        self.defend_chance_spin.setSingleStep(0.05)
        self.defend_chance_spin.setValue(0.4)
        form.addRow("防御概率：", self.defend_chance_spin)

        layout.addLayout(form)

        tip = QLabel("提示：自定义怪物不属于任何副本，仅在勾选“使用自定义怪物战斗”时生效。")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: gray;")
        layout.addWidget(tip)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("保存")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if monster_data:
            self._load_from_data(monster_data)

    def _load_from_data(self, data):
        self.name_edit.setText(str(data.get('name', '')))
        self.type_edit.setText(str(data.get('type', '自定义')))
        self.attack_spin.setValue(int(data.get('attack', 0)))
        self.defense_spin.setValue(int(data.get('defense', 0)))
        self.hp_spin.setValue(int(data.get('hp', 100)))
        self.agility_spin.setValue(int(data.get('agility', 0)))
        self.defend_chance_spin.setValue(float(data.get('defend_chance', 0.4)))

    def get_data(self):
        return {
            'name': self.name_edit.text().strip() or '自定义怪物',
            'type': self.type_edit.text().strip() or '自定义',
            'attack': self.attack_spin.value(),
            'defense': self.defense_spin.value(),
            'hp': self.hp_spin.value(),
            'agility': self.agility_spin.value(),
            'defend_chance': self.defend_chance_spin.value(),
        }
