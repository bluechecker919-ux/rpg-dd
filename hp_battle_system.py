import random
from typing import List, Dict, Any, Optional
from rpg_system import Character
from spell_system import SpellSystem

class HogwartsBattle:
    def __init__(self, player: Character, enemy_name: str, enemy_level: int):
        self.player = player
        self.enemy_name = enemy_name
        self.enemy_level = enemy_level
        
        # 적 능력치
        self.enemy_max_hp = 30 + (enemy_level * 15)
        self.enemy_current_hp = self.enemy_max_hp
        self.enemy_attack = 5 + (enemy_level * 3)
        self.enemy_defense = 2 + (enemy_level * 1)
        
        # 전투 시스템
        self.turn = 0
        self.in_progress = True
        self.duel_rotation = []  # 턴제 듀얼로이테이션
        self.current_duelist = None
        self.battle_log = []
        
        # 마법 시스템
        self.spell_system = SpellSystem()
        
        # 하우스포인트 시스템
        self.player_house_points = 0
        self.enemy_house_points = 0
    
    def add_log(self, message: str):
        self.battle_log.append(message)
    
    def get_duel_rotation(self) -> List:
        """턴제 듀얼로이테이션 결정"""
        rotation = [self.player, self.enemy_name]
        if self.player.speed >= 10:  # 플레이어가 빠르면 먼저 공격
            return rotation
        else:
            return rotation[::-1]  # 적이 먼저 공격
    
    def cast_harry_potter_spell(self, spell_name: str) -> Dict[str, Any]:
        """Harry Potter 스타일 마법 시전"""
        spell = self.spell_system.get_spell(spell_name)
        
        if not spell:
            return {'error': '알 수 없는 마법입니다.'}
        
        if self.player.current_mp < spell.mana_cost:
            return {'error': f'마력이 부족합니다. 필요: {spell.mana_cost}'}
        
        # 마법 시전
        success, message, damage = self.spell_system.cast_spell(spell, self.player.current_mp)
        
        if not success:
            return {'error': message}
        
        self.player.current_mp -= spell.mana_cost
        
        # 마법 효과 적용
        if spell.spell_type == 'attack':
            actual_damage = max(1, damage - (self.enemy_defense // 2))
            self.enemy_current_hp = max(0, self.enemy_current_hp - actual_damage)
            return {
                'success': True,
                'message': message,
                'damage': actual_damage,
                'enemy_hp': self.enemy_current_hp,
                'enemy_max_hp': self.enemy_max_hp,
                'defeated': not self.is_enemy_alive()
            }
        elif spell.spell_type == 'defense':
            self.player.current_hp = min(self.player.current_hp + spell.damage, self.player.max_hp)
            return {
                'success': True,
                'message': message,
                'heal': spell.damage,
                'current_hp': self.player.current_hp,
                'max_hp': self.player.max_hp
            }
        else:
            return {
                'success': True,
                'message': message,
                'effect': spell.effect
            }
    
    def perform_basic_attack(self, attacker: str) -> Dict[str, Any]:
        """기본 공격 수행"""
        if attacker == self.player.name:
            damage = self.player.attack + random.randint(-2, 2)
            actual_damage = max(1, damage - (self.enemy_defense // 2))
            self.enemy_current_hp = max(0, self.enemy_current_hp - actual_damage)
            
            return {
                'attacker': self.player.name,
                'defender': self.enemy_name,
                'damage': actual_damage,
                'enemy_hp': self.enemy_current_hp,
                'enemy_max_hp': self.enemy_max_hp,
                'defeated': not self.is_enemy_alive()
            }
        else:
            damage = self.enemy_attack + random.randint(-2, 2)
            actual_damage = max(1, damage - (self.player.defense // 2))
            self.player.current_hp = max(0, self.player.current_hp - actual_damage)
            
            return {
                'attacker': self.enemy_name,
                'defender': self.player.name,
                'damage': actual_damage,
                'player_hp': self.player.current_hp,
                'player_max_hp': self.player.max_hp,
                'defeated': not self.is_player_alive()
            }
    
    def is_enemy_alive(self) -> bool:
        return self.enemy_current_hp > 0
    
    def is_player_alive(self) -> bool:
        return self.player.current_hp > 0
    
    def process_turn(self, action: str, spell_name: Optional[str] = None) -> Dict[str, Any]:
        """턴 처리"""
        if not self.in_progress:
            return {'error': '전투가 이미 종료되었습니다.'}
        
        results = []
        rotation = self.get_duel_rotation()
        
        for actor in rotation:
            if not self.in_progress:
                break
            
            if actor == self.player.name:
                if action == 'attack':
                    result = self.perform_basic_attack(actor)
                    self.add_log(f"🗡️ {self.player.name}이(가) {self.enemy_name}에게 {result['damage']} 데미지를 입혔습니다!")
                    results.append(result)
                    
                    if result.get('defeated', False):
                        self.in_progress = False
                        self.player_house_points += 10
                        return {'battle_end': True, 'winner': 'player', 'results': results}
                
                elif action == 'spell' and spell_name:
                    result = self.cast_harry_potter_spell(spell_name)
                    if 'error' in result:
                        return result
                    self.add_log(f"✨ {self.player.name}이(가) {spell_name} 시전! {result['message']}")
                    results.append(result)
                    
                    if result.get('defeated', False):
                        self.in_progress = False
                        self.player_house_points += 15
                        return {'battle_end': True, 'winner': 'player', 'results': results}
                
                elif action == 'defend':
                    self.player.current_hp = min(self.player.current_hp + 10, self.player.max_hp)
                    self.add_log(f"🛡️ {self.player.name}이(가) 방어 태세를 취합니다!")
                    results.append({'action': 'defend', 'actor': self.player.name})
                
                elif action == 'disarm':
                    self.add_log(f"⚔️ {self.player.name}이(가) 무장 해제 마법을 시전합니다!")
                    results.append({'action': 'disarm', 'actor': self.player.name})
                    # 실제 효과: 적의 공격력 감소
                    self.enemy_attack = max(1, self.enemy_attack - 5)
            
            else:  # Enemy turn
                result = self.perform_basic_attack(actor)
                self.add_log(f"👹 {self.enemy_name}이(가) {self.player.name}에게 {result['damage']} 데미지를 입혔습니다!")
                results.append(result)
                
                if result.get('defeated', False):
                    self.in_progress = False
                    self.enemy_house_points += 10
                    return {'battle_end': True, 'winner': 'enemy', 'results': results}
        
        self.turn += 1
        return {'battle_end': False, 'results': results, 'turn': self.turn}
    
    def get_battle_status(self) -> Dict[str, Any]:
        """전투 상태"""
        return {
            'player_hp': f"{self.player.current_hp}/{self.player.max_hp}",
            'player_mp': f"{self.player.current_mp}/{self.player.max_mp}",
            'enemy_hp': f"{self.enemy_current_hp}/{self.enemy_max_hp}",
            'enemy_name': self.enemy_name,
            'turn': self.turn,
            'in_progress': self.in_progress,
            'log': self.battle_log[-3:]  # 최근 3개 로그
        }