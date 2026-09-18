import random
import asyncio
from typing import List, Dict, Any, Optional
from rpg_system import Character

class Enemy:
    def __init__(self, name: str, level: int, hp: int, attack: int, defense: int, speed: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.current_hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
    
    def take_damage(self, amount: int) -> int:
        actual_damage = max(1, amount - (self.defense // 2))
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def get_attack_damage(self) -> int:
        return self.attack + random.randint(-2, 2)

class Battle:
    def __init__(self, player: Character, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0
        self.battle_log = []
        self.in_progress = True
        self.winner = None
    
    def add_log(self, message: str):
        self.battle_log.append(message)
    
    def get_turn_order(self) -> List:
        if self.player.speed >= self.enemy.speed:
            return [self.player, self.enemy]
        else:
            return [self.enemy, self.player]
    
    def execute_attack(self, attacker, defender) -> Dict[str, Any]:
        if isinstance(attacker, Character):
            damage = attacker.attack + random.randint(-2, 2)
            actual_damage = defender.take_damage(damage)
            attacker_name = attacker.name
        else:
            damage = attacker.get_attack_damage()
            actual_damage = defender.take_damage(damage)
            attacker_name = attacker.name
        
        result = {
            'attacker': attacker_name,
            'defender': defender.name,
            'damage': actual_damage,
            'defender_hp': defender.current_hp,
            'defender_max_hp': defender.max_hp,
            'defeated': not defender.is_alive()
        }
        
        return result
    
    def execute_skill(self, character: Character, skill_name: str) -> Dict[str, Any]:
        # 간단한 스킬 시스템
        skill_effects = {
            '파워 스트라이크': {'damage': 1.5, 'mp_cost': 10},
            '파이어볼': {'damage': 2.0, 'mp_cost': 15},
            '아이스 스파이크': {'damage': 1.8, 'mp_cost': 12},
            '라이트닝 볼트': {'damage': 2.2, 'mp_cost': 18},
            '관통 사격': {'damage': 1.7, 'mp_cost': 8},
            '연사': {'damage': 1.3, 'mp_cost': 10, 'hits': 2},
            '맹독 화살': {'damage': 1.2, 'mp_cost': 10, 'dot': 5},
            '암습': {'damage': 2.5, 'mp_cost': 20},
            '백스탭': {'damage': 3.0, 'mp_cost': 25},
            '은신': {'damage': 0, 'mp_cost': 5, 'evade': True}
        }
        
        if skill_name not in skill_effects:
            return {'error': '알 수 없는 스킬입니다.'}
        
        effect = skill_effects[skill_name]
        
        if character.current_mp < effect['mp_cost']:
            return {'error': 'MP가 부족합니다.'}
        
        character.current_mp -= effect['mp_cost']
        
        base_damage = character.attack * effect.get('damage', 1.0)
        hits = effect.get('hits', 1)
        total_damage = 0
        
        for _ in range(hits):
            damage = int(base_damage + random.randint(-2, 2))
            actual_damage = self.enemy.take_damage(damage)
            total_damage += actual_damage
        
        result = {
            'skill': skill_name,
            'attacker': character.name,
            'damage': total_damage,
            'defender': self.enemy.name,
            'defender_hp': self.enemy.current_hp,
            'defender_max_hp': self.enemy.max_hp,
            'defeated': not self.enemy.is_alive(),
            'mp_used': effect['mp_cost']
        }
        
        return result
    
    def process_turn(self, action: str, skill_name: Optional[str] = None) -> Dict[str, Any]:
        if not self.in_progress:
            return {'error': '전투가 이미 종료되었습니다.'}
        
        turn_order = self.get_turn_order()
        results = []
        
        for actor in turn_order:
            if not self.in_progress:
                break
            
            if isinstance(actor, Character):
                if action == 'attack':
                    result = self.execute_attack(actor, self.enemy)
                    self.add_log(f"🗡️ {actor.name}이(가) {self.enemy.name}에게 {result['damage']} 데미지를 입혔습니다!")
                elif action == 'skill' and skill_name:
                    result = self.execute_skill(actor, skill_name)
                    if 'error' in result:
                        return result
                    self.add_log(f"✨ {actor.name}이(가) {result['skill']} 사용! {self.enemy.name}에게 {result['damage']} 데미지!")
                elif action == 'defend':
                    actor.current_hp = min(actor.current_hp + 5, actor.max_hp)
                    result = {'action': 'defend', 'actor': actor.name}
                    self.add_log(f"🛡️ {actor.name}이(가) 방어 태세를 취합니다! HP 5 회복.")
                else:
                    return {'error': '잘못된 액션입니다.'}
                
                results.append(result)
                
                if result.get('defeated', False):
                    self.winner = actor
                    self.in_progress = False
                    self.add_log(f"🎉 {self.enemy.name}을(를) 물리쳤습니다!")
                    return {'battle_end': True, 'winner': 'player', 'results': results}
            
            else:  # Enemy turn
                result = self.execute_attack(actor, self.player)
                self.add_log(f"👹 {actor.name}이(가) {self.player.name}에게 {result['damage']} 데미지를 입혔습니다!")
                results.append(result)
                
                if result.get('defeated', False):
                    self.winner = actor
                    self.in_progress = False
                    self.add_log(f"💀 {self.player.name}이(가) 패배했습니다...")
                    return {'battle_end': True, 'winner': 'enemy', 'results': results}
        
        self.turn += 1
        return {'battle_end': False, 'results': results, 'turn': self.turn}
    
    def get_battle_status(self) -> Dict[str, Any]:
        player_hp_percent = int((self.player.current_hp / self.player.max_hp) * 100) if self.player.max_hp > 0 else 0
        enemy_hp_percent = int((self.enemy.current_hp / self.enemy.max_hp) * 100) if self.enemy.max_hp > 0 else 0
        
        return {
            'player_name': self.player.name,
            'player_hp': self.player.current_hp,
            'player_max_hp': self.player.max_hp,
            'player_hp_percent': player_hp_percent,
            'player_mp': self.player.current_mp,
            'player_max_mp': self.player.max_mp,
            'player_atk': self.player.attack,
            'player_def': self.player.defense,
            'enemy_name': self.enemy.name,
            'enemy_hp': self.enemy.current_hp,
            'enemy_max_hp': self.enemy.max_hp,
            'enemy_hp_percent': enemy_hp_percent,
            'enemy_atk': self.enemy.attack,
            'enemy_def': self.enemy.defense,
            'turn': self.turn,
            'in_progress': self.in_progress,
            'log': self.battle_log[-5:]  # 최근 5개 로그
        }

class EnemyFactory:
    @staticmethod
    def create_enemy(level: int) -> Enemy:
        enemies = [
            {'name': '슬라임', 'hp': 30, 'attack': 5, 'defense': 2, 'speed': 5, 'exp': 20, 'gold': 10},
            {'name': '고블린', 'hp': 50, 'attack': 8, 'defense': 3, 'speed': 8, 'exp': 35, 'gold': 15},
            {'name': '오크', 'hp': 80, 'attack': 12, 'defense': 5, 'speed': 6, 'exp': 50, 'gold': 25},
            {'name': '스켈레톤', 'hp': 60, 'attack': 10, 'defense': 4, 'speed': 10, 'exp': 45, 'gold': 20},
            {'name': '늑대', 'hp': 40, 'attack': 9, 'defense': 3, 'speed': 12, 'exp': 30, 'gold': 12},
            {'name': '트롤', 'hp': 120, 'attack': 15, 'defense': 8, 'speed': 4, 'exp': 70, 'gold': 35},
            {'name': '드래곤', 'hp': 200, 'attack': 25, 'defense': 15, 'speed': 15, 'exp': 150, 'gold': 100}
        ]
        
        # 레벨에 따른 적 선택
        max_index = min(len(enemies) - 1, level // 10)
        selected_enemy = enemies[max_index]
        
        # 레벨 보정
        level_multiplier = 1 + (level * 0.1)
        
        return Enemy(
            name=selected_enemy['name'],
            level=level,
            hp=int(selected_enemy['hp'] * level_multiplier),
            attack=int(selected_enemy['attack'] * level_multiplier),
            defense=int(selected_enemy['defense'] * level_multiplier),
            speed=int(selected_enemy['speed'] * level_multiplier),
            exp_reward=int(selected_enemy['exp'] * level_multiplier),
            gold_reward=int(selected_enemy['gold'] * level_multiplier)
        )
