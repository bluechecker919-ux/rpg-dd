from typing import Dict, List, Any
from enum import Enum

class ItemType(Enum):
    WEAPON = "무기"
    ARMOR = "방어구"
    POTION = "포션"
    MATERIAL = "재료"
    QUEST = "퀘스트 아이템"

class Item:
    def __init__(self, item_id: str, name: str, item_type: ItemType, description: str, 
                 price: int = 0, stat_bonus: Dict[str, int] = None, consumable: bool = False):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.price = price
        self.stat_bonus = stat_bonus or {}
        self.consumable = consumable
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'item_type': self.item_type.value,
            'description': self.description,
            'price': self.price,
            'stat_bonus': self.stat_bonus,
            'consumable': self.consumable
        }

class Inventory:
    def __init__(self, max_slots: int = 20):
        self.items: Dict[str, int] = {}  # item_id: quantity
        self.max_slots = max_slots
        self.equipped = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
    
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        if item.item_id in self.items:
            self.items[item.item_id] += quantity
            return True
        
        if len(self.items) < self.max_slots:
            self.items[item.item_id] = quantity
            return True
        
        return False
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        if item_id not in self.items:
            return False
        
        if self.items[item_id] >= quantity:
            self.items[item_id] -= quantity
            if self.items[item_id] <= 0:
                del self.items[item_id]
            return True
        
        return False
    
    def get_item_quantity(self, item_id: str) -> int:
        return self.items.get(item_id, 0)
    
    def get_all_items(self) -> List[str]:
        return list(self.items.keys())
    
    def equip_item(self, item: Item, slot: str) -> bool:
        if item.item_id not in self.items:
            return False
        
        if slot not in self.equipped:
            return False
        
        # 아이템 타입 확인
        valid_slots = {
            ItemType.WEAPON: ['weapon'],
            ItemType.ARMOR: ['armor'],
            ItemType.POTION: [],
            ItemType.MATERIAL: [],
            ItemType.QUEST: []
        }
        
        if slot not in valid_slots.get(item.item_type, []):
            return False
        
        # 기존 장비 해제
        if self.equipped[slot]:
            self.add_item(Item(
                self.equipped[slot]['item_id'],
                self.equipped[slot]['name'],
                ItemType(self.equipped[slot]['item_type']),
                self.equipped[slot]['description'],
                self.equipped[slot]['price'],
                self.equipped[slot]['stat_bonus']
            ))
        
        # 새 장비 장착
        self.equipped[slot] = item.to_dict()
        self.remove_item(item.item_id)
        
        return True
    
    def unequip_item(self, slot: str) -> bool:
        if slot not in self.equipped or not self.equipped[slot]:
            return False
        
        equipped_item = self.equipped[slot]
        item = Item(
            equipped_item['item_id'],
            equipped_item['name'],
            ItemType(equipped_item['item_type']),
            equipped_item['description'],
            equipped_item['price'],
            equipped_item['stat_bonus']
        )
        
        if self.add_item(item):
            self.equipped[slot] = None
            return True
        
        return False
    
    def get_stat_bonus(self) -> Dict[str, int]:
        total_bonus = {}
        
        for slot, item_data in self.equipped.items():
            if item_data:
                for stat, bonus in item_data['stat_bonus'].items():
                    total_bonus[stat] = total_bonus.get(stat, 0) + bonus
        
        return total_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'items': self.items,
            'max_slots': self.max_slots,
            'equipped': self.equipped
        }

class ItemFactory:
    @staticmethod
    def create_item(item_id: str) -> Item:
        items = {
            # 무기
            'sword_iron': Item('sword_iron', '철검', ItemType.WEAPON, '기본적인 철검', 100, {'attack': 5}),
            'sword_steel': Item('sword_steel', '강철검', ItemType.WEAPON, '튼튼한 강철검', 300, {'attack': 10}),
            'sword_magic': Item('sword_magic', '마법검', ItemType.WEAPON, '마법이 깃든 검', 800, {'attack': 18, 'mp': 20}),
            'bow_wood': Item('bow_wood', '나무 활', ItemType.WEAPON, '기본적인 나무 활', 80, {'attack': 4, 'speed': 2}),
            'bow_composite': Item('bow_composite', '합성 활', ItemType.WEAPON, '강력한 합성 활', 250, {'attack': 9, 'speed': 4}),
            'staff_basic': Item('staff_basic', '기본 지팡이', ItemType.WEAPON, '마법사의 기본 지팡이', 120, {'attack': 3, 'mp': 30}),
            'staff_fire': Item('staff_fire', '불의 지팡이', ItemType.WEAPON, '불의 힘이 담긴 지팡이', 500, {'attack': 8, 'mp': 50}),
            
            # 방어구
            'armor_leather': Item('armor_leather', '가죽 갑옷', ItemType.ARMOR, '기본적인 가죽 갑옷', 80, {'defense': 3, 'hp': 10}),
            'armor_chain': Item('armor_chain', '사슬 갑옷', ItemType.ARMOR, '튼튼한 사슬 갑옷', 200, {'defense': 7, 'hp': 20}),
            'armor_plate': Item('armor_plate', '판금 갑옷', ItemType.ARMOR, '강력한 판금 갑옷', 500, {'defense': 15, 'hp': 40}),
            'robe_apprentice': Item('robe_apprentice', '견습 로브', ItemType.ARMOR, '마법사의 기본 로브', 100, {'defense': 2, 'mp': 20}),
            'robe_master': Item('robe_master', '마스터 로브', ItemType.ARMOR, '고급 마법사 로브', 400, {'defense': 5, 'mp': 50}),
            
            # 포션
            'potion_hp_small': Item('potion_hp_small', '작은 HP 포션', ItemType.POTION, 'HP를 30 회복', 20, {}, True),
            'potion_hp_medium': Item('potion_hp_medium', '중간 HP 포션', ItemType.POTION, 'HP를 70 회복', 50, {}, True),
            'potion_hp_large': Item('potion_hp_large', '큰 HP 포션', ItemType.POTION, 'HP를 150 회복', 100, {}, True),
            'potion_mp_small': Item('potion_mp_small', '작은 MP 포션', ItemType.POTION, 'MP를 20 회복', 25, {}, True),
            'potion_mp_medium': Item('potion_mp_medium', '중간 MP 포션', ItemType.POTION, 'MP를 50 회복', 60, {}, True),
            
            # 재료
            'herb': Item('herb', '허브', ItemType.MATERIAL, '약초 재료', 5),
            'ore_iron': Item('ore_iron', '철광석', ItemType.MATERIAL, '철 제련용 광석', 10),
            'crystal': Item('crystal', '마법 수정', ItemType.MATERIAL, '마법에 사용되는 수정', 50),
        }
        
        return items.get(item_id, Item('unknown', '알 수 없는 아이템', ItemType.MATERIAL, '설명 없음', 0))
    
    @staticmethod
    def get_shop_items() -> List[Item]:
        shop_item_ids = [
            'sword_iron', 'sword_steel', 'bow_wood', 'bow_composite',
            'staff_basic', 'armor_leather', 'armor_chain', 'robe_apprentice',
            'potion_hp_small', 'potion_hp_medium', 'potion_hp_large',
            'potion_mp_small', 'potion_mp_medium', 'herb', 'ore_iron'
        ]
        
        return [ItemFactory.create_item(item_id) for item_id in shop_item_ids]
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Item:
        return Item(
            data['item_id'],
            data['name'],
            ItemType(data['item_type']),
            data['description'],
            data['price'],
            data['stat_bonus'],
            data['consumable']
        )
