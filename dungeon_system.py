import random
from typing import Dict, List, Optional
from battle_system import Battle, EnemyFactory
from rpg_system import Character

class Dungeon:
    def __init__(self, name: str, description: str, min_level: int, max_level: int, stages: List[Dict]):
        self.name = name
        self.description = description
        self.min_level = min_level
        self.max_level = max_level
        self.stages = stages  # 각 스테이지 정보
    
    def get_stage(self, stage_number: int) -> Optional[Dict]:
        """특정 스테이지 정보 가져오기"""
        if 1 <= stage_number <= len(self.stages):
            return self.stages[stage_number - 1]
        return None

class DungeonSystem:
    def __init__(self):
        self.dungeons = self._initialize_dungeons()
        self.active_dungeons = {}  # user_id: dungeon_progress
    
    def _initialize_dungeons(self) -> Dict[str, Dungeon]:
        """던전 초기화"""
        return {
            '슬라임 동굴': Dungeon(
                name='슬라임 동굴',
                description='초보자를 위한 입문 던전',
                min_level=1,
                max_level=10,
                stages=[
                    {'stage': 1, 'enemy_count': 2, 'enemy_level_mult': 1.0, 'reward_gold': 50, 'reward_exp': 30},
                    {'stage': 2, 'enemy_count': 3, 'enemy_level_mult': 1.1, 'reward_gold': 80, 'reward_exp': 50},
                    {'stage': 3, 'enemy_count': 1, 'enemy_level_mult': 1.3, 'is_boss': True, 'reward_gold': 150, 'reward_exp': 100, 'boss_name': '슬라임 킹'}
                ]
            ),
            '고블린 성채': Dungeon(
                name='고블린 성채',
                description='고블린들이 점령한 성채',
                min_level=10,
                max_level=25,
                stages=[
                    {'stage': 1, 'enemy_count': 3, 'enemy_level_mult': 1.2, 'reward_gold': 120, 'reward_exp': 80},
                    {'stage': 2, 'enemy_count': 4, 'enemy_level_mult': 1.3, 'reward_gold': 180, 'reward_exp': 120},
                    {'stage': 3, 'enemy_count': 2, 'enemy_level_mult': 1.4, 'reward_gold': 250, 'reward_exp': 150},
                    {'stage': 4, 'enemy_count': 1, 'enemy_level_mult': 1.6, 'is_boss': True, 'reward_gold': 400, 'reward_exp': 250, 'boss_name': '고블린 왕'}
                ]
            ),
            '드래곤의 둥지': Dungeon(
                name='드래곤의 둥지',
                description='고대 드래곤이 서식하는 위험한 던전',
                min_level=25,
                max_level=50,
                stages=[
                    {'stage': 1, 'enemy_count': 4, 'enemy_level_mult': 1.5, 'reward_gold': 300, 'reward_exp': 200},
                    {'stage': 2, 'enemy_count': 5, 'enemy_level_mult': 1.6, 'reward_gold': 400, 'reward_exp': 280},
                    {'stage': 3, 'enemy_count': 3, 'enemy_level_mult': 1.7, 'reward_gold': 500, 'reward_exp': 350},
                    {'stage': 4, 'enemy_count': 2, 'enemy_level_mult': 1.8, 'reward_gold': 600, 'reward_exp': 420},
                    {'stage': 5, 'enemy_count': 1, 'enemy_level_mult': 2.0, 'is_boss': True, 'reward_gold': 1000, 'reward_exp': 600, 'boss_name': '고대 드래곤'}
                ]
            )
        }
    
    def get_available_dungeons(self, player_level: int) -> List[Dungeon]:
        """플레이어 레벨에 맞는 던전 목록"""
        available = []
        for dungeon in self.dungeons.values():
            if dungeon.min_level <= player_level <= dungeon.max_level:
                available.append(dungeon)
        return available
    
    def start_dungeon(self, user_id: str, dungeon_name: str, character: Character) -> bool:
        """던전 시작"""
        if dungeon_name not in self.dungeons:
            return False
        
        dungeon = self.dungeons[dungeon_name]
        
        if character.level < dungeon.min_level or character.level > dungeon.max_level:
            return False
        
        self.active_dungeons[user_id] = {
            'dungeon': dungeon,
            'current_stage': 1,
            'character': character,
            'completed': False
        }
        
        return True
    
    def get_current_stage(self, user_id: str) -> Optional[Dict]:
        """현재 스테이지 정보"""
        if user_id not in self.active_dungeons:
            return None
        
        progress = self.active_dungeons[user_id]
        dungeon = progress['dungeon']
        stage_num = progress['current_stage']
        
        return dungeon.get_stage(stage_num)
    
    def advance_stage(self, user_id: str) -> bool:
        """다음 스테이지로 진행"""
        if user_id not in self.active_dungeons:
            return False
        
        progress = self.active_dungeons[user_id]
        dungeon = progress['dungeon']
        
        if progress['current_stage'] >= len(dungeon.stages):
            progress['completed'] = True
            return False  # 던전 완료
        
        progress['current_stage'] += 1
        return True
    
    def complete_dungeon(self, user_id: str) -> Dict:
        """던전 완료 처리"""
        if user_id not in self.active_dungeons:
            return {}
        
        progress = self.active_dungeons[user_id]
        dungeon = progress['dungeon']
        
        # 총 보상 계산
        total_gold = 0
        total_exp = 0
        
        for stage in dungeon.stages:
            total_gold += stage.get('reward_gold', 0)
            total_exp += stage.get('reward_exp', 0)
        
        # 완료 보너스
        total_gold = int(total_gold * 1.2)  # 20% 보너스
        total_exp = int(total_exp * 1.2)
        
        del self.active_dungeons[user_id]
        
        return {
            'dungeon_name': dungeon.name,
            'total_gold': total_gold,
            'total_exp': total_exp,
            'stages_cleared': len(dungeon.stages)
        }
    
    def abandon_dungeon(self, user_id: str):
        """던전 포기"""
        if user_id in self.active_dungeons:
            del self.active_dungeons[user_id]