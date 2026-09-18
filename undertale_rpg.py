import discord
import config
from database import Database
import random
import sys
import io

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
db = Database()
command_prefix = '!'

# 전역 상태
active_battles = {}
undertale_characters = {}  # user_id: UndertaleCharacter
auto_battle_enabled = {}  # user_id: bool

class UndertaleCharacter:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        self.lv = 1
        self.hp = 20
        self.max_hp = 20
        self.love = 0  # LV (사랑의 힘)
        self.exp = 0
        self.gold = 100
        self.atk = 10
        self.defense = 5
        self.weapon = None
        self.armor = None
        self.items = []
    
    def gain_exp(self, amount: int) -> bool:
        self.exp += amount
        exp_needed = self.lv * 20
        
        if self.exp >= exp_needed:
            self.exp -= exp_needed
            return self.level_up()
        return False
    
    def level_up(self) -> bool:
        if self.lv >= 99:
            return False
        
        self.lv += 1
        self.max_hp += 5
        self.hp = self.max_hp
        self.atk += 2
        self.defense += 1
        return True
    
    def heal(self, amount: int):
        self.hp = min(self.hp + amount, self.max_hp)
    
    def take_damage(self, amount: int) -> int:
        actual_damage = max(1, amount - (self.defense // 2))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def is_alive(self) -> bool:
        return self.hp > 0

class Weapon:
    def __init__(self, name: str, attack: int, description: str):
        self.name = name
        self.attack = attack
        self.description = description

class Armor:
    def __init__(self, name: str, defense: int, description: str):
        self.name = name
        self.defense = defense
        self.description = description

class UndertaleEnemy:
    def __init__(self, name: str, lv: int, hp: int, atk: int, defense: int, exp: int, gold: int):
        self.name = name
        self.lv = lv
        self.max_hp = hp
        self.current_hp = hp
        self.atk = atk
        self.defense = defense
        self.exp = exp
        self.gold = gold
    
    def take_damage(self, amount: int) -> int:
        actual_damage = max(1, amount - (self.defense // 2))
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def is_alive(self) -> bool:
        return self.current_hp > 0

class AutoBattle:
    def __init__(self, player: UndertaleCharacter, enemy: UndertaleEnemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0
        self.in_progress = True
        self.logs = []
    
    def add_log(self, message: str):
        self.logs.append(message)
    
    def process_turn(self) -> dict:
        if not self.in_progress:
            return {'error': '전투가 이미 종료되었습니다.'}
        
        results = []
        
        # 플레이어 턴
        player_damage = self.player.atk + random.randint(-2, 2)
        actual_damage = self.enemy.take_damage(player_damage)
        self.add_log(f"⚔️ {self.player.name}이(가) {self.enemy.name}에게 {actual_damage} 데미지를 입혔습니다!")
        results.append({'attacker': self.player.name, 'defender': self.enemy.name, 'damage': actual_damage})
        
        if not self.enemy.is_alive():
            self.in_progress = False
            return {'battle_end': True, 'winner': 'player', 'results': results}
        
        # 적 턴
        enemy_damage = self.enemy.atk + random.randint(-2, 2)
        actual_damage = self.player.take_damage(enemy_damage)
        self.add_log(f"👹 {self.enemy.name}이(가) {self.player.name}에게 {actual_damage} 데미지를 입혔습니다!")
        results.append({'attacker': self.enemy.name, 'defender': self.player.name, 'damage': actual_damage})
        
        if not self.player.is_alive():
            self.in_progress = False
            return {'battle_end': True, 'winner': 'enemy', 'results': results}
        
        self.turn += 1
        return {'battle_end': False, 'results': results, 'turn': self.turn}
    
    def get_status(self):
        return {
            'player_hp': f"{self.player.hp}/{self.player.max_hp}",
            'enemy_hp': f"{self.enemy.current_hp}/{self.enemy.max_hp}",
            'turn': self.turn,
            'in_progress': self.in_progress
        }

# 언더테일 스타일 아이템들
WEAPONS = {
    '목검': Weapon('목검', 5, '기본적인 나무 검'),
    '나이프': Weapon('나이프', 8, '단검'),
    '트뤼텔': Weapon('트뤼텔', 12, '도끼의 검'),
    '고블린': Weapon('고블린', 10, '코블린에서 주워낸 검'),
    '알파인': Weapon('알파인', 15, '강철검'),
    '미스틸': Weapon('미스틸', 20, '강철로 만든 신비한 검'),
    '볼이비': Weapon('볼이비', 30, '공포의 영혼이 담긴 검'),
    '인디고 아이': Weapon('인디고 아이', 40, '타락의 사망'),
    '리얼 힘': Weapon('리얼 힘', 50, '전설의 검'),
    '오리지널 테이포디': Weapon('오리지널 테이포디', 60, '샌즈가 사용하는 특수무기')
}

ARMORS = {
    '밴드': Armor('밴드', 2, '기본적인 장갑'),
    '갑옷': Armor('갑옷', 5, '사슬 갑옷'),
    '플레이트': Armor('플레이트', 8, '경판 갑옷'),
    '고블린 장갑': Armor('고블린 장갑', 7, '고블린 장갑'),
    '미스틸 장갑': Armor('미스틸 장갑', 12, '강철 장갑'),
    '사우자의 갑옷': Armor('사우자의 갑옷', 15, '전사의 갑옷'),
    '니이트의 갑옷': Armor('니이트의 갑옷', 18, '암흑갑'),
    '로열의 갑옷': Armor('로열의 갑옷', 25, '마법으로 강화된 갑옷'),
    '무적의 갑옷': Armor('무적의 갑옷', 30, '악몽을 방어하는 갑옷'),
    '이터네이티': Armor('이터네이티', 40, '무적이 될 수 없는 갑옷')
}

# 언더테일 스타일 적들
UNDERTALE_ENEMIES = [
    {'name': '프로그림', 'base_hp': 20, 'base_atk': 4, 'base_def': 1, 'exp': 10, 'g': 5},
    {'name': '나프스터블라이트', 'base_hp': 30, 'base_atk': 6, 'base_def': 2, 'exp': 15, 'g': 8},
    {'name': '샤이', 'base_hp': 40, 'base_atk': 8, 'base_def': 3, 'exp': 20, 'g': 12},
    {'name': '파피루스', 'base_hp': 50, 'base_atk': 10, 'base_def': 4, 'exp': 25, 'g': 15},
    {'name': '마드뮤', 'base_hp': 60, 'base_atk': 12, 'base_def': 5, 'exp': 30, 'g': 18},
    {'name': '토리엘', 'base_hp': 70, 'base_atk': 14, 'base_def': 6, 'exp': 35, 'g': 20},
    {'name': '파피', 'base_hp': 80, 'base_atk': 16, 'base_def': 7, 'exp': 40, 'g': 25},
    {'name': '그라비', 'base_hp': 90, 'base_atk': 18, 'base_def': 8, 'exp': 45, 'g': 30},
    {'name': '스폰지', 'base_hp': 100, 'base_atk': 20, 'base_def': 9, 'exp': 50, 'g': 35},
    {'name': '메타톤', 'base_hp': 110, 'base_atk': 22, 'base_def': 10, 'exp': 55, 'g': 40},
    {'name': '아스리엘', 'base_hp': 120, 'base_atk': 24, 'base_def': 11, 'exp': 60, 'g': 45},
    {'name': '오메가', 'base_hp': 130, 'base_atk': 26, 'base_def': 12, 'exp': 65, 'g': 50},
    {'name': '샌드', 'base_hp': 140, 'base_atk': 28, 'base_def': 13, 'exp': 70, 'g': 55},
    {'name': '샌즈', 'base_hp': 150, 'base_atk': 30, 'base_def': 14, 'exp': 75, 'g': 60}
]

def create_enemy(player_lv: int) -> UndertaleEnemy:
    enemy_data = random.choice(UNDERTALE_ENEMIES)
    lv_mult = 1 + (player_lv * 0.1)
    
    return UndertaleEnemy(
        name=enemy_data['name'],
        lv=player_lv,
        hp=int(enemy_data['base_hp'] * lv_mult),
        atk=int(enemy_data['base_atk'] * lv_mult),
        defense=int(enemy_data['base_def'] * lv_mult),
        exp=int(enemy_data['exp'] * lv_mult),
        gold=int(enemy_data['g'] * lv_mult)
    )

@client.event
async def on_ready():
    print(f'{client.user}가 연결되었습니다!')
    print(f'서버 수: {len(client.guilds)}')
    await client.change_presence(activity=discord.Game(name="!도움말"))

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if not message.guild:
        return
    
    content = message.content.strip()
    
    if not content.startswith(command_prefix):
        return
    
    parts = content[1:].split()
    if not parts:
        return
    
    command = parts[0].lower()
    args = parts[1:]
    
    try:
        await handle_command(message, command, args)
    except Exception as e:
        print(f"명령어 처리 에러: {e}")
        await message.channel.send(f"❌ 명령어 처리 중 오류가 발생했습니다: {e}")

async def handle_command(message, command, args):
    user_id = str(message.author.id)
    
    # 언더테일 스타일 명령어
    if command == '도움말':
        await show_help(message)
    
    elif command == '캐릭터생성':
        if not args:
            await message.channel.send("❌ 사용법: !캐릭터생성 [이름]")
            return
        await create_character(message, args[0])
    
    elif command == '내정보':
        await show_character_info(message)
    
    elif command == '무기':
        await show_weapons(message)
    
    elif command == '갑옷':
        await show_armors(message)
    
    elif command == '장착':
        if not args:
            await message.channel.send("❌ 사용법: !장착 [무기/갑옷] [이름]")
            return
        await equip_item(message, args[0], args[1] if len(args) > 1 else None)
    
    elif command == '인벤토리':
        await show_inventory(message)
    
    elif command == '자동전투':
        await toggle_auto_battle(message)
    
    elif command == '전투':
        await start_auto_battle(message)
    
    elif command == '휴식':
        await rest_character(message)
    
    elif command == '저장':
        await save_game(message)
    
    elif command == '로드':
        await load_game(message)
    
    elif command == '상점':
        await message.channel.send("❌ 상점 시스템은 제거되었습니다.")
    
    else:
        await message.channel.send(f"❌ 알 수 없는 명령어입니다: {command}")

# 캐릭터 관련 함수
async def create_character(message, name: str):
    user_id = str(message.author.id)
    
    if user_id in undertale_characters:
        await message.channel.send("❌ 이미 캐릭터가 존재합니다.")
        return
    
    character = UndertaleCharacter(user_id, name)
    undertale_characters[user_id] = character
    
    embed = discord.Embed(
        title="❤️ 캐릭터 생성 완료!",
        description=f"{name}이(가) 언더테일에서 모험을 시작합니다!",
        color=discord.Color.blue()
    )
    embed.add_field(name="이름", value=character.name, inline=True)
    embed.add_field(name="LV", value=character.lv, inline=True)
    embed.add_field(name="HP", value=f"{character.hp}/{character.max_hp}", inline=True)
    embed.add_field(name="ATK", value=character.atk, inline=True)
    embed.add_field(name="DEF", value=character.defense, inline=True)
    embed.add_field(name="골드", value=character.gold, inline=True)
    
    await message.channel.send(embed=embed)

async def show_character_info(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다. !캐릭터생성 [이름]으로 캐릭터를 생성하세요.")
        return
    
    char = undertale_characters[user_id]
    exp_needed = char.lv * 20
    
    embed = discord.Embed(
        title=f"❤️ {char.name}의 정보",
        description="언더테일 스타일 캐릭터",
        color=discord.Color.blue()
    )
    embed.add_field(name="LV", value=char.lv, inline=True)
    embed.add_field(name="EXP", value=f"{char.exp}/{exp_needed}", inline=True)
    embed.add_field(name="HP", value=f"{char.hp}/{char.max_hp}", inline=True)
    embed.add_field(name="ATK", value=char.atk, inline=True)
    embed.add_field(name="DEF", value=char.defense, inline=True)
    embed.add_field(name="골드", value=char.gold, inline=True)
    
    if char.weapon:
        embed.add_field(name="무기", value=f"{char.weapon.name} (+{char.weapon.attack} ATK)", inline=True)
    else:
        embed.add_field(name="무기", value="없음", inline=True)
    
    if char.armor:
        embed.add_field(name="갑옷", value=f"{char.armor.name} (+{char.armor.defense} DEF)", inline=True)
    else:
        embed.add_field(name="갑옷", value="없음", inline=True)
    
    await message.channel.send(embed=embed)

# 아이템 관련 함수
async def show_weapons(message):
    embed = discord.Embed(
        title="⚔️ 무기 목록",
        description="무기를 구매하여 공격력을 높이세요!",
        color=discord.Color.orange()
    )
    
    for weapon_name, weapon in WEAPONS.items():
        embed.add_field(
            name=f"{weapon.name} - {weapon.attack * 100}골드",
            value=weapon.description,
            inline=False
        )
    
    embed.add_field(name="구매 방법", value="!장착 무기 [이름]", inline=False)
    await message.channel.send(embed=embed)

async def show_armors(message):
    embed = discord.Embed(
        title="🛡️ 갑옷 목록",
        description="갑옷을 구매하여 방어력을 높이세요!",
        color=discord.Color.blue()
    )
    
    for armor_name, armor in ARMORS.items():
        embed.add_field(
            name=f"{armor.name} - {armor.defense * 100}골드",
            value=armor.description,
            inline=False
        )
    
    embed.add_field(name="구매 방법", value="!장착 갑옷 [이름]", inline=False)
    await message.channel.send(embed=embed)

async def equip_item(message, item_type: str, item_name: str):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    char = undertale_characters[user_id]
    
    if item_type == '무기':
        if item_name not in WEAPONS:
            await message.channel.send("❌ 존재하지 않는 무기입니다.")
            return
        
        weapon = WEAPONS[item_name]
        cost = weapon.attack * 100
        
        if char.gold < cost:
            await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
            return
        
        char.gold -= cost
        
        # 기존 무기 해제
        if char.weapon:
            char.atk -= char.weapon.attack
        
        char.weapon = weapon
        char.atk += weapon.attack
        
        await message.channel.send(f"✅ {weapon.name}을(를) 장착했습니다! ATK +{weapon.attack}")
    
    elif item_type == '갑옷':
        if item_name not in ARMORS:
            await message.channel.send("❌ 존재하지 않는 갑옷입니다.")
            return
        
        armor = ARMORS[item_name]
        cost = armor.defense * 100
        
        if char.gold < cost:
            await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
            return
        
        char.gold -= cost
        
        # 기존 갑옷 해제
        if char.armor:
            char.defense -= char.armor.defense
        
        char.armor = armor
        char.defense += armor.defense
        
        await message.channel.send(f"✅ {armor.name}을(를) 장착했습니다! DEF +{armor.defense}")
    
    else:
        await message.channel.send("❌ 올바른 아이템 타입이 아닙니다. (무기/갑옷)")

async def show_inventory(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    char = undertale_characters[user_id]
    
    embed = discord.Embed(
        title="🎒 인벤토리",
        description=f"{char.name}의 소지품",
        color=discord.Color.purple()
    )
    
    if char.weapon:
        embed.add_field(name="무기", value=f"{char.weapon.name} (+{char.weapon.attack} ATK)", inline=True)
    else:
        embed.add_field(name="무기", value="없음", inline=True)
    
    if char.armor:
        embed.add_field(name="갑옷", value=f"{char.armor.name} (+{char.armor.defense} DEF)", inline=True)
    else:
        embed.add_field(name="갑옷", value="없음", inline=True)
    
    if char.items:
        items_text = "\n".join(char.items)
        embed.add_field(name="아이템", value=items_text, inline=False)
    else:
        embed.add_field(name="아이템", value="소지품이 없습니다.", inline=False)
    
    await message.channel.send(embed=embed)

# 전투 관련 함수
async def toggle_auto_battle(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 캐릭터생성 [이름]으로 캐릭터를 생성하세요.")
        return
    
    if user_id not in auto_battle_enabled:
        auto_battle_enabled[user_id] = False
    
    auto_battle_enabled[user_id] = not auto_battle_enabled[user_id]
    
    if auto_battle_enabled[user_id]:
        await message.channel.send("✅ 자동 전투가 활성화되었습니다! 전투를 시작하려면 !전투를 입력하세요.")
    else:
        await message.channel.send("❌ 자동 전투가 비활성화되었습니다.")

async def start_auto_battle(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 캐릭터생성 [이름]으로 캐릭터를 생성하세요.")
        return
    
    if not auto_battle_enabled.get(user_id, False):
        await message.channel.send("❌ 자동 전투가 활성화되지 않았습니다. !자동전투로 활성화하세요.")
        return
    
    if user_id in active_battles:
        await message.channel.send("❌ 이미 진행 중인 전투가 있습니다.")
        return
    
    char = undertale_characters[user_id]
    
    if not char.is_alive():
        await message.channel.send("❌ 캐릭터가 사망했습니다. !휴식으로 회복하세요.")
        return
    
    enemy = create_enemy(char.lv)
    battle = AutoBattle(char, enemy)
    active_battles[user_id] = battle
    
    embed = discord.Embed(
        title="⚔️ 자동 전투 시작!",
        description=f"{enemy.name}(이)가 나타났습니다!",
        color=discord.Color.red()
    )
    embed.add_field(name="상대", value=f"{char.name} vs {enemy.name}", inline=True)
    embed.add_field(name="전투 방식", value="자동 전투", inline=True)
    
    await message.channel.send(embed=embed)
    
    # 자동 전투 루프
    while battle.in_progress:
        result = battle.process_turn()
        
        if result.get('battle_end'):
            del active_battles[user_id]
            
            if result['winner'] == 'player':
                char = battle.player
                exp_gained = battle.enemy.exp
                gold_gained = battle.enemy.gold
                
                leveled_up = char.gain_exp(exp_gained)
                char.gold += gold_gained
                char.heal(char.max_hp // 2)
                
                embed = discord.Embed(
                    title="🎉 전투 승리!",
                    description=f"{battle.enemy.name}을(를) 물리쳤습니다!",
                    color=discord.Color.green()
                )
                embed.add_field(name="획득 EXP", value=exp_gained, inline=True)
                embed.add_field(name="획득 골드", value=gold_gained, inline=True)
                
                if leveled_up:
                    embed.add_field(name="🎊 레벨업!", value=f"현재 레벨: {char.lv}", inline=False)
                
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("💀 전투 패배... 캐릭터가 사망했습니다.")
            
            break
        
        # 다음 턴 전 딜레이
        import asyncio
        await asyncio.sleep(2)
        
        # 상태 표시
        status = battle.get_status()
        embed = discord.Embed(
            title=f"⚔️ 전투 진행 중 (턴 {status['turn']})",
            color=discord.Color.orange()
        )
        embed.add_field(name="내 HP", value=status['player_hp'], inline=True)
        embed.add_field(name="적 HP", value=status['enemy_hp'], inline=True)
        
        await message.channel.send(embed=embed)

async def rest_character(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 캐릭터생성 [이름]으로 캐릭터를 생성하세요.")
        return
    
    char = undertale_characters[user_id]
    
    if char.is_alive():
        await message.channel.send("❌ 캐릭터가 이미 살아있습니다.")
        return
    
    cost = char.lv * 10
    if char.gold < cost:
        await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
        return
    
    char.gold -= cost
    char.hp = char.max_hp
    
    await message.channel.send(f"✅ {cost}골드를 지불하고 회복했습니다!")

async def save_game(message):
    user_id = str(message.author.id)
    
    if user_id not in undertale_characters:
        await message.channel.send("❌ 캐릭터가 캐릭터생성 [이름]으로 캐릭터를 생성하세요.")
        return
    
    char = undertale_characters[user_id]
    
    save_data = {
        'name': char.name,
        'lv': char.lv,
        'hp': char.hp,
        'max_hp': char.max_hp,
        'atk': char.atk,
        'defense': char.defense,
        'exp': char.exp,
        'gold': char.gold,
        'weapon': char.weapon.name if char.weapon else None,
        'armor': char.armor.name if char.armor else None,
        'items': char.items
    }
    
    db.data['undertale_characters'] = db.data.get('undertale_characters', {})
    db.data['undertale_characters'][user_id] = save_data
    db.save()
    
    await message.channel.send("✅ 게임이 저장되었습니다!")

async def load_game(message):
    user_id = str(message.author.id)
    
    if 'undertale_characters' not in db.data or user_id not in db.data['undertale_characters']:
        await message.channel.send("❌ 저장된 게임이 없습니다.")
        return
    
    save_data = db.data['undertale_characters'][user_id]
    
    char = UndertaleCharacter(user_id, save_data['name'])
    char.lv = save_data['lv']
    char.hp = save_data['hp']
    char.max_hp = save_data['max_hp']
    char.atk = save_data['atk']
    char.defense = save_data['defense']
    char.exp = save_data['exp']
    char.gold = save_data['gold']
    char.items = save_data['items']
    
    if save_data['weapon']:
        char.weapon = WEAPONS.get(save_data['weapon'])
        if char.weapon:
            char.atk += char.weapon.attack
    
    if save_data['armor']:
        char.armor = ARMORS.get(save_data['armor'])
        if char.armor:
            char.defense += char.armor.defense
    
    undertale_characters[user_id] = char
    
    embed = discord.Embed(
        title="🎮 게임 로드 완료!",
        description=f"{char.name}님의 데이터를 불러왔습니다.",
        color=discord.Color.green()
    )
    embed.add_field(name="LV", value=char.lv, inline=True)
    embed.add_field(name="HP", value=f"{char.hp}/{char.max_hp}", inline=True)
    embed.add_field(name="골드", value=char.gold, inline=True)
    
    await message.channel.send(embed=embed)

async def show_help(message):
    embed = discord.Embed(
        title="❤️ 언더테일 스타일 RPG 봇 도움말",
        description="샌즈가 주인공인 RPG 봇!",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="캐릭터", value="!캐릭터생성 [이름] - 캐릭터 생성\n!내정보 - 내 캐릭터 정보", inline=False)
    embed.add_field(name="장비", value="!무기 - 무기 목록\n!갑옷 - 갑옷 목록\n!장착 [무기/갑옷] [이름] - 장착", inline=False)
    embed.add_field(name="전투", value="!자동전투 - 자동 전투 토글\n!전투 - 전투 시작\n!휴식 - 회복 (골드 필요)", inline=False)
    embed.add_field(name="시스템", value="!저장 - 게임 저장\n!로드 - 게임 로드\n!인벤토리 - 인벤토리 확인", inline=False)
    
    await message.channel.send(embed=embed)

if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        print("DISCORD_TOKEN 환경 변수를 설정해주세요!")
    else:
        client.run(config.DISCORD_TOKEN)