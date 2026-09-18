import random
from typing import Dict, List, Tuple
from item_system import ItemFactory, Item

class GachaSystem:
    def __init__(self):
        self.rarity_weights = {
            'common': 60,      # 60%
            'uncommon': 25,    # 25%
            'rare': 10,        # 10%
            'epic': 4,         # 4%
            'legendary': 1     # 1%
        }
        
        self.gacha_items = self._initialize_gacha_items()
    
    def _initialize_gacha_items(self) -> Dict[str, List[str]]:
        """뽑기 아이템 초기화"""
        return {
            'common': [
                'potion_hp_small', 'potion_mp_small', 'herb', 'ore_iron'
            ],
            'uncommon': [
                'potion_hp_medium', 'potion_mp_medium', 'sword_iron', 'bow_wood'
            ],
            'rare': [
                'potion_hp_large', 'sword_steel', 'bow_composite', 'staff_basic'
            ],
            'epic': [
                'sword_magic', 'staff_fire', 'armor_chain', 'robe_apprentice'
            ],
            'legendary': [
                'armor_plate', 'robe_master', 'crystal'
            ]
        }
    
    def pull_gacha(self, pull_count: int = 1) -> List[Dict]:
        """뽑기 실행"""
        results = []
        
        for _ in range(pull_count):
            rarity = self._get_random_rarity()
            item_id = random.choice(self.gacha_items[rarity])
            item = ItemFactory.create_item(item_id)
            
            results.append({
                'item': item,
                'rarity': rarity,
                'is_new': True  # 추후 구현 시 실제 신규 여부 체크
            })
        
        return results
    
    def _get_random_rarity(self) -> str:
        """랜덤 희귀도 결정"""
        rand = random.random() * 100
        cumulative = 0
        
        for rarity, weight in self.rarity_weights.items():
            cumulative += weight
            if rand <= cumulative:
                return rarity
        
        return 'common'  # 기본값
    
    def get_pull_cost(self, pull_count: int = 1) -> int:
        """뽑기 비용 계산"""
        base_cost = 100  # 기본 1회 비용
        if pull_count == 10:
            return int(base_cost * 10 * 0.9)  # 10회 뽑기 시 10% 할인
        return base_cost * pull_count
    
    def format_rarity_emoji(self, rarity: str) -> str:
        """희귀도 이모지"""
        rarity_emojis = {
            'common': '⚪',
            'uncommon': '🟢',
            'rare': '🔵',
            'epic': '🟣',
            'legendary': '🟡'
        }
        return rarity_emojis.get(rarity, '⚪')
    
    def get_pity_system_info(self, user_pulls: int) -> Dict:
        """피티 시스템 정보"""
        # 90회마다 레전더리 보장
        legendary_pity = 90
        pulls_until_legendary = legendary_pity - (user_pulls % legendary_pity)
        
        # 10회마다 에픽 이상 보장
        epic_pity = 10
        pulls_until_epic = epic_pity - (user_pulls % epic_pity)
        
        return {
            'legendary_pity': pulls_until_legendary,
            'epic_pity': pulls_until_epic,
            'total_pulls': user_pulls
        }