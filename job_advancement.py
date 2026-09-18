from typing import Dict, List
from rpg_system import CharacterFactory, Character, CharacterClass

class JobAdvancement:
    def __init__(self):
        self.job_trees = self._initialize_job_trees()
    
    def _initialize_job_trees(self) -> Dict[str, Dict]:
        """직업 트리 초기화"""
        return {
            '전사': {
                '2차': {
                    '기사': {
                        'level_requirement': 20,
                        'description': '성기사의 길을 걷는 방어형 전사',
                        'stat_bonus': {'defense': 10, 'hp': 30, 'attack': 5},
                        'new_skills': ['성스러운 보호', '방패 막기', '성기사의 맹세']
                    },
                    '전사': {
                        'level_requirement': 20,
                        'description': '전장의 영웅, 공격형 전사',
                        'stat_bonus': {'attack': 15, 'speed': 5, 'defense': 3},
                        'new_skills': ['영웅의 일격', '전장의 함성', '분노의 폭발']
                    }
                },
                '3차': {
                    '기사': {
                        '팔라딘': {
                            'level_requirement': 40,
                            'description': '신성한 수호자, 최고의 방어력',
                            'stat_bonus': {'defense': 20, 'hp': 50, 'attack': 10, 'mp': 20},
                            'new_skills': ['신성한 빛', '천사의 축복', '성스러운 심판']
                        },
                        '용기사': {
                            'level_requirement': 40,
                            'description': '용의 힘을 다루는 전사',
                            'stat_bonus': {'attack': 25, 'defense': 10, 'hp': 30, 'speed': 10},
                            'new_skills': ['용의 숨결', '용의 비늘', '드래곤 슬레이어']
                        }
                    },
                    '전사': {
                        '전설의 영웅': {
                            'level_requirement': 40,
                            'description': '전설 속의 영웅, 전투의 대가',
                            'stat_bonus': {'attack': 30, 'speed': 15, 'defense': 5, 'hp': 20},
                            'new_skills': ['영웅의 전설', '전장의 지배자', '불멸의 일격']
                        },
                        '바바리안': {
                            'level_requirement': 40,
                            'description': '야만적인 전사, 광전사',
                            'stat_bonus': {'attack': 35, 'hp': 40, 'defense': 0, 'speed': 5},
                            'new_skills': ['광폭', '야만의 일격', '불굴의 의지']
                        }
                    }
                }
            },
            '마법사': {
                '2차': {
                    '마법사': {
                        'level_requirement': 20,
                        'description': '순수한 마법의 연구자',
                        'stat_bonus': {'mp': 40, 'attack': 10, 'defense': 2},
                        'new_skills': ['메테오', '텔레포트', '마법 증폭']
                    },
                    '소환사': {
                        'level_requirement': 20,
                        'description': '마법 생물을 소환하는 마법사',
                        'stat_bonus': {'mp': 30, 'attack': 8, 'defense': 5},
                        'new_skills': ['소환: 슬라임', '소환: 고블린', '마법진']
                    }
                },
                '3차': {
                    '마법사': {
                        '대마법사': {
                            'level_requirement': 40,
                            'description': '마법의 대가, 모든 마법을 통달',
                            'stat_bonus': {'mp': 60, 'attack': 20, 'defense': 5, 'speed': 5},
                            'new_skills': ['알테마', '시간 정지', '마법의 극치']
                        },
                        '현자': {
                            'level_requirement': 40,
                            'description': '지혜의 현자, 지원형 마법사',
                            'stat_bonus': {'mp': 50, 'attack': 5, 'defense': 10, 'hp': 20},
                            'new_skills': ['치유의 빛', '현자의 축복', '지혜의 눈']
                        }
                    },
                    '소환사': {
                        '소환마법사': {
                            'level_requirement': 40,
                            'description': '강력한 소환술의 대가',
                            'stat_bonus': {'mp': 45, 'attack': 15, 'defense': 8},
                            'new_skills': ['소환: 드래곤', '소환의 제왕', '마법 진흙']
                        },
                        '네이처마스터': {
                            'level_requirement': 40,
                            'description': '자연의 힘을 다루는 소환사',
                            'stat_bonus': {'mp': 40, 'attack': 12, 'defense': 12, 'hp': 15},
                            'new_skills': ['자연의 보호', '정령의 부름', '생명의 춤']
                        }
                    }
                }
            },
            '궁수': {
                '2차': {
                    '저격수': {
                        'level_requirement': 20,
                        'description': '장거리 저격의 명수',
                        'stat_bonus': {'attack': 12, 'speed': 10, 'defense': 3},
                        'new_skills': ['저격', '관통 사격', '맹추']
                    },
                    '사냥꾼': {
                        'level_requirement': 20,
                        'description': '야생의 사냥꾼',
                        'stat_bonus': {'attack': 10, 'speed': 12, 'defense': 5, 'hp': 10},
                        'new_skills': ['야생의 감각', '포획', '자연의 친구']
                    }
                },
                '3차': {
                    '저격수': {
                        '전설의 저격수': {
                            'level_requirement': 40,
                            'description': '전설적인 저격수',
                            'stat_bonus': {'attack': 20, 'speed': 18, 'defense': 5},
                            'new_skills': ['한 방의 일격', '보이지 않는 사격', '저격의 신']
                        },
                        '궁술大师': {
                            'level_requirement': 40,
                            'description': '궁술의 대가',
                            'stat_bonus': {'attack': 18, 'speed': 20, 'defense': 8},
                            'new_skills': ['다중 사격', '궁술의 극치', '화살의 비']
                        }
                    },
                    '사냥꾼': {
                        '마스터 사냥꾼': {
                            'level_requirement': 40,
                            'description': '모든 짐승의 지배자',
                            'stat_bonus': {'attack': 15, 'speed': 15, 'defense': 10, 'hp': 20},
                            'new_skills': ['야생의 왕', '수렵의 달인', '자연의 수호자']
                        },
                        '레인저': {
                            'level_requirement': 40,
                            'description': '숲의 수호자',
                            'stat_bonus': {'attack': 14, 'speed': 18, 'defense': 12, 'mp': 15},
                            'new_skills': ['숲의 축복', '은신의 대가', '자연의 분노']
                        }
                    }
                }
            },
            '도적': {
                '2차': {
                    '암살자': {
                        'level_requirement': 20,
                        'description': '그림자의 암살자',
                        'stat_bonus': {'attack': 18, 'speed': 15, 'defense': 2},
                        'new_skills': ['암살', '은신', '독']
                    },
                    '도적': {
                        'level_requirement': 20,
                        'description': '도둑의 기술을 다루는 자',
                        'stat_bonus': {'attack': 12, 'speed': 18, 'defense': 5, 'mp': 10},
                        'new_skills': ['도둑질', '금고 열기', '도망술']
                    }
                },
                '3차': {
                    '암살자': {
                        '섀도 마스터': {
                            'level_requirement': 40,
                            'description': '그림자의 지배자',
                            'stat_bonus': {'attack': 25, 'speed': 25, 'defense': 5},
                            'new_skills': ['그림자 걷기', '섀도 블레이드', '암살의 달인']
                        },
                        '나이트 스토커': {
                            'level_requirement': 40,
                            'description': '밤의 사냥꾼',
                            'stat_bonus': {'attack': 22, 'speed': 22, 'defense': 8, 'mp': 15},
                            'new_skills': ['야간 투시', '침묵의 발걸음', '어둠의 칼날']
                        }
                    },
                    '도적': {
                        '마스터 도적': {
                            'level_requirement': 40,
                            'description': '도둑의 왕',
                            'stat_bonus': {'attack': 15, 'speed': 20, 'defense': 10, 'mp': 25},
                            'new_skills': ['만능 열쇠', '도둑의 눈', '보물의 발견']
                        },
                        '닌자': {
                            'level_requirement': 40,
                            'description': '동양의 암살 기술',
                            'stat_bonus': {'attack': 20, 'speed': 25, 'defense': 5, 'mp': 20},
                            'new_skills': ['닌자술', '수리검', '분신술']
                        }
                    }
                }
            }
        }
    
    def get_available_advancements(self, current_class: str, current_level: int, current_job_stage: int) -> List[Dict]:
        """가능한 전직 옵션 반환"""
        if current_class not in self.job_trees:
            return []
        
        job_tree = self.job_trees[current_class]
        available = []
        
        if current_job_stage == 1 and current_level >= 20:
            # 2차 전직 가능
            for job_name, job_info in job_tree['2차'].items():
                if current_level >= job_info['level_requirement']:
                    available.append({
                        'job_name': job_name,
                        'stage': 2,
                        **job_info
                    })
        
        elif current_job_stage == 2 and current_level >= 40:
            # 3차 전직 가능
            base_class = current_class  # 현재는 기본 클래스를 유지한다고 가정
            # 실제로는 현재 2차 직업을 추적해야 함
            for job_name, job_info in job_tree['3차'].get(current_class, {}).items():
                if current_level >= job_info['level_requirement']:
                    available.append({
                        'job_name': job_name,
                        'stage': 3,
                        **job_info
                    })
        
        return available
    
    def advance_job(self, character: Character, new_job: str, stage: int) -> bool:
        """전직 실행"""
        # 실제 구현에서는 캐릭터 데이터 업데이트 필요
        # 여기서는 개념적 구현만 제공
        return True