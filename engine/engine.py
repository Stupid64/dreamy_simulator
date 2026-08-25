# -*- coding: utf-8 -*-
"""战斗引擎：回合制战斗的核心状态机与事件派发。

职责：
- 回合循环（start / _next_turn / _end_of_turn）
- 事件派发（battle_start / turn_start / turn_end / damage_dealt / heal / buff_applied / buff_removed / battle_end）
- 先后手、冷却、能量、防御反击、世界Boss 机制
- 伤害与 buff 的便捷入口

技能效果全部通过 ``skills.registry`` 注册的执行器 / 事件监听器实现，
引擎不包含任何具体技能分支。
"""
import random

from models.enums import DamageKind
from models.skill import Skill
from engine.events import (BattleStart, BattleEnd, TurnStart, TurnEnd,
                           DamageEvent, HealEvent, BuffAppliedEvent,
                           BuffRemovedEvent, EventBus)
from engine.damage import DamageCalculator
from engine.buffs import BuffManager
from skills.registry import (get_active_handler, get_passive_listeners,
                             FIRST_STRIKE_SKILLS)


class BattleEngine:
    # 基础技能
    ATTACK_SKILL = Skill(
        id=0, name='攻击', type='active', power=1.0, energy_cost=0,
        buff_effect=None, duration=0, target='enemy',
        desc='普通攻击，造成100%基础伤害', cooldown=0)
    DEFEND_SKILL = Skill(
        id=0, name='防御反击', type='buff', power=0, energy_cost=0,
        buff_effect=None, duration=1, target='self',
        desc='进入防御反击状态，本回合受到攻击时减伤50%并反击', cooldown=0)

    def __init__(self, player, monster, attack_variance=True, seed=None):
        self.player = player
        self.monster = monster
        self.attack_variance = attack_variance
        self.rng = random.Random(seed)

        self.log = []
        self.state = 'ongoing'
        self.turn = 'player'
        self.log_signal = None          # 由界面注入的回调，用于刷新显示

        self.turn_count = 0
        self.defend_counter = False
        self.skill_cooldowns = {}
        self._cd_grace = set()
        self.sunset_triggered = False
        self.world_boss_initial_hp = 0
        self.player_damage_dealt_this_turn = 0.0
        self.monster_is_first = False

        # 特殊被动状态
        self.fu_tian_active = False
        self.zhen_ming_done = False
        self.yin_mi_regen_amount = 0.0
        self.ji_yu_passive = False

        self.bus = EventBus()
        self.damage = DamageCalculator(self)
        self.buffs = BuffManager(self)

    # ================= buff 便捷方法 =================
    def buff_total(self, character, stat) -> float:
        return self.buffs.total(character, stat)

    def has_buff(self, character, stat) -> bool:
        return self.buffs.has(character, stat)

    def has_buff_named(self, character, name) -> bool:
        return self.buffs.has_named(character, name)

    def apply_buff_effect(self, target, effect, duration, is_debuff=False,
                          start_next_turn=False):
        buff = self.buffs.apply(target, effect, duration, is_debuff, start_next_turn)
        if buff is not None:
            self.bus.emit(BuffAppliedEvent(target=target, buff=buff))
        return buff

    def remove_buff_effect(self, target, buff) -> None:
        self.buffs.remove(target, buff)
        self.bus.emit(BuffRemovedEvent(target=target, buff=buff))

    def process_buffs(self, character) -> None:
        expired = self.buffs.tick(character, self.turn_count)
        for buff in expired:
            self.remove_buff_effect(character, buff)
            self.log.append(f"{character.name} 的 [{buff.name}] 效果消失")

    def eternal_reduction(self) -> float:
        for buff in self.player.buffs:
            if buff.name == '永恒减伤':
                return buff.amount
        return 0

    # ================= 伤害便捷方法 =================
    def has_sunset_buff(self) -> bool:
        return self.has_buff_named(self.player, '黄昏增伤')

    def apply_sunset(self, damage: float) -> float:
        return round(damage * 1.1, 2) if self.has_sunset_buff() else damage

    def _monster_eff_def(self) -> float:
        return max(0, self.monster.defense - self.player.pen)

    def hit_monster_normal(self, base: float) -> float:
        dmg = round(base / (1.0 + 0.01 * self._monster_eff_def()), 2)
        self.monster.hp = round(self.monster.hp - dmg, 2)
        self.player_damage_dealt_this_turn += dmg
        return dmg

    def hit_monster_true(self, dmg: float) -> float:
        self.monster.hp = round(self.monster.hp - dmg, 2)
        self.player_damage_dealt_this_turn += dmg
        return dmg

    def heal_player(self, amount: float, label: str) -> float:
        heal_reduce = self.buff_total(self.player, 'heal_reduce')
        if heal_reduce:
            amount = round(amount * (1 - heal_reduce / 100.0), 2)
            self.log.append(f"治疗降低 {heal_reduce:.2f}%")
        if self.monster.world_boss:
            amount = round(amount * 0.7, 2)
            self.log.append("世界Boss压制，治疗量降低30%")
        self.player.hp = min(self.player.max_hp, round(self.player.hp + amount, 2))
        self.log.append(f"{label}：恢复 {round(amount)} 点生命")
        self.bus.emit(HealEvent(target=self.player, amount=amount, label=label))
        return amount

    def get_attack(self, attacker) -> float:
        return self.damage.get_attack(attacker)

    def _has_storm_buff(self) -> bool:
        return self.has_buff_named(self.player, '风暴降临')

    def _storm_extra_damage(self) -> float:
        return round(0.07 * self.player.agility + self.player.get_weapon_level(), 2)

    def dodge_chance(self, attacker, defender) -> float:
        x = defender.agility
        y = attacker.agility
        if x > 8.4:
            ratio = y / (x - 8.4)
            p = 0.05 + 0.45 / (1.0 + 2.94 * ratio * ratio)
        else:
            p = 0.05
        return max(0.05, min(0.5, p))

    def perform_attack(self, attacker, defender, skill=None,
                       power_multiplier=None) -> bool:
        if power_multiplier is not None:
            skill_power = power_multiplier
        else:
            skill_power = skill.power if skill else 1.0

        # 必闪
        if self.has_buff(defender, 'sure_dodge'):
            self.log.append(f"{defender.name} 闪避了攻击（必闪）！")
            return False

        # 闪避判定
        dodge_prob = 0.0 if self.has_buff(attacker, 'sure_hit') else self.dodge_chance(attacker, defender)
        if self.rng.random() < dodge_prob:
            self.log.append(f"{defender.name} 闪避了攻击！")
            return False

        dmg = self.damage.calculate(attacker, defender, skill_power, DamageKind.NORMAL)
        defender.hp = round(defender.hp - dmg, 2)
        self.log.append(f"{attacker.name} 对 {defender.name} 造成 {round(dmg)} 点伤害")

        if attacker is self.player and defender is self.monster:
            self.player_damage_dealt_this_turn += dmg

        self.bus.emit(DamageEvent(source=attacker, target=defender,
                                  amount=dmg, kind=DamageKind.NORMAL, skill=skill))

        # 普通附伤（走防御减免）
        bonus_flat = self.buff_total(attacker, 'bonus_flat')
        if bonus_flat > 0:
            eff_def = max(0, defender.defense - getattr(attacker, 'pen', 0))
            bd = round(bonus_flat / (1.0 + 0.01 * eff_def), 2)
            defender.hp = round(defender.hp - bd, 2)
            self.log.append(f"{attacker.name} 附带 {round(bd)} 点伤害")
            if attacker is self.player and defender is self.monster:
                self.player_damage_dealt_this_turn += bd

        # 真实附伤
        bonus_true = self.buff_total(attacker, 'bonus_true')
        if bonus_true > 0:
            defender.hp = round(defender.hp - bonus_true, 2)
            self.log.append(f"{attacker.name} 附加 {round(bonus_true)} 点真实伤害")
            if attacker is self.player and defender is self.monster:
                self.player_damage_dealt_this_turn += bonus_true

        # 风暴降临附加真实伤害
        if attacker is self.player and self._has_storm_buff():
            extra = self.apply_sunset(self._storm_extra_damage())
            defender.hp = round(defender.hp - extra, 2)
            self.player_damage_dealt_this_turn += extra
            self.log.append(f"风暴降临附加 {round(extra)} 点真实伤害！")
        return True

    # ================= 技能 =================
    def get_active_skills(self):
        skills = [self.ATTACK_SKILL, self.DEFEND_SKILL]
        for s in self.player.equipped_skills:
            if s.type in ('active', 'buff', 'heal'):
                skills.append(s)
        return skills

    def _init_cooldowns(self):
        for skill in self.get_active_skills():
            self.skill_cooldowns[skill.name] = 0

    # ================= 战斗流程 =================
    def start(self):
        self._init_cooldowns()
        self._register_passive_listeners()
        self.bus.emit(BattleStart())

        # 世界Boss初始化
        if self.monster.world_boss:
            self.monster.max_hp = 9999999.0
            self.monster.hp = 9999999.0
            self.world_boss_initial_hp = self.monster.hp
            self.player.energy = round(self.player.max_energy * 0.2, 2)
            self.log.append(f"世界Boss {self.monster.name} 降临！血量近乎无限，每回合属性增强3%。初始能量降至20%")

        self._next_turn()

    def _register_passive_listeners(self):
        for skill in self.player.passive_skills:
            for event_name, fn in get_passive_listeners(skill.name):
                self.bus.on(event_name, lambda event, f=fn: f(self, event))

    def _next_turn(self):
        self.turn_count += 1
        self.player_damage_dealt_this_turn = 0.0
        self.monster_is_first = False
        self.log.append(f"--- 第 {self.turn_count} 回合 ---")

        self.bus.emit(TurnStart(turn=self.turn_count))

        # 通用每回合恢复（regen buff）
        regen = self.buff_total(self.player, 'regen')
        if regen > 0:
            self.player.hp = min(self.player.max_hp, round(self.player.hp + regen, 2))
            self.log.append(f"每回合恢复 {round(regen)} 点生命")

        self.turn = 'player'
        self._signal()

    def _end_of_turn(self):
        # 怪物防御反击结算
        defend_buff = self._get_monster_defend_buff()
        if defend_buff and defend_buff.remaining == 1:
            if self.player_damage_dealt_this_turn > 0:
                counter = self.monster.attack * 0.4 / (1 + 0.01 * self.player.defense)
                counter += self.player_damage_dealt_this_turn * 0.4
                counter = round(counter, 2)
                self.player.hp = round(self.player.hp - counter, 2)
                self.log.append(f"{self.monster.name} 防御反击！对你造成 {round(counter)} 点伤害")
            else:
                penalty = round(self.monster.agility * 0.5, 2)
                self.apply_buff_effect(self.monster, {'name': '敏捷削弱', 'stat': 'agility', 'amount': -penalty}, 2, is_debuff=True)
                self.log.append(f"{self.monster.name} 防御失败，下回合敏捷降低50%")

        self.process_buffs(self.player)
        self.process_buffs(self.monster)

        # 世界Boss每回合成长
        if self.monster.world_boss:
            self.monster.attack = round(self.monster.attack * 1.03, 2)
            self.monster.defense = round(self.monster.defense * 1.03, 2)
            self.monster.agility = round(self.monster.agility * 1.03, 2)
            if self.turn_count % 5 == 0:
                self.log.append(f"{self.monster.name} 属性增强！攻击 {self.monster.attack:.0f} 防御 {self.monster.defense:.0f} 敏捷 {self.monster.agility:.0f}")

        # 冷却递减
        for name in list(self.skill_cooldowns.keys()):
            if name in self._cd_grace:
                self._cd_grace.discard(name)
                continue
            if self.skill_cooldowns[name] > 0:
                self.skill_cooldowns[name] -= 1

        self.bus.emit(TurnEnd(turn=self.turn_count))

        if self.state == 'ongoing':
            self._next_turn()

    def _get_monster_defend_buff(self):
        for buff in self.monster.buffs:
            if buff.name == '防御反击':
                return buff
        return None

    def _signal(self):
        if self.log_signal:
            self.log_signal(self)

    # ================= 怪物行动 =================
    def _monster_action(self):
        if self.has_buff(self.monster, 'stun'):
            self.log.append(f"{self.monster.name} 被眩晕，无法行动！")
            return
        will_defend = self.rng.random() < self.monster.defend_chance

        if self.defend_counter:
            if will_defend:
                self.log.append(f"{self.monster.name} 使用防御反击，你的防御反击被破解！")
                self.defend_counter = False
                penalty = round(self.player.agility * 0.5, 2)
                self.apply_buff_effect(self.player, {'name': '敏捷削弱', 'stat': 'agility', 'amount': -penalty}, 2, is_debuff=True)
                self._apply_monster_defend()
            else:
                dodge_prob = self.dodge_chance(self.monster, self.player)
                if self.rng.random() < dodge_prob:
                    self.log.append(f"{self.player.name} 闪避了攻击！")
                    self.defend_counter = False
                else:
                    raw_dmg = self.damage.calculate(self.monster, self.player, 1.0, DamageKind.NORMAL)
                    actual_dmg = round(raw_dmg * 0.5, 2)
                    self.player.hp = round(self.player.hp - actual_dmg, 2)
                    self.log.append(f"{self.monster.name} 对 {self.player.name} 造成 {round(actual_dmg)} 点伤害（减半）")

                    effective_def = max(0, self.monster.defense - self.player.pen)
                    defense_factor = 1.0 / (1.0 + 0.01 * effective_def)
                    attack_part = round(self.player.attack * defense_factor * 0.4, 2)
                    counter_dmg = round(attack_part + raw_dmg * 0.2, 2)
                    counter_dmg = self.apply_sunset(counter_dmg)
                    self.monster.hp = round(self.monster.hp - counter_dmg, 2)
                    self.log.append(f"防御反击！对 {self.monster.name} 造成 {round(counter_dmg)} 点伤害")

                    energy_gain = round(2 + self.player.max_energy * 0.02, 2)
                    self.player.energy = min(self.player.max_energy, round(self.player.energy + energy_gain, 2))
                    self.log.append(f"恢复 {round(energy_gain)} 点能量")
                    self.defend_counter = False
        else:
            if will_defend:
                self._apply_monster_defend()
            else:
                self.perform_attack(self.monster, self.player)

    def _apply_monster_defend(self):
        duration = 1 if self.monster_is_first else 2
        self.log.append(f"{self.monster.name} 进入防御反击状态！" + ("本回合生效" if duration == 1 else "下回合生效"))
        self.apply_buff_effect(self.monster, {'name': '防御反击', 'stat': 'none', 'amount': 0}, duration)

    # ================= 玩家行动 =================
    def _energy_cost(self, skill) -> float:
        need = skill.energy_cost
        if skill.name == '治疗':
            need = 5 + round(self.player.max_energy * 0.07, 2)
        elif skill.name == '怒击':
            need = 5 + round(self.player.max_energy * 0.07, 2)
        elif skill.name == '三连击':
            need = 5 + round(self.player.max_energy * 0.07, 2)
        elif skill.name == '狂暴之力':
            need = 5 + round(self.player.max_energy * 0.04, 2)
        elif skill.name == '盛怒绽放':
            need = round(self.player.max_energy * 0.25, 2)
        elif skill.name == '繁荣不息':
            need = self._get_gear_level('护甲')
        return need

    def _get_gear_level(self, slot) -> int:
        gear = self.player.gear.get(slot)
        if gear and gear.get('equipment'):
            return int(gear.get('level', 0))
        return 0

    def player_action(self, skill):
        if self.state != 'ongoing' or self.turn != 'player':
            return

        # 玩家眩晕
        if self.has_buff(self.player, 'stun'):
            self.log.append("你被眩晕，无法行动！")
            self.monster_is_first = True
            self._monster_action()
            self.check_end()
            if self.state == 'ongoing':
                self._end_of_turn()
            else:
                self._signal()
            return

        # 冷却检查
        cd = self.skill_cooldowns.get(skill.name, 0)
        if cd > 0:
            self.log.append(f"{skill.name} 还在冷却中，剩余 {cd} 回合")
            self._signal()
            return

        # 能量检查
        need_energy = self._energy_cost(skill)
        if need_energy > 0 and self.player.energy < need_energy:
            self.log.append("能量不足！")
            self._signal()
            return

        self.player.energy = max(0.0, round(self.player.energy - need_energy, 2))

        # 设置冷却
        if skill.name == '治疗':
            cooldown = 3
        elif skill.name == '怒击':
            cooldown = 2
        elif skill.name == '三连击':
            cooldown = 2
        else:
            cooldown = skill.cooldown
        if cooldown > 0:
            self.skill_cooldowns[skill.name] = cooldown
            self._cd_grace.add(skill.name)

        # 先后手
        if skill.name == '防御反击':
            self.monster_is_first = False
        else:
            player_first = self.player.agility >= self.monster.agility
            self.monster_is_first = not player_first

        first_strike = (skill.name == '防御反击'
                        or skill.name in FIRST_STRIKE_SKILLS)

        if first_strike:
            self._execute_player_skill(skill)
            self.check_end()
            if self.state == 'ongoing':
                self._monster_action()
                self.check_end()
        else:
            if not self.monster_is_first:
                self._execute_player_skill(skill)
                self.check_end()
                if self.state == 'ongoing':
                    self._monster_action()
                    self.check_end()
            else:
                self._monster_action()
                self.check_end()
                if self.state == 'ongoing' and self.player.hp > 0:
                    self._execute_player_skill(skill)
                    self.check_end()

        if self.state == 'ongoing':
            self._end_of_turn()
        else:
            self._signal()

    def _execute_player_skill(self, skill) -> bool:
        handler = get_active_handler(skill.name)
        if handler is not None:
            return handler(self, skill)
        return False

    def check_end(self):
        if self.player.hp <= 0:
            self.player.hp = 0.0
            self.state = 'lose'
            self.log.append(f"你被 {self.monster.name} 击败了...")
            if self.monster.world_boss:
                total_dmg = round(self.world_boss_initial_hp - self.monster.hp, 2)
                self.log.append(f"本次对世界Boss造成了 {total_dmg} 点伤害")
            self.bus.emit(BattleEnd(result='lose'))
        elif self.monster.hp <= 0:
            self.monster.hp = 0.0
            self.state = 'win'
            self.log.append(f"你获得了胜利！击败了 {self.monster.name}")
            self.bus.emit(BattleEnd(result='win'))
        self._signal()

    def escape(self):
        if self.state != 'ongoing':
            return
        self.state = 'lose'
        self.log.append(f"你从 {self.monster.name} 面前逃跑了...")
        if self.monster.world_boss:
            total_dmg = round(self.world_boss_initial_hp - self.monster.hp, 2)
            self.log.append(f"本次对世界Boss造成了 {total_dmg} 点伤害")
        self.bus.emit(BattleEnd(result='escape'))
        self._signal()
