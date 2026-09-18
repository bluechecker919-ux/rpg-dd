import random
import config
from typing import Dict, Any, List

class CharacterClass:
    def __init__(self, name: str, description: str, base_stats: Dict[str, int], skills: List[str]):
        self.name = name
        self.description = description
        self.base_stats = base_stats
        self.skills = skills

class Character:
    def __init__(self, user_id: str, name: str, character_class: CharacterClass):
        self.user_id = user_id
        self.name = name
        self.character_class = character_class
        self.level = 1
        self.exp = 0
        self.gold = 100
        
        # 능력치 계산
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.max_mp = self._calculate_max_mp()
        self.current_mp = self.max_mp
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.speed = self._calculate_speed()
        
        # 스킬
        self.skills = character_class.skills.copy()
    
    def _calculate_max_hp(self) -> int:
        base = self.character_class.base_stats.get('hp', 100)
        return base + (self.level * 10)
    
    def _calculate_max_mp(self) -> int:
        base = self.character_class.base_stats.get('mp', 50)
        return base + (self.level * 5)
    
    def _calculate_attack(self) -> int:
        base = self.character_class.base_stats.get('attack', 10)
        return base + (self.level * 2)
    
    def _calculate_defense(self) -> int:
        base = self.character_class.base_stats.get('defense', 5)
        return base + (self.level * 1)
    
    def _calculate_speed(self) -> int:
        base = self.character_class.base_stats.get('speed', 10)
        return base + (self.level * 1)
    
    def gain_exp(self, amount: int) -> bool:
        self.exp += amount
        exp_needed = self._get_exp_needed()
        
        if self.exp >= exp_needed:
            self.exp -= exp_needed
            return self.level_up()
        return False
    
    def _get_exp_needed(self) -> int:
        return int(config.BASE_EXP_REQUIREMENT * (config.EXP_GROWTH_RATE ** (self.level - 1)))
    
    def level_up(self) -> bool:
        if self.level >= config.MAX_LEVEL:
            return False
        
        self.level += 1
        
        # 능력치 재계산
        old_max_hp = self.max_hp
        old_max_mp = self.max_mp
        
        self.max_hp = self._calculate_max_hp()
        self.max_mp = self._calculate_max_mp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.speed = self._calculate_speed()
        
        # HP/MP 회복
        self.current_hp = min(self.current_hp + (self.max_hp - old_max_hp), self.max_hp)
        self.current_mp = min(self.current_mp + (self.max_mp - old_max_mp), self.max_mp)
        
        return True
    
    def heal(self, amount: int):
        self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def restore_mp(self, amount: int):
        self.current_mp = min(self.current_mp + amount, self.max_mp)
    
    def take_damage(self, amount: int):
        actual_damage = max(1, amount - (self.defense // 2))
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'class_name': self.character_class.name,
            'level': self.level,
            'exp': self.exp,
            'gold': self.gold,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'current_mp': self.current_mp,
            'max_mp': self.max_mp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'skills': self.skills
        }

class CharacterFactory:
    @staticmethod
    def get_class(class_name: str) -> CharacterClass:
        classes = {
            '전사': CharacterClass(
                name='전사',
                description='근접 전투의 전문가. 높은 체력과 방어력을 가집니다.',
                base_stats={'hp': 150, 'mp': 30, 'attack': 15, 'defense': 10, 'speed': 8},
                skills=['파워 스트라이크', '방어 태세', '분노의 일격']
            ),
            '마법사': CharacterClass(
                name='마법사',
                description='마법의 힘을 다루는 자. 높은 마력과 공격력을 가집니다.',
                base_stats={'hp': 80, 'mp': 100, 'attack': 20, 'defense': 3, 'speed': 10},
                skills=['파이어볼', '아이스 스파이크', '라이트닝 볼트']
            ),
            '궁수': CharacterClass(
                name='궁수',
                description='원거리 공격의 명수. 높은 속도와 정확도를 가집니다.',
                base_stats={'hp': 100, 'mp': 50, 'attack': 18, 'defense': 5, 'speed': 15},
                skills=['관통 사격', '연사', '맹독 화살']
            ),
            '도적': CharacterClass(
                name='도적',
                description='그림자 속의 암살자. 높은 속도와 치명타 확률을 가집니다.',
                base_stats={'hp': 90, 'mp': 60, 'attack': 16, 'defense': 4, 'speed': 18},
                skills=['암습', '백스탭', '은신']
            )
        }
        return classes.get(class_name, classes['전사'])
    
    @staticmethod
    def create_character(user_id: str, name: str, class_name: str) -> Character:
        character_class = CharacterFactory.get_class(class_name)
        return Character(user_id, name, character_class)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Character:
        character_class = CharacterFactory.get_class(data['class_name'])
        character = Character(data['user_id'], data['name'], character_class)
        
        character.level = data['level']
        character.exp = data['exp']
        character.gold = data['gold']
        character.current_hp = data['current_hp']
        character.max_hp = data['max_hp']
        character.current_mp = data['current_mp']
        character.max_mp = data['max_mp']
        character.attack = data['attack']
        character.defense = data['defense']
        character.speed = data['speed']
        character.skills = data['skills']
        
        return character
