from typing import Dict, List, Set
from database import Database

class Compendium:
    def __init__(self):
        self.db = Database()
    
    def get_compendium(self, user_id: str) -> Dict[str, Set[str]]:
        """사용자의 도감 데이터 가져오기"""
        compendium_data = self.db.data.get('compendiums', {})
        user_compendium = compendium_data.get(user_id, {
            'monsters': set(),
            'items': set(),
            'bosses': set()
        })
        return user_compendium
    
    def save_compendium(self, user_id: str, compendium_data: Dict[str, Set[str]]):
        """도감 데이터 저장"""
        if 'compendiums' not in self.db.data:
            self.db.data['compendiums'] = {}
        
        # Set을 리스트로 변환하여 저장
        save_data = {
            'monsters': list(compendium_data['monsters']),
            'items': list(compendium_data['items']),
            'bosses': list(compendium_data['bosses'])
        }
        
        self.db.data['compendiums'][user_id] = save_data
        self.db.save()
    
    def add_monster(self, user_id: str, monster_name: str) -> bool:
        """몬스터를 도감에 추가"""
        compendium = self.get_compendium(user_id)
        
        if monster_name not in compendium['monsters']:
            compendium['monsters'].add(monster_name)
            self.save_compendium(user_id, compendium)
            return True  # 새로 추가됨
        return False  # 이미 있음
    
    def add_item(self, user_id: str, item_name: str) -> bool:
        """아이템을 도감에 추가"""
        compendium = self.get_compendium(user_id)
        
        if item_name not in compendium['items']:
            compendium['items'].add(item_name)
            self.save_compendium(user_id, compendium)
            return True
        return False
    
    def add_boss(self, user_id: str, boss_name: str) -> bool:
        """보스를 도감에 추가"""
        compendium = self.get_compendium(user_id)
        
        if boss_name not in compendium['bosses']:
            compendium['bosses'].add(boss_name)
            self.save_compendium(user_id, compendium)
            return True
        return False
    
    def get_completion_rate(self, user_id: str) -> Dict[str, float]:
        """도감 완성률 계산"""
        compendium = self.get_compendium(user_id)
        
        # 전체 몬스터/아이템/보스 수 (실제 게임 데이터에 맞춰 조정 필요)
        total_monsters = 20  # 예시
        total_items = 50     # 예시
        total_bosses = 10    # 예시
        
        monster_rate = (len(compendium['monsters']) / total_monsters) * 100
        item_rate = (len(compendium['items']) / total_items) * 100
        boss_rate = (len(compendium['bosses']) / total_bosses) * 100
        total_rate = ((len(compendium['monsters']) + len(compendium['items']) + len(compendium['bosses'])) / 
                      (total_monsters + total_items + total_bosses)) * 100
        
        return {
            'monsters': monster_rate,
            'items': item_rate,
            'bosses': boss_rate,
            'total': total_rate
        }
    
    def get_unlocked_rewards(self, user_id: str) -> List[str]:
        """도감 완성 보상 확인"""
        completion = self.get_completion_rate(user_id)
        rewards = []
        
        if completion['monsters'] >= 50:
            rewards.append("🎖️ 몬스터 도감 50% 달성 보상: 골드 +1000")
        if completion['monsters'] >= 100:
            rewards.append("🏆 몬스터 도감 완성 보상: 전체 능력치 +5")
        
        if completion['items'] >= 50:
            rewards.append("🎖️ 아이템 도감 50% 달성 보상: 골드 +2000")
        if completion['items'] >= 100:
            rewards.append("🏆 아이템 도감 완성 보상: 인벤토리 슬롯 +10")
        
        if completion['bosses'] >= 50:
            rewards.append("🎖️ 보스 도감 50% 달성 보상: 골드 +3000")
        if completion['bosses'] >= 100:
            rewards.append("🏆 보스 도감 완성 보상: 특수 스킬 해금")
        
        return rewards