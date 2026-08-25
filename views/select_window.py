import os, json, copy
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QListWidget, QMessageBox,
                               QAbstractItemView, QSpinBox, QDoubleSpinBox, QGroupBox,
                               QGridLayout, QCompleter, QCheckBox, QInputDialog,
                               QLineEdit, QDialog)
from PySide6.QtCore import Qt, QStringListModel, QSortFilterProxyModel
from models.player import Player
from engine.engine import BattleEngine
from views.battle_window import BattleWindow
from views.custom_monster_dialog import CustomMonsterDialog
from models.skill import Skill
from utils.equipment_skills import NEW_EQUIPMENT_SKILLS, get_skills_by_equipment
from skills.catalog import (unlocked_legacy_skills, entry_desc, build_skills,
                            legacy_entry_by_name, skill_id_to_name, skill_name_to_id)
from config import ROOT_DIR


class SelectWindow(QWidget):
    # ============= 淬炼属性 =============
    REFINE_ATTRS = [
        ('无淬炼', None),
        ('攻击', 'attack'),
        ('防御', 'defense'),
        ('生命', 'hp'),
        ('能量', 'energy'),
        ('暴击', 'crit'),
        ('穿透', 'pen'),
        ('敏捷', 'agility'),
    ]
    REFINE_ATTR_NAME = {val: text for text, val in REFINE_ATTRS}
    ATTR_NAMES = ['攻击', '防御', '生命', '能量', '暴击', '穿透', '敏捷']
    STAT_KEYS = ['attack', 'defense', 'hp', 'energy', 'crit', 'pen', 'agility']

    def __init__(self, monsters, equipments, skills_pool):
        super().__init__()
        self.all_monsters = monsters
        self.filtered_monsters = monsters[:]
        self.equipments = equipments
        self.skills_pool = list(skills_pool)
        self.player = Player()
        self.battle_window = None
        self.config_file = os.path.join(ROOT_DIR, "last_config.json")
        self.custom_monsters_file = os.path.join(ROOT_DIR, "custom_monsters.json")
        self.custom_monsters = []
        self.load_custom_monsters()
        self.all_schemes = {}
        self.current_scheme_name = "方案1"

        self.slot_labels = {}
        self.init_ui()
        self.load_all_config()
        self._update_gear_tooltips()

    def init_ui(self):
        self.setWindowTitle("战前准备")
        root_layout = QHBoxLayout(self)

        # ============ 左侧：主配置界面 ============
        left_panel = QWidget()
        main_layout = QVBoxLayout(left_panel)

        # 方案管理
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(QLabel("装备方案："))
        self.scheme_combo = QComboBox()
        self.scheme_combo.setMinimumWidth(120)
        self.scheme_combo.currentIndexChanged.connect(self.on_scheme_changed)
        scheme_layout.addWidget(self.scheme_combo)
        self.btn_new_scheme = QPushButton("新建")
        self.btn_new_scheme.clicked.connect(self.new_scheme)
        scheme_layout.addWidget(self.btn_new_scheme)
        self.btn_delete_scheme = QPushButton("删除")
        self.btn_delete_scheme.clicked.connect(self.delete_scheme)
        scheme_layout.addWidget(self.btn_delete_scheme)
        self.btn_rename_scheme = QPushButton("重命名")
        self.btn_rename_scheme.clicked.connect(self.rename_scheme)
        scheme_layout.addWidget(self.btn_rename_scheme)
        scheme_layout.addStretch()
        main_layout.addLayout(scheme_layout)

        # 玩家等级
        lv_layout = QHBoxLayout()
        lv_layout.addWidget(QLabel("玩家等级："))
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 999)
        self.level_spin.setValue(1)
        self.level_spin.valueChanged.connect(self.on_level_changed)
        lv_layout.addWidget(self.level_spin)
        lv_layout.addStretch()
        main_layout.addLayout(lv_layout)

        # 装备选择
        gear_group = QGroupBox("装备选择（可输入文字搜索）")
        gear_layout = QGridLayout()
        self.slot_widgets = {}
        slots = ['武器', '护甲', '头盔', '鞋子', '饰品']
        for idx, slot in enumerate(slots):
            combo = QComboBox()
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.NoInsert)
            self._setup_completer(combo, slot)
            combo.addItem("无", None)
            for eq in self.equipments:
                if eq.slot == slot:
                    combo.addItem(eq.name, eq)
            combo.currentIndexChanged.connect(self.on_gear_changed)
            label = QLabel(slot)
            self.slot_labels[slot] = label
            gear_layout.addWidget(label, idx, 0)
            gear_layout.addWidget(combo, idx, 1)

            lv_spin = QSpinBox()
            lv_spin.setRange(0, 99)
            lv_spin.setValue(0)
            lv_spin.valueChanged.connect(self.on_gear_changed)
            gear_layout.addWidget(QLabel("等级"), idx, 2)
            gear_layout.addWidget(lv_spin, idx, 3)

            qty_spin = QSpinBox()
            qty_spin.setRange(100, 120)
            qty_spin.setValue(100)
            qty_spin.setSuffix("%")
            qty_spin.valueChanged.connect(self.on_gear_changed)
            gear_layout.addWidget(QLabel("品质"), idx, 4)
            gear_layout.addWidget(qty_spin, idx, 5)

            # 淬炼属性（一件装备只能淬炼一种属性）
            refine_combo = QComboBox()
            for text, val in self.REFINE_ATTRS:
                refine_combo.addItem(text, val)
            refine_combo.setToolTip("选择要淬炼的属性（无淬炼则保持不变）")
            refine_combo.currentIndexChanged.connect(self.on_gear_changed)
            gear_layout.addWidget(QLabel("淬炼"), idx, 6)
            gear_layout.addWidget(refine_combo, idx, 7)

            # 淬炼百分比（100%~120%）
            refine_spin = QSpinBox()
            refine_spin.setRange(100, 120)
            refine_spin.setValue(100)
            refine_spin.setSuffix("%")
            refine_spin.setToolTip("淬炼后该属性 = 强化后属性 × 淬炼百分比，其他属性不变")
            refine_spin.valueChanged.connect(self.on_gear_changed)
            gear_layout.addWidget(refine_spin, idx, 8)
            self.slot_widgets[slot] = (combo, lv_spin, qty_spin, refine_combo, refine_spin)
        gear_group.setLayout(gear_layout)
        main_layout.addWidget(gear_group)

        # 属性预览
        self.stats_preview = QLabel()
        self.stats_preview.setStyleSheet("background: #f0f0f0; padding: 5px;")
        main_layout.addWidget(QLabel("玩家属性预览："))
        main_layout.addWidget(self.stats_preview)

        # 副本选择
        dungeon_layout = QHBoxLayout()
        dungeon_layout.addWidget(QLabel("选择副本："))
        self.dungeon_combo = QComboBox()
        self._populate_dungeon_combo()
        self.dungeon_combo.currentIndexChanged.connect(self.on_dungeon_changed)
        dungeon_layout.addWidget(self.dungeon_combo)
        dungeon_layout.addStretch()
        main_layout.addLayout(dungeon_layout)

        # 怪物选择
        monster_layout = QHBoxLayout()
        monster_layout.addWidget(QLabel("选择怪物："))
        self.monster_combo = QComboBox()
        self._populate_monster_combo()
        monster_layout.addWidget(self.monster_combo)
        main_layout.addLayout(monster_layout)

        # 技能选择
        skill_layout = QHBoxLayout()
        self.skill_label = QLabel("选择技能：")
        skill_layout.addWidget(self.skill_label)
        self.skill_list = QListWidget()
        self.skill_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self._refresh_skill_list()
        skill_layout.addWidget(self.skill_list)
        main_layout.addLayout(skill_layout)

        # 浮动选项
        variance_layout = QHBoxLayout()
        self.variance_check = QCheckBox("攻击力浮动（90%~110%）")
        self.variance_check.setChecked(True)
        variance_layout.addWidget(self.variance_check)
        variance_layout.addStretch()
        variance_layout.addWidget(QLabel("怪物防御概率："))
        self.defend_spin = QDoubleSpinBox()
        self.defend_spin.setRange(0.0, 1.0)
        self.defend_spin.setSingleStep(0.05)
        self.defend_spin.setDecimals(2)
        self.defend_spin.setValue(0.2)
        self.defend_spin.setToolTip("怪物每回合进入防御反击状态的概率（0~1，默认0.2）")
        variance_layout.addWidget(self.defend_spin)
        main_layout.addLayout(variance_layout)

        self.start_btn = QPushButton("开始战斗")
        self.start_btn.clicked.connect(self.start_battle)
        main_layout.addWidget(self.start_btn)

        root_layout.addWidget(left_panel, stretch=3)

        # ============ 右侧：自定义怪物面板 ============
        right_panel = self._build_custom_monster_panel()
        root_layout.addWidget(right_panel, stretch=1)

        self.setLayout(root_layout)

    def _setup_completer(self, combo, slot):
        items = ["无"] + [eq.name for eq in self.equipments if eq.slot == slot]
        model = QStringListModel(items)
        class ContainsFilterProxy(QSortFilterProxyModel):
            def filterAcceptsRow(self, row, parent):
                pattern = self.filterRegularExpression().pattern()
                if not pattern: return True
                index = self.sourceModel().index(row, 0, parent)
                text = self.sourceModel().data(index)
                return pattern.lower() in text.lower()
        proxy = ContainsFilterProxy()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        completer = QCompleter()
        completer.setModel(proxy)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        combo.setCompleter(completer)
        combo.lineEdit().textChanged.connect(lambda text, p=proxy: p.setFilterRegularExpression(text))

    # ================= 技能槽 =================
    def get_max_skills(self):
        return 2 + self.level_spin.value() // 20

    # ================= 装备变化 =================
    def on_gear_changed(self):
        self.refresh_player_from_ui()
        self._refresh_skill_list()

    def _equipped_names(self):
        names = []
        for slot, (combo, *_rest) in self.slot_widgets.items():
            eq = combo.currentData()
            if eq:
                names.append(eq.name)
        return names

    def _new_equipment_skill_defs(self):
        return get_skills_by_equipment(self._equipped_names())

    def _refresh_skill_list(self):
        selected_names = [item.text().split(' [')[0] for item in self.skill_list.selectedItems()]
        self.skill_list.clear()

        # 普通技能
        for s in self.skills_pool:
            self.skill_list.addItem(f"{s.name} [{s.type}] - {s.desc}")

        # 已有装备技能（按装备解锁）
        equipped_names = self._equipped_names()
        for entry in unlocked_legacy_skills(equipped_names, self.player):
            desc = entry_desc(entry, self.player)
            self.skill_list.addItem(f"{entry['name']} [{entry['type']}] - {desc}")

        # 新装备技能（数据驱动）
        for sdef in self._new_equipment_skill_defs():
            self.skill_list.addItem(f"{sdef['name']} [{sdef['type']}] - {sdef['desc']}")

        # 恢复选中
        for i in range(self.skill_list.count()):
            item = self.skill_list.item(i)
            if item.text().split(' [')[0] in selected_names:
                item.setSelected(True)

        self.skill_label.setText(f"选择技能（最多{self.get_max_skills()}个）：")

    def on_level_changed(self, value):
        self.player.set_level(value)
        self.refresh_player_from_ui()
        self._refresh_skill_list()

    def refresh_player_from_ui(self):
        for slot, (combo, lv_spin, qty_spin, refine_combo, refine_spin) in self.slot_widgets.items():
            eq = combo.currentData()
            if eq:
                self.player.equip_item(slot, eq, lv_spin.value(), qty_spin.value(),
                                       refine_combo.currentData(), refine_spin.value())
            else:
                self.player.unequip_item(slot)
        p = self.player
        text = (f"攻击:{round(p.base_attack)}  防御:{round(p.base_defense)}  生命:{round(p.base_hp)}  能量:{round(p.base_energy)}\n"
                f"暴击:{round(p.base_crit)}%  穿透:{round(p.base_pen)}  敏捷:{round(p.base_agility)}")
        self.stats_preview.setText(text)
        self._update_gear_tooltips()

    def _update_gear_tooltips(self):
        for slot, (combo, lv_spin, qty_spin, refine_combo, refine_spin) in self.slot_widgets.items():
            eq = combo.currentData()
            label = self.slot_labels.get(slot)
            if not label: continue
            if eq is None:
                label.setToolTip("无装备")
                continue
            level = lv_spin.value()
            quality = qty_spin.value()
            refine_stat = refine_combo.currentData()
            refine_percent = refine_spin.value()
            # 三列：基础属性 / 强化×品质 / 淬炼后
            base_vals = [getattr(eq, f'base_{k}') for k in self.STAT_KEYS]
            enh_vals = [eq.get_stats(level=level, quality=quality)[k] for k in self.STAT_KEYS]
            refine_vals = [eq.get_stats(level=level, quality=quality,
                                        refine_stat=refine_stat, refine_percent=refine_percent)[k]
                           for k in self.STAT_KEYS]
            tooltip = f"<b>装备：{eq.name}</b><br>"
            if refine_stat:
                rname = self.REFINE_ATTR_NAME.get(refine_stat, refine_stat)
                tooltip += f"<b>淬炼：{rname} ×{refine_percent}%</b><br>"
            tooltip += "<table border='1' cellpadding='3' cellspacing='0' style='border-collapse:collapse;'>"
            tooltip += (f"<tr><th>属性</th><th>基础属性</th>"
                        f"<th>强化×品质<br>(Lv.{level}+品质{quality}%)</th><th>淬炼后</th></tr>")
            for attr, b_val, e_val, r_val in zip(self.ATTR_NAMES, base_vals, enh_vals, refine_vals):
                tooltip += (f"<tr><td>{attr}</td><td align='center'>{round(b_val)}</td>"
                            f"<td align='center'>{round(e_val)}</td><td align='center'>{round(r_val)}</td></tr>")
            tooltip += "</table>"
            label.setToolTip(tooltip)

    def _populate_dungeon_combo(self):
        dungeon_map = {}
        for m in self.all_monsters:
            if m.world_boss: continue
            if m.dungeon_id not in dungeon_map:
                dungeon_map[m.dungeon_id] = m.dungeon_name if m.dungeon_name else f"副本{m.dungeon_id}"
        self.dungeon_combo.blockSignals(True)
        self.dungeon_combo.clear()
        self.dungeon_combo.addItem("全部", None)
        for did in sorted(dungeon_map.keys()):
            display_text = f"副本{did:2d} {dungeon_map[did]}"
            self.dungeon_combo.addItem(display_text, did)
        if any(m.world_boss for m in self.all_monsters):
            self.dungeon_combo.addItem("世界BOSS", -1)
        self.dungeon_combo.blockSignals(False)

    def on_dungeon_changed(self, idx):
        dungeon_id = self.dungeon_combo.currentData()
        if dungeon_id is None:
            self.filtered_monsters = self.all_monsters
        elif dungeon_id == -1:
            self.filtered_monsters = [m for m in self.all_monsters if m.world_boss]
        else:
            self.filtered_monsters = [m for m in self.all_monsters if m.dungeon_id == dungeon_id]
        self._populate_monster_combo()

    def _populate_monster_combo(self):
        self.monster_combo.blockSignals(True)
        self.monster_combo.clear()
        for m in self.filtered_monsters:
            self.monster_combo.addItem(
                f"{m.name} [{m.type}] 攻:{m.attack} 防:{m.defense} HP:{m.hp}", m)
        self.monster_combo.blockSignals(False)

    # ================= 自定义怪物 =================
    def _build_custom_monster_panel(self):
        panel = QGroupBox("自定义怪物")
        layout = QVBoxLayout(panel)

        self.custom_check = QCheckBox("使用自定义怪物战斗")
        self.custom_check.setToolTip("勾选后，将使用右侧选中的自定义怪物进行战斗，而非副本怪物")
        self.custom_check.toggled.connect(self.on_custom_toggle)
        layout.addWidget(self.custom_check)

        layout.addWidget(QLabel("选择自定义怪物："))
        self.custom_monster_combo = QComboBox()
        self.custom_monster_combo.currentIndexChanged.connect(self._refresh_custom_preview)
        layout.addWidget(self.custom_monster_combo)

        self.custom_monster_preview = QLabel()
        self.custom_monster_preview.setWordWrap(True)
        self.custom_monster_preview.setStyleSheet("background: #f0f0f0; padding: 5px;")
        layout.addWidget(self.custom_monster_preview)

        btn_layout = QHBoxLayout()
        self.btn_custom_add = QPushButton("新建")
        self.btn_custom_add.clicked.connect(self.add_custom_monster)
        self.btn_custom_edit = QPushButton("修改")
        self.btn_custom_edit.clicked.connect(self.edit_custom_monster)
        self.btn_custom_del = QPushButton("删除")
        self.btn_custom_del.clicked.connect(self.delete_custom_monster)
        btn_layout.addWidget(self.btn_custom_add)
        btn_layout.addWidget(self.btn_custom_edit)
        btn_layout.addWidget(self.btn_custom_del)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("自定义怪物单独保存于 custom_monsters.json，\n不属于任何副本。"))
        layout.addStretch()

        self._populate_custom_monster_combo()
        return panel

    def load_custom_monsters(self):
        self.custom_monsters = []
        if os.path.exists(self.custom_monsters_file):
            try:
                with open(self.custom_monsters_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.custom_monsters = data
            except Exception as e:
                print(f"加载自定义怪物失败: {e}")
                self.custom_monsters = []

    def save_custom_monsters(self):
        try:
            with open(self.custom_monsters_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_monsters, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存自定义怪物失败: {e}")

    def _populate_custom_monster_combo(self):
        self.custom_monster_combo.blockSignals(True)
        self.custom_monster_combo.clear()
        for m in self.custom_monsters:
            self.custom_monster_combo.addItem(m.get('name', '未命名'), m)
        self.custom_monster_combo.blockSignals(False)
        self._refresh_custom_preview()

    def _refresh_custom_preview(self):
        m = self.custom_monster_combo.currentData()
        if m is None:
            self.custom_monster_preview.setText("未选择自定义怪物\n（可点击下方“新建”创建）")
            return
        text = (f"名字：{m.get('name', '')}   类型：{m.get('type', '自定义')}\n"
                f"攻击：{m.get('attack', 0)}   防御：{m.get('defense', 0)}\n"
                f"生命：{m.get('hp', 0)}   敏捷：{m.get('agility', 0)}\n"
                f"防御概率：{m.get('defend_chance', 0.4)}")
        self.custom_monster_preview.setText(text)

    def on_custom_toggle(self, checked):
        # 勾选后使用自定义怪物战斗，禁用普通副本/怪物选择
        self.dungeon_combo.setEnabled(not checked)
        self.monster_combo.setEnabled(not checked)

    def add_custom_monster(self):
        dialog = CustomMonsterDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.get_data()
        name = data['name']
        base = name
        i = 2
        while any(m.get('name') == name for m in self.custom_monsters):
            name = f"{base}{i}"
            i += 1
        data['name'] = name
        self.custom_monsters.append(data)
        self.save_custom_monsters()
        self._populate_custom_monster_combo()
        idx = self.custom_monster_combo.findText(name)
        if idx >= 0:
            self.custom_monster_combo.setCurrentIndex(idx)
        self.custom_check.setChecked(True)

    def edit_custom_monster(self):
        m = self.custom_monster_combo.currentData()
        if m is None:
            QMessageBox.information(self, "提示", "请先选择一个自定义怪物")
            return
        dialog = CustomMonsterDialog(self, m)
        if dialog.exec() != QDialog.Accepted:
            return
        new_data = dialog.get_data()
        idx = self.custom_monster_combo.currentIndex()
        self.custom_monsters[idx] = new_data
        self.save_custom_monsters()
        self._populate_custom_monster_combo()
        if 0 <= idx < self.custom_monster_combo.count():
            self.custom_monster_combo.setCurrentIndex(idx)

    def delete_custom_monster(self):
        m = self.custom_monster_combo.currentData()
        if m is None:
            QMessageBox.information(self, "提示", "请先选择一个自定义怪物")
            return
        reply = QMessageBox.question(
            self, "删除自定义怪物",
            f"确定删除自定义怪物“{m.get('name')}”吗？",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        idx = self.custom_monster_combo.currentIndex()
        del self.custom_monsters[idx]
        self.save_custom_monsters()
        self._populate_custom_monster_combo()

    def _build_custom_monster(self, data):
        if not data:
            return None
        from models.monster import Monster
        idx = self.custom_monster_combo.currentIndex()
        return Monster(
            id=-(200000 + idx),
            name=data.get('name', '自定义怪物'),
            type=data.get('type', '自定义'),
            attack=data.get('attack', 100),
            defense=data.get('defense', 50),
            hp=data.get('hp', 500),
            agility=data.get('agility', 10),
            skill_pool=[],
            gold=0,
            exp=0,
            defend_chance=data.get('defend_chance', 0.4),
            dungeon_id=0,
            dungeon_name='自定义',
            world_boss=False
        )

    # ================= 开始战斗 =================
    def start_battle(self):
        selected = [item for item in self.skill_list.selectedItems()]
        max_skills = self.get_max_skills()
        if len(selected) > max_skills:
            QMessageBox.warning(self, "错误", f"最多选择{max_skills}个技能！")
            return
        self.refresh_player_from_ui()
        chosen_skills = []
        for item in selected:
            skill_name = item.text().split(' [')[0]
            # 已有装备技能
            entry = legacy_entry_by_name(skill_name)
            if entry:
                chosen_skills.extend(build_skills(entry, self.player))
                continue
            # 新装备技能（数据驱动）
            sdef = NEW_EQUIPMENT_SKILLS.get(skill_name)
            if sdef:
                chosen_skills.append(Skill(
                    id=sdef['id'], name=skill_name, type=sdef['type'],
                    power=0, energy_cost=sdef['energy_cost'],
                    buff_effect=None, duration=sdef['duration'],
                    target=sdef['target'], desc=sdef['desc'],
                    cooldown=sdef['cooldown']))
                continue
            # 普通技能
            for s in self.skills_pool:
                if s.name == skill_name:
                    chosen_skills.append(s)
                    break

        self.player.passive_skills = [s for s in chosen_skills if s.type == 'passive']
        self.player.equipped_skills = [s for s in chosen_skills if s.type != 'passive']
        self.player.apply_passive_skills()

        if self.custom_check.isChecked():
            monster = self._build_custom_monster(self.custom_monster_combo.currentData())
            if monster is None:
                QMessageBox.warning(self, "错误", "请选择自定义怪物！")
                return
        else:
            monster = self.monster_combo.currentData()
            if not monster:
                QMessageBox.warning(self, "错误", "请选择怪物！")
                return

        self.save_current_scheme()
        battle_monster = copy.deepcopy(monster)
        battle_monster.defend_chance = self.defend_spin.value()
        variance = self.variance_check.isChecked()
        self.controller = BattleEngine(self.player, battle_monster, attack_variance=variance)
        self.battle_window = BattleWindow(self.controller)
        self.battle_window.battle_finished.connect(self._on_battle_finished)
        self.hide()
        self.battle_window.show()

    def _on_battle_finished(self):
        if self.battle_window:
            try:
                self.battle_window.battle_finished.disconnect(self._on_battle_finished)
            except: pass
            self.battle_window.close()
            self.battle_window = None
        self.player = Player()
        self._restore_current_scheme()
        self.refresh_player_from_ui()
        self.show()

    # ================= 方案管理 =================
    def _collect_current_data(self):
        data = {
            "level": self.level_spin.value(),
            "gear": {},
            "monster_id": None,
            "dungeon_id": self.dungeon_combo.currentData(),
            "skill_ids": [],
            "attack_variance": self.variance_check.isChecked(),
            "monster_defend_chance": self.defend_spin.value(),
            "use_custom_monster": self.custom_check.isChecked(),
            "custom_monster_name": self.custom_monster_combo.currentText()
        }
        for slot, (combo, lv_spin, qty_spin, refine_combo, refine_spin) in self.slot_widgets.items():
            eq = combo.currentData()
            if eq:
                data["gear"][slot] = {
                    "equipment_id": eq.id,
                    "level": lv_spin.value(),
                    "quality": qty_spin.value(),
                    "refine_stat": refine_combo.currentData(),
                    "refine_percent": refine_spin.value()
                }
            else:
                data["gear"][slot] = None
        monster = self.monster_combo.currentData()
        if monster: data["monster_id"] = monster.id
        for item in self.skill_list.selectedItems():
            skill_name = item.text().split(' [')[0]
            skill_id = skill_name_to_id(skill_name)
            if skill_id is not None:
                data["skill_ids"].append(skill_id)
            else:
                for s in self.skills_pool:
                    if s.name == skill_name:
                        data["skill_ids"].append(s.id)
                        break
        return data

    def _apply_data_to_ui(self, data):
        controls = [self.level_spin, self.monster_combo, self.dungeon_combo,
                    self.custom_check, self.custom_monster_combo, self.defend_spin]
        for combo, lv_spin, qty_spin, refine_combo, refine_spin in self.slot_widgets.values():
            controls.extend([combo, lv_spin, qty_spin, refine_combo, refine_spin])
        for ctrl in controls: ctrl.blockSignals(True)

        self.level_spin.setValue(data.get("level", 1))
        self.player.set_level(data.get("level", 1))

        dungeon_id = data.get("dungeon_id")
        if dungeon_id is not None:
            idx = self.dungeon_combo.findData(dungeon_id)
            if idx >= 0: self.dungeon_combo.setCurrentIndex(idx)
            else: self.dungeon_combo.setCurrentIndex(0)
        else: self.dungeon_combo.setCurrentIndex(0)
        self.on_dungeon_changed(self.dungeon_combo.currentIndex())

        for slot, gear_info in data.get("gear", {}).items():
            if slot not in self.slot_widgets: continue
            combo, lv_spin, qty_spin, refine_combo, refine_spin = self.slot_widgets[slot]
            refine_stat = gear_info.get("refine_stat") if gear_info else None
            refine_percent = gear_info.get("refine_percent", 100) if gear_info else 100
            r_idx = refine_combo.findData(refine_stat)
            refine_combo.setCurrentIndex(r_idx if r_idx >= 0 else 0)
            refine_spin.setValue(refine_percent)
            if gear_info and "equipment_id" in gear_info:
                eq = next((e for e in self.equipments if e.id == gear_info["equipment_id"] and e.slot == slot), None)
                if eq:
                    combo.setCurrentIndex(combo.findData(eq))
                    lv_spin.setValue(gear_info.get("level", 0))
                    qty_spin.setValue(gear_info.get("quality", 100))
                    self.player.equip_item(slot, eq, gear_info.get("level", 0),
                                           gear_info.get("quality", 100),
                                           refine_stat, refine_percent)
                else:
                    combo.setCurrentIndex(0); lv_spin.setValue(0); qty_spin.setValue(100)
                    self.player.unequip_item(slot)
            else:
                combo.setCurrentIndex(0); lv_spin.setValue(0); qty_spin.setValue(100)
                self.player.unequip_item(slot)

        self._refresh_skill_list()
        self.skill_list.clearSelection()
        for skill_id in data.get("skill_ids", []):
            target_name = skill_id_to_name(skill_id)
            if target_name:
                for i in range(self.skill_list.count()):
                    item = self.skill_list.item(i)
                    if item.text().split(' [')[0] == target_name:
                        item.setSelected(True)
                        break
            else:
                for i, s in enumerate(self.skills_pool):
                    if s.id == skill_id and i < self.skill_list.count():
                        item = self.skill_list.item(i)
                        if item: item.setSelected(True)
                        break

        monster_id = data.get("monster_id")
        if monster_id:
            for i in range(self.monster_combo.count()):
                if self.monster_combo.itemData(i) and self.monster_combo.itemData(i).id == monster_id:
                    self.monster_combo.setCurrentIndex(i); break
        else:
            self.monster_combo.setCurrentIndex(0)

        use_custom = data.get("use_custom_monster", False)
        self.custom_check.setChecked(use_custom)
        custom_name = data.get("custom_monster_name")
        if custom_name:
            idx = self.custom_monster_combo.findText(custom_name)
            if idx >= 0:
                self.custom_monster_combo.setCurrentIndex(idx)

        self.variance_check.setChecked(data.get("attack_variance", True))
        self.defend_spin.setValue(data.get("monster_defend_chance", 0.2))
        for ctrl in controls: ctrl.blockSignals(False)
        self.on_custom_toggle(self.custom_check.isChecked())
        self.refresh_player_from_ui()

    def save_current_scheme(self):
        if not self.current_scheme_name: return
        self.all_schemes[self.current_scheme_name] = self._collect_current_data()
        self._save_all_schemes_to_disk()

    def _save_all_schemes_to_disk(self):
        config = {"current_scheme": self.current_scheme_name, "schemes": self.all_schemes}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e: print(f"保存方案失败: {e}")

    def load_all_config(self):
        if not os.path.exists(self.config_file):
            self._init_default_scheme()
            return
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except: self._init_default_scheme(); return
        if "schemes" not in config:
            self.all_schemes = {"方案1": config}; self.current_scheme_name = "方案1"
            self._save_all_schemes_to_disk()
        else:
            self.all_schemes = config.get("schemes", {})
            self.current_scheme_name = config.get("current_scheme", "方案1")
            if not self.all_schemes: self._init_default_scheme(); return
        if self.current_scheme_name not in self.all_schemes:
            self.current_scheme_name = next(iter(self.all_schemes))
        self._populate_scheme_combo()
        self._restore_current_scheme()

    def _init_default_scheme(self):
        self.all_schemes = {"方案1": self._collect_current_data()}
        self.current_scheme_name = "方案1"
        self._save_all_schemes_to_disk()
        self._populate_scheme_combo()

    def _populate_scheme_combo(self):
        self.scheme_combo.blockSignals(True)
        self.scheme_combo.clear()
        for name in self.all_schemes: self.scheme_combo.addItem(name)
        idx = self.scheme_combo.findText(self.current_scheme_name)
        if idx >= 0: self.scheme_combo.setCurrentIndex(idx)
        self.scheme_combo.blockSignals(False)

    def _restore_current_scheme(self):
        data = self.all_schemes.get(self.current_scheme_name, {})
        if not data:
            data = self._collect_current_data()
            self.all_schemes[self.current_scheme_name] = data
        self._apply_data_to_ui(data)

    def on_scheme_changed(self, idx):
        if idx < 0: return
        new_name = self.scheme_combo.itemText(idx)
        if new_name == self.current_scheme_name: return
        self.save_current_scheme()
        self.current_scheme_name = new_name
        self.player = Player()
        self._restore_current_scheme()

    def new_scheme(self):
        base = "方案"; i = 1
        while f"{base}{i}" in self.all_schemes: i += 1
        name = f"{base}{i}"
        self.save_current_scheme()
        self.all_schemes[name] = self._collect_current_data()
        self.current_scheme_name = name
        self._save_all_schemes_to_disk()
        self._populate_scheme_combo()

    def delete_scheme(self):
        if len(self.all_schemes) <= 1:
            QMessageBox.warning(self, "错误", "至少保留一个方案！"); return
        reply = QMessageBox.question(self, "删除方案", f"确定删除方案“{self.current_scheme_name}”吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        del self.all_schemes[self.current_scheme_name]
        self.current_scheme_name = next(iter(self.all_schemes))
        self._save_all_schemes_to_disk()
        self._populate_scheme_combo()
        self.player = Player()
        self._restore_current_scheme()

    def rename_scheme(self):
        new_name, ok = QInputDialog.getText(self, "重命名方案", "输入新名称：",
                                            QLineEdit.Normal, self.current_scheme_name)
        if not ok or not new_name.strip(): return
        new_name = new_name.strip()
        if new_name == self.current_scheme_name: return
        if new_name in self.all_schemes:
            QMessageBox.warning(self, "错误", "方案名已存在！"); return
        data = self.all_schemes.pop(self.current_scheme_name)
        self.all_schemes[new_name] = data
        self.current_scheme_name = new_name
        self._save_all_schemes_to_disk()
        self._populate_scheme_combo()

    def closeEvent(self, event):
        self.save_current_scheme()
        event.accept()