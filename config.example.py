import os

# 디스코드 봇 토큰 (여기에 당신의 봇 토큰을 입력하세요)
# Discord Developer Portal에서 봇 토큰을 받을 수 있습니다.
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# 게임 설정
MAX_LEVEL = 100  # 최대 레벨
BASE_EXP_REQUIREMENT = 100  # 1레벨 경험치 요구량
EXP_GROWTH_RATE = 1.5  # 레벨당 경험치 증가율

# 전투 설정
TURN_TIME_LIMIT = 30  # 각 턴의 시간 제한 (초) - 현재 미사용

# 경제 설정
STARTING_GOLD = 100  # 시작 골드
HEAL_COST_MULTIPLIER = 10  # 레벨당 회복 비용倍率

# 인벤토리 설정
DEFAULT_INVENTORY_SLOTS = 20  # 기본 인벤토리 슬롯 수
