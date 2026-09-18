import random
from typing import Dict, List, Optional

class Spell:
    def __init__(self, name: str, description: str, mana_cost: int, damage: int, effect: str, spell_type: str):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.damage = damage
        self.effect = effect
        self.spell_type = spell_type  # attack, defense, utility

class SpellSystem:
    def __init__(self):
        self.available_spells = self._initialize_spells()
        self.learned_spells = {}  # user_id: List[Spell]
    
    def _initialize_spells(self) -> Dict[str, Spell]:
        """마법 주문 초기화 (Harry Potter 스타일)"""
        return {
            # 기초 마법
            '루모스': Spell(
                name='루모스',
                description='빛의 마법 주문',
                mana_cost=5,
                damage=10,
                effect='작은 빛의 구체',
                spell_type='attack'
            ),
            '플립펜도': Spell(
                name='플립펜도',
                description='물체를 띄우는 마법',
                mana_cost=8,
                damage=15,
                effect='목표를 비틀어뜨',
                spell_type='attack'
            ),
            '윙가디움 레비오사': Spell(
                name='윙가디움 레비오사',
                description='잎사 주문',
                mana_cost=10,
                damage=20,
                effect='빨간 방어막 생성',
                spell_type='defense'
            ),
            '엑스펙토': Spell(
                name='엑스펙토',
                description='방어 마법 주문',
                mana_cost=12,
                damage=0,
                effect='적의 공격을 막음',
                spell_type='defense'
            ),
            '아구아멘티': Spell(
                name='아구아멘티',
                description='무장 해제 마법',
                mana_cost=15,
                damage=0,
                effect='무기를 공격하는 마법',
                spell_type='utility'
            ),
            
            # 중급 마법
            '스투페디': Spell(
                name='스투펜디',
                description='신경 마법 주문',
                mana_cost=15,
                damage=25,
                effect='적의 신경을 마비',
                spell_type='attack'
            ),
            '푸르고': Spell(
                name='푸르고',
                description='불의 마법 주문',
                mana_cost=18,
                damage=30,
                effect='불구체 공격',
                spell_type='attack'
            ),
            '아쿠시오': Spell(
                name='아쿠시오',
                description='방어 마법 주문',
                mana_cost=20,
                damage=0,
                effect='더 강력한 방어막',
                spell_type='defense'
            ),
            '루모스 맥시마': Spell(
                name='루모스 맥시마',
                description='최대 광선 주문',
                mana_cost=25,
                damage=40,
                effect='강력한 빛의 공격',
                spell_type='attack'
            ),
            
            # 고급 마법
            '페트리피쿠스': Spell(
                name='페트리피쿠스',
                description='매혈 마법 주문',
                mana_cost=30,
                damage=35,
                effect='목표를 비틀어뜨',
                spell_type='attack'
            ),
            '임페리오': Spell(
                name='임페리오',
                description='사해 주문',
                mana_cost=35,
                damage=45,
                effect='모든 것을 파괴',
                spell_type='attack'
            ),
            '애비오케드바': Spell(
                name='애비오케드바',
                description='소환 마법 주문',
                mana_cost=40,
                damage=50,
                effect='비밀을 공개하는 마법',
                spell_type='attack'
            ),
            '프로테고 맥시마': Spell(
                name='프로테고 맥시마',
                description='고대 보호 주문',
                mana_cost=50,
                damage=0,
                effect='전체 보호막',
                spell_type='defense'
            ),
            
            # 전설급 마법
            '엑스펙리아마스 맥시마': Spell(
                name='엑스펙리아마스 맥시마',
                description='최고 방어 주문',
                mana_cost=60,
                damage=0,
                effect='모든 것을 막음',
                spell_type='defense'
            ),
            '피니테 인칸타템': Spell(
                name='피니테 인칸타템',
                description='죽음을 부활하는 주문',
                mana_cost=80,
                damage=0,
                effect='목표를 되살림',
                spell_type='utility'
            )
        }
    
    def get_spell(self, spell_name: str) -> Optional[Spell]:
        """특정 마법 정보 가져오기"""
        return self.available_spells.get(spell_name)
    
    def get_available_spells(self, user_level: int) -> List[Spell]:
        """레벨에 따른 사용 가능한 마법"""
        available = []
        
        if user_level >= 1:
            basic_spells = ['루모스', '플립펜도', '윙가디움 레비오사', '엑스펙토', '아구아멘티']
            available.extend([self.available_spells[name] for name in basic_spells if name in self.available_spells])
        
        if user_level >= 10:
            intermediate_spells = ['스투펜디', '푸르고', '아쿠시오', '루모스 맥시마']
            available.extend([self.available_spells[name] for name in intermediate_spells if name in self.available_spells])
        
        if user_level >= 20:
            advanced_spells = ['페트리피쿠스', '임페리오', '애비오케드바', '프로테고 맥시마']
            available.extend([self.available_spells[name] for name in advanced_spells if name in self.available_spells])
        
        if user_level >= 40:
            legendary_spells = ['엑스펙리아마스 맥시마', '피니테 인칸타템']
            available.extend([self.available_spells[name] for name in legendary_spells if name in self.available_spells])
        
        return available
    
    def cast_spell(self, spell: Spell, caster_mp: int) -> tuple:
        """마법 시전"""
        if caster_mp < spell.mana_cost:
            return False, "마력이 부족합니다", 0
        
        success = random.random() < 0.9  # 90% 성공률
        if success:
            damage = spell.damage + random.randint(-5, 5)
            return True, f"{spell.name} 시전 성공! {spell.effect}", damage
        else:
            return False, f"{spell.name} 시전 실패...", 0
    
    def learn_spell(self, user_id: str, spell_name: str) -> bool:
        """마법 배우기"""
        if user_id not in self.learned_spells:
            self.learned_spells[user_id] = []
        
        if spell_name in self.learned_spells[user_id]:
            return False  # 이미 배움
        
        if spell_name in self.available_spells:
            self.learned_spells[user_id].append(spell_name)
            return True
        
        return False
    
    def get_learned_spells(self, user_id: str) -> List[str]:
        """배운 마법 목록"""
        return self.learned_spells.get(user_id, [])
    
    def cast_by_chant(self, chant: str, user_id: str, caster_mp: int) -> tuple:
        """주문으로 마법 시전"""
        # 주문-마법 매핑
        chant_mapping = {
            '루모스': '루모스',
            '루모스 맥시마': '루모스 맥시마',
            '윙가디움': '윙가디움 레비오사',
            '엑스펙토': '엑스펙토',
            '아구아멘티': '아구아멘티',
            '스투펜디': '스투펜디',
            '푸르고': '푸르고',
            '아쿠시오': '아쿠시오',
            '페트리피쿠스': '페트리피쿠스',
            '임페리오': '임페리오',
            '애비오케드바': '애비오케드바',
            '프로테고': '프로테고 맥시마',
            '프로테고 맥시마': '프로테고 맥시마',
            '피니테': '피니테 인칸타템',
            '피니테 인칸타템': '피니테 인칸타템'
        }
        
        # 주문 매칭
        matched_spell = None
        for chant_key, spell_name in chant_mapping.items():
            if chant_key in chant.lower():
                matched_spell = self.available_spells.get(spell_name)
                break
        
        if not matched_spell:
            return False, "알 수 없는 주문입니다", 0
        
        # 해당 마법을 배웠는지 확인
        learned_spells = self.get_learned_spells(user_id)
        if matched_spell.name not in learned_spells:
            return False, f"{matched_spell.name} 마법을 배우지 않았습니다", 0
        
        return self.cast_spell(matched_spell, caster_mp)