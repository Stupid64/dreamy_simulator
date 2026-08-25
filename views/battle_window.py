from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class BattleWindow(QWidget):
    battle_finished = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.log_signal = self.on_log_update
        self.setWindowTitle("战斗")
        self.init_ui()
        self.controller.start()
        self.refresh()

    def init_ui(self):
        main_layout = QVBoxLayout()

        panels = QHBoxLayout()
        self.player_frame = self.create_player_panel()
        self.monster_frame = self.create_monster_panel()
        panels.addWidget(self.player_frame)
        panels.addWidget(self.monster_frame)

        self.log_label = QLabel()
        self.log_label.setWordWrap(True)
        self.log_label.setTextFormat(Qt.RichText)
        self.log_label.setStyleSheet("background: #f0f0f0; padding: 5px;")
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.log_label)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumHeight(150)
        self.scroll.verticalScrollBar().rangeChanged.connect(
            lambda min_val, max_val: self.scroll.verticalScrollBar().setValue(max_val))

        self.skill_layout = QHBoxLayout()
        self.skill_buttons = []

        self.exit_btn = QPushButton("逃跑")
        self.exit_btn.clicked.connect(self.on_exit_click)

        main_layout.addLayout(panels)
        main_layout.addWidget(QLabel("战斗报告："))
        main_layout.addWidget(self.scroll)
        main_layout.addWidget(QLabel("技能："))
        main_layout.addLayout(self.skill_layout)
        main_layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)
        self.setLayout(main_layout)
        self.resize(600, 400)
        self.update_skill_buttons()

    def create_player_panel(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()
        self.player_name = QLabel("玩家")
        self.player_hp = QLabel()
        self.player_energy = QLabel()
        self.player_atk = QLabel()
        self.player_stats = QLabel()
        self.player_buffs = QLabel()
        self.player_buffs.setWordWrap(True)
        layout.addWidget(self.player_name)
        layout.addWidget(self.player_hp)
        layout.addWidget(self.player_energy)
        layout.addWidget(self.player_atk)
        layout.addWidget(self.player_stats)
        layout.addWidget(self.player_buffs)
        frame.setLayout(layout)
        return frame

    def create_monster_panel(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()
        self.monster_name = QLabel()
        self.monster_hp = QLabel()
        self.monster_atk = QLabel()
        self.monster_stats = QLabel()
        self.monster_buffs = QLabel()          # 显示怪物所有状态
        self.monster_buffs.setWordWrap(True)
        layout.addWidget(self.monster_name)
        layout.addWidget(self.monster_hp)
        layout.addWidget(self.monster_atk)
        layout.addWidget(self.monster_stats)
        layout.addWidget(self.monster_buffs)   # 新增
        frame.setLayout(layout)
        return frame

    def update_skill_buttons(self):
        for btn in self.skill_buttons:
            self.skill_layout.removeWidget(btn)
            btn.deleteLater()
        self.skill_buttons.clear()
        for skill in self.controller.get_active_skills():
            btn = QPushButton(skill.name)
            btn.clicked.connect(lambda *args, s=skill: self.on_skill_click(s))
            self.skill_layout.addWidget(btn)
            self.skill_buttons.append(btn)

    def refresh(self):
        p = self.controller.player
        m = self.controller.monster
        self.player_name.setText(f"== {p.name} ==")
        self.player_hp.setText(f"血量：{round(p.hp)}/{round(p.max_hp)}")
        self.player_energy.setText(f"能量：{round(p.energy)}/{round(p.max_energy)}")
        self.player_atk.setText(f"攻击力：{round(p.attack)}")
        self.player_stats.setText(f"防御：{round(p.defense)} 敏捷：{round(p.agility)} 暴击：{round(p.crit)} 穿透：{round(p.pen)}")

        # 玩家buff
        buff_text = "Buff: "
        if p.buffs:
            buff_info = []
            for b in p.buffs:
                if b.remaining > 0:
                    buff_info.append(f"{b.name}({b.remaining}回合)")
                elif b.remaining == -1:
                    buff_info.append(f"{b.name}(永久)")
                else:
                    buff_info.append(f"{b.name}(即将结束)")
            buff_text += ", ".join(buff_info)
        else:
            buff_text += "无"
        self.player_buffs.setText(buff_text)

        self.monster_name.setText(f"== {m.name} ==")
        self.monster_hp.setText(f"血量：{round(m.hp)}/{round(m.max_hp)}")
        self.monster_atk.setText(f"攻击力：{round(m.attack)}")
        self.monster_stats.setText(f"防御：{round(m.defense)} 敏捷：{round(m.agility)}")

        # 怪物所有状态（正面▲，负面▼）
        all_buffs_text = "状态: "
        if m.buffs:
            info = []
            for b in m.buffs:
                prefix = "▲" if not b.is_debuff else "▼"
                if b.remaining > 0:
                    info.append(f"{prefix}{b.name}({b.remaining}回合)")
                elif b.remaining == -1:
                    info.append(f"{prefix}{b.name}(永久)")
                else:
                    info.append(f"{prefix}{b.name}(即将结束)")
            all_buffs_text += ", ".join(info)
        else:
            all_buffs_text += "无"
        self.monster_buffs.setText(all_buffs_text)

        # 技能按钮更新
        for btn, skill in zip(self.skill_buttons, self.controller.get_active_skills()):
            if skill.name == '治疗':
                energy_cost = round(5 + p.max_energy * 0.07)
            elif skill.name == '怒击':
                energy_cost = round(5 + p.max_energy * 0.07)
            else:
                energy_cost = skill.energy_cost

            cd = self.controller.skill_cooldowns.get(skill.name, 0)
            if skill.name in ('攻击', '防御反击'):
                btn.setText(f"{skill.name} (CD:{cd})" if cd > 0 else skill.name)
            else:
                btn.setText(f"{skill.name} ({energy_cost}) (CD:{cd})" if cd > 0 else f"{skill.name} ({energy_cost})")

            tip = f"{skill.desc}\n能量消耗：{energy_cost}"
            if cd > 0:
                tip += f"\n冷却中，剩余 {cd} 回合"
            btn.setToolTip(tip)
            btn.setEnabled(cd == 0 and energy_cost <= p.energy and self.controller.state == 'ongoing')

        if self.controller.state != 'ongoing':
            for btn in self.skill_buttons:
                btn.setEnabled(False)
            self.exit_btn.setText("完成")
        else:
            self.exit_btn.setText("逃跑")

    def on_skill_click(self, skill):
        self.controller.player_action(skill)
        self.refresh()

    def on_exit_click(self):
        if self.controller.state == 'ongoing':
            self.controller.escape()
        self.battle_finished.emit()
        self.close()

    def on_log_update(self, controller):
        html_lines = []
        for line in controller.log:
            if '暴击！' in line:
                line = f"<span style='color:red;'>{line}</span>"
            if line.startswith('--- 第') and '回合 ---' in line:
                line = f"<b>{line}</b>"
            html_lines.append(line)
        self.log_label.setText('<br>'.join(html_lines))
        self.refresh()