import discord
import config
from database import Database
from rpg_system import CharacterFactory, Character
from battle_system import Battle, EnemyFactory
from item_system import ItemFactory, Inventory, ItemType
from compendium_system import Compendium
from gacha_system import GachaSystem
from job_advancement import JobAdvancement
from currency_system import CurrencySystem
from spell_system import SpellSystem
from hp_battle_system import HogwartsBattle
from shop_items import SHOP_ITEMS, CATEGORIES, CURRENCY_ICONS
import sys
import io
import random

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# 디스코드 클라이언트 생성 (Bot 대신 Client 사용)
client = discord.Client(intents=intents)

# 데이터베이스 및 전역 상태
db = Database()
active_battles = {}
active_hp_battles = {}  # Harry Potter 스타일 전투
command_prefix = '!'
compendium = Compendium()
gacha_system = GachaSystem()
job_advancement = JobAdvancement()
currency_system = CurrencySystem()
spell_system = SpellSystem()
user_pull_counts = {}  # user_id: pull_count
player_job_stages = {}  # user_id: job_stage (1=기본, 2=2차, 3=3차)
player_current_jobs = {}  # user_id: current_job_name
shop_page_states = {}  # user_id: current_page, category
shop_confirm_states = {}  # user_id: item_name (구매 확인 상태)

@client.event
async def on_ready():
    print(f'{client.user}가 연결되었습니다!')
    print(f'서버 수: {len(client.guilds)}')
    
    # 활동 상태 설정
    await client.change_presence(activity=discord.Game(name="!도움말"))
    
    print('봇 상태: 온라인')

@client.event
async def on_message(message):
    # 봇 자신의 메시지 무시
    if message.author.bot:
        return
    
    # DM 메시지 무시
    if not message.guild:
        return
    
    content = message.content.strip()
    user_id = str(message.author.id)
    
    # 전투 중인 경우 접두사 없는 명령어 처리
    if user_id in active_battles:
        await handle_battle_command(message, content)
        return
    
    # 명령어 접두사 확인
    if not content.startswith(command_prefix):
        return
    
    # 명령어 파싱
    parts = content[1:].split()
    if not parts:
        return
    
    command = parts[0].lower()
    args = parts[1:]
    
    # 명령어 처리
    try:
        await handle_command(message, command, args)
    except Exception as e:
        print(f"명령어 처리 에러: {e}")
        await message.channel.send(f"❌ 명령어 처리 중 오류가 발생했습니다: {e}")

async def handle_battle_command(message, content):
    """전투 중 접두사 없는 명령어 처리"""
    user_id = str(message.author.id)
    battle = active_battles.get(user_id)
    
    if not battle:
        return
    
    # 전투 중 가능한 액션
    battle_actions = {
        '공격': 'attack',
        '방어': 'defend', 
        '도망': 'flee'
    }
    
    skill_list = ['파이어볼', '아이스 스파이크', '라이트닝 볼트', '파워 스트라이크', '관통 사격', '연사', '맹독 화살', '암습', '백스탭', '은신']
    
    # 기본 액션 처리
    if content in battle_actions:
        action = battle_actions[content]
        if action == 'flee':
            import random
            if random.random() < 0.5:
                del active_battles[user_id]
                await message.channel.send("🏃 도망에 성공했습니다!")
                return
            else:
                await message.channel.send("❌ 도망에 실패했습니다! 적의 공격!")
                action = 'attack'  # 실패 시 공격으로 처리
        
        result = battle.process_turn(action)
        await handle_battle_result(message, result, user_id)
    
    # 스킬 처리
    elif content in skill_list:
        result = battle.process_turn('skill', content)
        await handle_battle_result(message, result, user_id)
    
    else:
        await message.channel.send(f"❌ 알 수 없는 명령어입니다. '공격', '방어', '도망' 또는 스킬 이름을 입력하세요.")

async def handle_command(message, command, args):
    """명령어 처리 함수"""
    user_id = str(message.author.id)
    
    # 도움말
    if command == '도움말':
        await show_help(message)
    
    # 캐릭터 생성
    elif command == '캐릭터생성':
        if len(args) < 2:
            await message.channel.send("❌ 사용법: !캐릭터생성 [이름] [클래스]")
            return
        await create_character(message, args[0], args[1])
    
    # 내정보
    elif command == '내정보':
        await show_character_info(message)
    
    # 전투 관련
    elif command == '전투시작':
        await start_battle(message)
    elif command == 'hp전투':
        await start_hp_battle(message)
    elif command == '공격':
        # HP 전투 중인지 확인
        user_id = str(message.author.id)
        if user_id in active_hp_battles:
            await perform_hp_battle_action(message, 'attack')
        else:
            await attack(message)
    elif command == '스킬':
        if not args:
            await message.channel.send("❌ 사용법: !스킬 [스킬명]")
            return
        user_id = str(message.author.id)
        if user_id in active_hp_battles:
            await perform_hp_battle_action(message, 'spell', ' '.join(args))
        else:
            await use_skill(message, ' '.join(args))
    elif command == '방어':
        user_id = str(message.author.id)
        if user_id in active_hp_battles:
            await perform_hp_battle_action(message, 'defend')
        else:
            await defend(message)
    elif command == '도망':
        user_id = str(message.author.id)
        if user_id in active_hp_battles:
            await message.channel.send("❌ 마법 대결에서는 도망할 수 없습니다!")
        else:
            await flee(message)
    elif command == '무장해제':
        user_id = str(message.author.id)
        if user_id in active_hp_battles:
            await perform_hp_battle_action(message, 'disarm')
        else:
            await message.channel.send("❌ 마법 대전 중에만 사용할 수 있습니다.")
    
    # 마법 관련
    elif command == '마법배우기':
        if not args:
            await show_spell_learning(message)
        else:
            # 마법 배우기
            user_id = str(message.author.id)
            player_data = db.get_player(user_id)
            
            if not player_data:
                await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
                return
            
            character = CharacterFactory.from_dict(player_data)
            spell_name = ' '.join(args)
            spell = spell_system.get_spell(spell_name)
            
            if not spell:
                await message.channel.send("❌ 존재하지 않는 마법입니다.")
                return
            
            cost = spell.mana_cost * 100
            if character.gold < cost:
                await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
                return
            
            character.gold -= cost
            db.update_player(user_id, character.to_dict())
            
            if spell_system.learn_spell(user_id, spell_name):
                await message.channel.send(f"✅ {spell_name} 마법을 배웠습니다! {cost}골드를 지불했습니다.")
            else:
                await message.channel.send("❌ 이미 배운 마법이거나 존재하지 않는 마법입니다.")
    elif command == '마법목록':
        await show_spell_list(message)
    elif command == '마법':
        if not args:
            await message.channel.send("❌ 사용법: !마법 [주문명]")
            return
        await cast_spell(message, ' '.join(args))
    
    # 회복
    elif command == '회복':
        await heal_character(message)
    
    # 아이템 관련
    elif command == '인벤토리':
        await show_inventory(message)
    elif command == '상점':
        if args:
            await show_shop_category(message, args[0])
        else:
            await show_shop_main(message)
    elif command == '상점이전':
        await shop_previous_page(message)
    elif command == '상점다음':
        await shop_next_page(message)
    elif command == '상점페이지':
        if not args:
            await message.channel.send("❌ 사용법: !상점페이지 [페이지번호]")
            return
        try:
            page_num = int(args[0])
            await show_shop_page(message, page_num)
        except ValueError:
            await message.channel.send("❌ 페이지 번호는 숫자여야 합니다.")
    elif command == '구매':
        if not args:
            await message.channel.send("❌ 사용법: !구매 [아이템이름]")
            return
        await buy_item(message, ' '.join(args))
    elif command == '사용':
        if not args:
            await message.channel.send("❌ 사용법: !사용 [아이템ID]")
            return
        await use_item(message, args[0])
    elif command == '장착':
        if not args:
            await message.channel.send("❌ 사용법: !장착 [아이템ID]")
            return
        await equip_item(message, args[0])
    
    # 도감 관련
    elif command == '도감':
        await show_compendium(message)
    elif command == '도감보상':
        await show_compendium_rewards(message)
    
    # 뽑기 관련
    elif command == '뽑기':
        pull_count = 1
        if args and args[0].isdigit():
            pull_count = int(args[0])
            if pull_count not in [1, 10]:
                await message.channel.send("❌ 뽑기 횟수는 1 또는 10만 가능합니다.")
                return
        await pull_gacha(message, pull_count)
    elif command == '뽑기정보':
        await show_gacha_info(message)
    
    # 던전 시스템 제거됨
    elif command == '던전목록':
        await message.channel.send("❌ 던전 시스템은 제거되었습니다.")
    elif command == '던전입장':
        await message.channel.send("❌ 던전 시스템은 제거되었습니다.")
    elif command == '던전진행':
        await message.channel.send("❌ 던전 시스템은 제거되었습니다.")
    elif command == '던전포기':
        await message.channel.send("❌ 던전 시스템은 제거되었습니다.")
    
    # 전직 관련
    elif command == '전직정보':
        await show_job_advancement_info(message)
    elif command == '전직':
        if not args:
            await message.channel.send("❌ 사용법: !전직 [직업이름]")
            return
        await perform_job_advancement(message, ' '.join(args))
    
    else:
        await message.channel.send(f"❌ 알 수 없는 명령어입니다: {command}")

# 캐릭터 관련 함수
async def create_character(message, name, class_name):
    user_id = str(message.author.id)
    
    if db.get_player(user_id):
        await message.channel.send("❌ 이미 캐릭터가 존재합니다!")
        return
    
    # 샌즈 주인공 설정 - 이름은 입력받지만 클래스는 고정
    character = CharacterFactory.create_character(user_id, name, '도적')  # 샌즈 스타일 도적 클래스
    character.name = name  # 샌즈 스타일 이름
    db.create_player(user_id, character.to_dict())
    
    inventory = Inventory()
    db.create_inventory(user_id, inventory.to_dict())
    
    embed = discord.Embed(
        title="❤️ 샌즈 캐릭터 생성 완료!",
        description=f"{name}이(가) 언더테일의 세계에 모험을 시작합니다!",
        color=discord.Color.blue()
    )
    embed.add_field(name="이름", value=character.name, inline=True)
    embed.add_field(name="클래스", value="샌즈 스타일", inline=True)
    embed.add_field(name="레벨", value=character.level, inline=True)
    embed.add_field(name="HP", value=f"{character.current_hp}/{character.max_hp}", inline=True)
    embed.add_field(name="MP", value=f"{character.current_mp}/{character.max_mp}", inline=True)
    embed.add_field(name="골드", value=character.gold, inline=True)
    embed.add_field(name="특수 능력", value="헤이와! 순간이동 및 뼈 미사일", inline=False)
    
    await message.channel.send(embed=embed)

async def show_character_info(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    exp_needed = character._get_exp_needed()
    
    embed = discord.Embed(
        title=f"👤 {character.name}의 정보",
        description=f"{character.character_class.description}",
        color=discord.Color.blue()
    )
    embed.add_field(name="클래스", value=character.character_class.name, inline=True)
    embed.add_field(name="레벨", value=character.level, inline=True)
    embed.add_field(name="경험치", value=f"{character.exp}/{exp_needed}", inline=True)
    embed.add_field(name="HP", value=f"{character.current_hp}/{character.max_hp}", inline=True)
    embed.add_field(name="MP", value=f"{character.current_mp}/{character.max_mp}", inline=True)
    embed.add_field(name="골드", value=character.gold, inline=True)
    
    await message.channel.send(embed=embed)

# 전투 관련 함수
async def start_battle(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    if user_id in active_battles:
        await message.channel.send("❌ 이미 진행 중인 전투가 있습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    
    if not character.is_alive():
        await message.channel.send("❌ 캐릭터가 사망했습니다. !회복으로 회복하세요.")
        return
    
    # 캐릭터 상태 초기화 확인
    if character.current_hp <= 0:
        character.current_hp = character.max_hp
        character.current_mp = character.max_mp
        db.update_player(user_id, character.to_dict())
    
    # 무작위 적 생성
    enemy = EnemyFactory.create_enemy(character.level)
    battle = Battle(character, enemy)
    active_battles[user_id] = battle
    
    # 정통 RPG 형식 전투 표시
    await show_rpg_battle_display(message, battle)

async def show_rpg_battle_display(message, battle):
    """정통 RPG 형식 전투 표시"""
    status = battle.get_battle_status()
    
    embed = discord.Embed(
        title="⚔️ 전투",
        color=discord.Color.red()
    )
    
    # 플레이어 정보
    player_hp_percent = status['player_hp_percent']
    player_hp_bar = "█" * (player_hp_percent // 10) + "░" * (10 - (player_hp_percent // 10))
    
    embed.add_field(
        name=f"{status['player_name']}",
        value=f"MP (마나): {status['player_mp']}\n"
              f"HP (체력): {status['player_hp']} ({player_hp_percent}%)\n"
              f"ATK (공격력): {status['player_atk']}\n"
              f"DEF (방어력): {status['player_def']}",
        inline=True
    )
    
    # 적 정보
    enemy_hp_percent = status['enemy_hp_percent']
    enemy_hp_bar = "█" * (enemy_hp_percent // 10) + "░" * (10 - (enemy_hp_percent // 10))
    
    embed.add_field(
        name=f"{status['enemy_name']}",
        value=f"MP (마나): ∞\n"
              f"HP (체력): {status['enemy_hp']} ({enemy_hp_percent}%)\n"
              f"ATK (공격력): {status['enemy_atk']}\n"
              f"DEF (방어력): {status['enemy_def']}",
        inline=True
    )
    
    # 전투 현황
    log_text = ""
    for log in status['log']:
        log_text += f"{log}\n"
    
    if not log_text:
        log_text = "전투가 시작되었습니다!"
    
    embed.add_field(
        name="전투 현황",
        value=log_text,
        inline=False
    )
    
    await message.channel.send(embed=embed)
    
    # 행동 안내
    embed = discord.Embed(
        title="🎯 행동 선택",
        description="스킬 이름이나 '공격', '방어', '도망'을 입력하세요 (접두사 없이)",
        color=discord.Color.gold()
    )
    embed.add_field(name="사용 가능한 스킬", value="파이어볼, 아이스 스파이크, 라이트닝 볼트, 파워 스트라이크 등", inline=False)
    embed.add_field(name="기본 행동", value="공격, 방어, 도망", inline=False)
    
    await message.channel.send(embed=embed)

async def show_battle_actions(message):
    embed = discord.Embed(
        title="🎯 행동 선택",
        description="전투 중 행동을 선택하세요:",
        color=discord.Color.gold()
    )
    embed.add_field(name="!공격", value="기본 공격", inline=True)
    embed.add_field(name="!스킬 [스킬명]", value="스킬 사용", inline=True)
    embed.add_field(name="!방어", value="방어 태세", inline=True)
    embed.add_field(name="!도망", value="전투 도망", inline=True)
    
    await message.channel.send(embed=embed)

async def attack(message):
    user_id = str(message.author.id)
    battle = active_battles.get(user_id)
    
    if not battle:
        await message.channel.send("❌ 진행 중인 전투가 없습니다.")
        return
    
    if not battle.in_progress:
        await message.channel.send("❌ 전투가 이미 종료되었습니다.")
        del active_battles[user_id]
        return
    
    result = battle.process_turn('attack')
    await handle_battle_result(message, result, user_id)

async def use_skill(message, skill_name):
    user_id = str(message.author.id)
    battle = active_battles.get(user_id)
    
    if not battle:
        await message.channel.send("❌ 진행 중인 전투가 없습니다.")
        return
    
    if not battle.in_progress:
        await message.channel.send("❌ 전투가 이미 종료되었습니다.")
        del active_battles[user_id]
        return
    
    result = battle.process_turn('skill', skill_name)
    await handle_battle_result(message, result, user_id)

async def defend(message):
    user_id = str(message.author.id)
    battle = active_battles.get(user_id)
    
    if not battle:
        await message.channel.send("❌ 진행 중인 전투가 없습니다.")
        return
    
    if not battle.in_progress:
        await message.channel.send("❌ 전투가 이미 종료되었습니다.")
        del active_battles[user_id]
        return
    
    result = battle.process_turn('defend')
    await handle_battle_result(message, result, user_id)

async def flee(message):
    user_id = str(message.author.id)
    battle = active_battles.get(user_id)
    
    if not battle:
        await message.channel.send("❌ 진행 중인 전투가 없습니다.")
        return
    
    if not battle.in_progress:
        await message.channel.send("❌ 전투가 이미 종료되었습니다.")
        del active_battles[user_id]
        return
    
    import random
    if random.random() < 0.5:
        del active_battles[user_id]
        await message.channel.send("🏃 도망에 성공했습니다!")
    else:
        await message.channel.send("❌ 도망에 실패했습니다! 적의 공격!")
        result = battle.process_turn('attack')
        await handle_battle_result(message, result, user_id)

async def handle_battle_result(message, result, user_id):
    if 'error' in result:
        await message.channel.send(f"❌ {result['error']}")
        return
    
    battle = active_battles.get(user_id)
    if not battle:
        return
    
    # 전투 로그 생성
    battle_logs = []
    for log in result.get('results', []):
        if isinstance(log, dict):
            if log.get('action') == 'defend':
                battle_logs.append(f"{log['actor']}이(가) 방어 태세를 취합니다!")
            else:
                damage = log.get('damage', 0)
                defender = log.get('defender', '')
                attacker = log.get('attacker', '')
                skill = log.get('skill', '')
                
                if skill:
                    battle_logs.append(f"{attacker}의 {skill}!")
                    battle_logs.append(f"약점을 찌른다!!!")
                    battle_logs.append(f"{defender}의 체력 - {damage}")
                else:
                    battle_logs.append(f"{attacker}의 공격!")
                    battle_logs.append(f"{defender}의 체력 - {damage}")
    
    # 전투 현황 업데이트
    for log in battle_logs:
        battle.add_log(log)
    
    # 업데이트된 전투 화면 표시
    await show_rpg_battle_display(message, battle)
    
    if result.get('battle_end'):
        del active_battles[user_id]
        
        if result['winner'] == 'player':
            character = battle.player
            exp_gained = battle.enemy.exp_reward
            gold_gained = battle.enemy.gold_reward
            
            leveled_up = character.gain_exp(exp_gained)
            character.gold += gold_gained
            character.heal(character.max_hp // 2)
            character.restore_mp(character.max_mp // 2)
            
            db.update_player(user_id, character.to_dict())
            
            # 도감에 몬스터 추가
            is_new_monster = compendium.add_monster(user_id, battle.enemy.name)
            
            # 아이템 드롭 시스템
            inventory_data = db.get_inventory(user_id)
            inventory = Inventory()
            if inventory_data:
                inventory.items = inventory_data['items']
                inventory.equipped = inventory_data['equipped']
            
            dropped_items = []
            drop_chance = random.random()
            
            # 30% 확률로 아이템 드롭
            if drop_chance < 0.3:
                all_items = ItemFactory.get_shop_items()
                if all_items:
                    dropped_item = random.choice(all_items)
                    if inventory.add_item(dropped_item):
                        dropped_items.append(dropped_item.name)
                        compendium.add_item(user_id, dropped_item.name)
                        db.update_inventory(user_id, inventory.to_dict())
            
            # 최종 전투 결과 표시
            embed = discord.Embed(
                title="⚔️ 전투 승리!",
                color=discord.Color.green()
            )
            
            final_logs = battle_logs.copy()
            final_logs.append(f"{battle.enemy.name}(은)는 쓰러졌다!")
            
            embed.add_field(name="전투 현황", value="\n".join(final_logs), inline=False)
            embed.add_field(name="획득 경험치", value=exp_gained, inline=True)
            embed.add_field(name="획득 골드", value=gold_gained, inline=True)
            
            if leveled_up:
                embed.add_field(name="🎊 레벨업!", value=f"현재 레벨: {character.level}", inline=False)
            
            if is_new_monster:
                embed.add_field(name="📚 새로운 몬스터 발견!", value=f"{battle.enemy.name}이(가) 도감에 추가되었습니다!", inline=False)
            
            if dropped_items:
                embed.add_field(name="🎁 아이템 획득!", value=", ".join(dropped_items), inline=False)
            
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("💀 전투 패배... 캐릭터가 사망했습니다.")
    else:
        battle = active_battles[user_id]
        status = battle.get_battle_status()
        
        embed = discord.Embed(
            title=f"⚔️ 전투 진행 중 (턴 {status['turn']})",
            color=discord.Color.orange()
        )
        embed.add_field(name="내 HP", value=status['player_hp'], inline=True)
        embed.add_field(name="내 MP", value=status['player_mp'], inline=True)
        embed.add_field(name="적 HP", value=status['enemy_hp'], inline=True)
        
        await message.channel.send(embed=embed)
        await show_battle_actions(message)

async def heal_character(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    
    if character.is_alive():
        await message.channel.send("❌ 캐릭터가 이미 살아있습니다.")
        return
    
    cost = character.level * 10
    if character.gold < cost:
        await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
        return
    
    character.gold -= cost
    character.current_hp = character.max_hp
    character.current_mp = character.max_mp
    
    db.update_player(user_id, character.to_dict())
    
    await message.channel.send(f"✅ {cost}골드를 지불하고 회복했습니다!")

# 아이템 관련 함수
async def show_inventory(message):
    user_id = str(message.author.id)
    inventory_data = db.get_inventory(user_id)
    
    if not inventory_data:
        await message.channel.send("❌ 인벤토리가 존재하지 않습니다.")
        return
    
    inventory = Inventory()
    inventory.items = inventory_data['items']
    inventory.equipped = inventory_data['equipped']
    
    embed = discord.Embed(
        title="🎒 인벤토리",
        description=f"슬롯: {len(inventory.items)}/{inventory.max_slots}",
        color=discord.Color.purple()
    )
    
    equipped_text = ""
    for slot, item in inventory.equipped.items():
        if item:
            equipped_text += f"{slot}: {item['name']}\n"
        else:
            equipped_text += f"{slot}: 없음\n"
    
    embed.add_field(name="장비", value=equipped_text or "장착한 장비가 없습니다.", inline=False)
    
    if inventory.items:
        items_text = ""
        for item_id, quantity in inventory.items.items():
            item = ItemFactory.create_item(item_id)
            items_text += f"{item.name} x{quantity}\n"
        embed.add_field(name="아이템", value=items_text, inline=False)
    else:
        embed.add_field(name="아이템", value="인벤토리가 비어있습니다.", inline=False)
    
    await message.channel.send(embed=embed)

async def show_help(message):
    embed = discord.Embed(
        title="📖 정통 RPG 봇 도움말",
        description="디스코드에서 RPG를 즐겨보세요!",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="캐릭터 관리", value="!캐릭터생성 [이름] [클래스] - 캐릭터 생성\n!내정보 - 내 캐릭터 정보", inline=False)
    embed.add_field(name="전투", value="!전투시작 - 전투 시작\n전투 중 스킬 이름 입력 (파이어볼, 아이스 스파이크 등)\n전투 중 '공격', '방어', '도망' 입력\n!회복 - 캐릭터 회복", inline=False)
    embed.add_field(name="아이템", value="!인벤토리 - 인벤토리 확인\n!상점 - 상점 메인\n!구매 [아이템이름] - 아이템 구매", inline=False)
    embed.add_field(name="도감", value="!도감 - 내 도감 확인\n!도감보상 - 도감 완성 보상 확인", inline=False)
    embed.add_field(name="뽑기", value="!뽑기 [1/10] - 아이템 뽑기\n!뽑기정보 - 뽑기 확률 및 피티 정보", inline=False)
    embed.add_field(name="전직", value="!전직정보 - 가능한 전직 확인\n!전직 [직업명] - 전직 실행", inline=False)
    embed.add_field(name="특징", value="• 정통 RPG 형식 전투\n• 전투 중 접두사 없는 명령어\n• 던전 시스템 제거\n• 한국어 상점 시스템", inline=False)
    
    await message.channel.send(embed=embed)

# 도감 관련 함수
async def show_compendium(message):
    user_id = str(message.author.id)
    user_compendium = compendium.get_compendium(user_id)
    completion = compendium.get_completion_rate(user_id)
    
    embed = discord.Embed(
        title="📚 몬스터 도감",
        description=f"총 완성률: {completion['total']:.1f}%",
        color=discord.Color.purple()
    )
    
    # 몬스터 도감
    monsters_text = ""
    if user_compendium['monsters']:
        monsters_text = ", ".join(sorted(user_compendium['monsters']))
    else:
        monsters_text = "수집한 몬스터가 없습니다."
    
    embed.add_field(name=f"🐉 몬스터 ({len(user_compendium['monsters'])}/20)", value=monsters_text, inline=False)
    
    # 아이템 도감
    items_text = ""
    if user_compendium['items']:
        items_text = ", ".join(sorted(user_compendium['items']))
    else:
        items_text = "수집한 아이템이 없습니다."
    
    embed.add_field(name=f"📦 아이템 ({len(user_compendium['items'])}/50)", value=items_text, inline=False)
    
    # 보스 도감
    bosses_text = ""
    if user_compendium['bosses']:
        bosses_text = ", ".join(sorted(user_compendium['bosses']))
    else:
        bosses_text = "처치한 보스가 없습니다."
    
    embed.add_field(name=f"👹 보스 ({len(user_compendium['bosses'])}/10)", value=bosses_text, inline=False)
    
    # 완성률
    embed.add_field(name="완성률", value=f"몬스터: {completion['monsters']:.1f}% | 아이템: {completion['items']:.1f}% | 보스: {completion['bosses']:.1f}%", inline=False)
    
    await message.channel.send(embed=embed)

async def show_compendium_rewards(message):
    user_id = str(message.author.id)
    rewards = compendium.get_unlocked_rewards(user_id)
    
    if rewards:
        embed = discord.Embed(
            title="🎁 도감 완성 보상",
            description="해금된 보상 목록:",
            color=discord.Color.gold()
        )
        
        for reward in rewards:
            embed.add_field(name="보상", value=reward, inline=False)
        
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("📊 아직 해금된 도감 보상이 없습니다. 더 많은 몬스터와 아이템을 수집하세요!")

# 뽑기 관련 함수
async def pull_gacha(message, pull_count: int):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    cost = gacha_system.get_pull_cost(pull_count)
    
    if character.gold < cost:
        await message.channel.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
        return
    
    # 뽑기 실행
    results = gacha_system.pull_gacha(pull_count)
    
    # 골드 차감
    character.gold -= cost
    db.update_player(user_id, character.to_dict())
    
    # 뽑기 횟수 증가
    user_pull_counts[user_id] = user_pull_counts.get(user_id, 0) + pull_count
    
    # 결과 표시
    embed = discord.Embed(
        title=f"🎰 뽑기 결과 ({pull_count}회)",
        description=f"{cost}골드를 사용하여 {pull_count}회 뽑기를 실행했습니다!",
        color=discord.Color.pink()
    )
    
    # 결과 요약
    rarity_count = {}
    for result in results:
        rarity = result['rarity']
        rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
    
    summary_text = ""
    for rarity in ['legendary', 'epic', 'rare', 'uncommon', 'common']:
        if rarity in rarity_count:
            emoji = gacha_system.format_rarity_emoji(rarity)
            summary_text += f"{emoji} {rarity}: {rarity_count[rarity]}개\n"
    
    embed.add_field(name="희귀도 분포", value=summary_text, inline=False)
    
    # 개별 결과
    for i, result in enumerate(results, 1):
        item = result['item']
        rarity = result['rarity']
        emoji = gacha_system.format_rarity_emoji(rarity)
        
        embed.add_field(
            name=f"{i}. {emoji} {item.name}",
            value=f"{item.item_type.value} | {item.price}골드",
            inline=True
        )
    
    # 인벤토리에 추가
    inventory_data = db.get_inventory(user_id)
    if inventory_data:
        inventory = Inventory()
        inventory.items = inventory_data['items']
        inventory.equipped = inventory_data['equipped']
        
        added_count = 0
        for result in results:
            if inventory.add_item(result['item']):
                added_count += 1
                # 도감에 아이템 추가
                compendium.add_item(user_id, result['item'].name)
        
        db.update_inventory(user_id, inventory.to_dict())
        
        if added_count > 0:
            embed.add_field(name="📦 인벤토리", value=f"{added_count}개의 아이템이 인벤토리에 추가되었습니다.", inline=False)
    
    await message.channel.send(embed=embed)

async def show_gacha_info(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    total_pulls = user_pull_counts.get(user_id, 0)
    pity_info = gacha_system.get_pity_system_info(total_pulls)
    
    embed = discord.Embed(
        title="🎰 뽑기 정보",
        description="현재 뽑기 시스템 정보",
        color=discord.Color.pink()
    )
    
    embed.add_field(name="💰 1회 뽑기", value="100골드", inline=True)
    embed.add_field(name="💰 10회 뽑기", value="900골드 (10% 할인)", inline=True)
    embed.add_field(name="📊 총 뽑기 횟수", value=str(total_pulls), inline=True)
    
    embed.add_field(name="🏆 레전더리 피티", value=f"{pity_info['legendary_pity']}회 후 보장", inline=True)
    embed.add_field(name="💜 에픽 피티", value=f"{pity_info['epic_pity']}회 후 보장", inline=True)
    
    # 희귀도 확률
    rarity_info = ""
    for rarity, weight in gacha_system.rarity_weights.items():
        emoji = gacha_system.format_rarity_emoji(rarity)
        rarity_info += f"{emoji} {rarity}: {weight}%\n"
    
    embed.add_field(name="📈 희귀도 확률", value=rarity_info, inline=False)
    
    await message.channel.send(embed=embed)

# 상점 시스템 (한국어 로컬라이징)
async def show_shop_main(message):
    """상점 메인 메뉴"""
    user_id = str(message.author.id)
    
    # 페이지 상태 초기화
    shop_page_states[user_id] = {'page': 1, 'category': '전체'}
    
    await show_shop_page(message, 1)

async def show_shop_category(message, category: str):
    """특정 카테고리 상점"""
    user_id = str(message.author.id)
    
    if category not in CATEGORIES:
        await message.channel.send(f"❌ 올바른 카테고리가 아닙니다. 사용 가능한 카테고리: {', '.join(CATEGORIES.keys())}")
        return
    
    shop_page_states[user_id] = {'page': 1, 'category': category}
    
    await show_shop_page(message, 1)

async def show_shop_page(message, page_num: int):
    """상점 특정 페이지 표시"""
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    
    # 페이지 상태 확인
    if user_id not in shop_page_states:
        shop_page_states[user_id] = {'page': 1, 'category': '전체'}
    
    shop_page_states[user_id]['page'] = page_num
    category = shop_page_states[user_id]['category']
    
    # 아이템 필터링
    filtered_items = []
    
    if category == '전체':
        filtered_items = list(SHOP_ITEMS.keys())
    else:
        for item_name, item_data in SHOP_ITEMS.items():
            if item_data['category'] == category:
                filtered_items.append(item_name)
    
    # 페이지네이션
    items_per_page = 4
    total_pages = (len(filtered_items) + items_per_page - 1) // items_per_page
    
    if page_num < 1 or page_num > total_pages:
        page_num = 1
    
    start_idx = (page_num - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_items))
    current_items = filtered_items[start_idx:end_idx]
    
    # 임베드 생성
    embed = discord.Embed(
        title=f"상점 ({page_num}/{total_pages})",
        color=discord.Color.gold()
    )
    
    # 아이템 목록
    for item_name in current_items:
        item_data = SHOP_ITEMS[item_name]
        
        # 가격 표시
        price_text = ""
        for currency, amount in item_data['price'].items():
            icon = CURRENCY_ICONS.get(currency, '💰')
            price_text += f"{amount}{icon} "
        
        embed.add_field(
            name=f"{item_name}",
            value=f"{item_data['description']}\n💰 {price_text}",
            inline=False
        )
    
    # 내 자산
    embed.add_field(name="💰 내 골드", value=str(character.gold), inline=True)
    
    # 네비게이션 안내
    nav_text = ""
    if page_num > 1:
        nav_text += "• !상점이전 - 이전 페이지\n"
    if page_num < total_pages:
        nav_text += "• !상점다음 - 다음 페이지\n"
    nav_text += f"• !상점페이지 [번호] - 특정 페이지"
    
    embed.add_field(name="📖 페이지 이동", value=nav_text or "첫 페이지입니다.", inline=False)
    
    # 카테고리 안내
    category_text = ""
    for cat_key, cat_name in CATEGORIES.items():
        category_text += f"• !상점 {cat_key} - {cat_name}\n"
    
    embed.add_field(name="📂 카테고리", value=category_text, inline=False)
    embed.add_field(name="🛒 구매", value="!구매 [아이템이름]", inline=False)
    
    await message.channel.send(embed=embed)

async def shop_previous_page(message):
    user_id = str(message.author.id)
    if user_id in shop_page_states:
        current_page = shop_page_states[user_id]['page']
        if current_page > 1:
            await show_shop_page(message, current_page - 1)
        else:
            await message.channel.send("❌ 이미 첫 페이지입니다.")
    else:
        await show_shop_page(message, 1)

async def shop_next_page(message):
    user_id = str(message.author.id)
    if user_id in shop_page_states:
        await show_shop_page(message, shop_page_states[user_id]['page'] + 1)
    else:
        await show_shop_page(message, 2)

async def buy_item(message, item_name: str):
    """아이템 구매"""
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    inventory_data = db.get_inventory(user_id)
    
    if not player_data or not inventory_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    inventory = Inventory()
    inventory.items = inventory_data['items']
    inventory.equipped = inventory_data['equipped']
    
    # 아이템 확인
    if item_name not in SHOP_ITEMS:
        await message.channel.send("❌ 존재하지 않는 아이템입니다.")
        return
    
    item_data = SHOP_ITEMS[item_name]
    
    # 구매 확인 상태 체크
    if user_id in shop_confirm_states and shop_confirm_states[user_id] == item_name:
        # 구매 확정
        del shop_confirm_states[user_id]
        
        # 골드 확인 (간단하게 골드만 체크)
        total_gold = item_data['price'].get('골드', 0)
        if character.gold < total_gold:
            await message.channel.send(f"❌ 골드가 부족합니다. 필요: {total_gold}골드")
            return
        
        # 인벤토리 추가
        # 기존 시스템과 호환을 위해 ItemFactory 사용
        try:
            new_item = ItemFactory.create_item(item_name.lower().replace(' ', '_'))
            if new_item.item_id == 'unknown':
                # 해당 아이템이 없으면 기본 아이템 생성
                new_item = ItemFactory.create_item('potion_hp')
                new_item.name = item_name
                new_item.price = total_gold
        except:
            new_item = ItemFactory.create_item('potion_hp')
            new_item.name = item_name
            new_item.price = total_gold
        
        if not inventory.add_item(new_item):
            await message.channel.send("❌ 인벤토리가 가득 찼습니다.")
            return
        
        character.gold -= total_gold
        db.update_player(user_id, character.to_dict())
        db.update_inventory(user_id, inventory.to_dict())
        
        await message.channel.send(f"✅ {item_name}을(를) 구매했습니다!")
    else:
        # 구매 확인 요청
        shop_confirm_states[user_id] = item_name
        
        # 가격 표시
        price_text = ""
        for currency, amount in item_data['price'].items():
            icon = CURRENCY_ICONS.get(currency, '💰')
            price_text += f"{amount}{icon} "
        
        embed = discord.Embed(
            title="🛒 구매 확인",
            description=f"{item_name}을(를) 구매하시겠습니까?",
            color=discord.Color.yellow()
        )
        embed.add_field(name="아이템", value=item_name, inline=True)
        embed.add_field(name="가격", value=price_text, inline=True)
        embed.add_field(name="확인", value="다시 !구매 {item_name}을 입력하면 구매가 확정됩니다.", inline=False)
        
        await message.channel.send(embed=embed)

# 던전 시스템 제거됨

# 마법 관련 함수
async def show_spell_learning(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    available_spells = spell_system.get_available_spells(character.level)
    learned_spells = spell_system.get_learned_spells(user_id)
    
    embed = discord.Embed(
        title="🧙 마법 배우기",
        description=f"LV.{character.level} - 배울 수 있는 마법",
        color=discord.Color.purple()
    )
    
    embed.add_field(name="레벨", value=character.level, inline=True)
    embed.add_field(name="현재 MP", value=f"{character.current_mp}/{character.max_mp}", inline=True)
    
    if available_spells:
        learnable_text = ""
        for spell in available_spells:
            if spell.name not in learned_spells:
                cost = spell.mana_cost * 100  # 배우 비용
                learnable_text += f"• {spell.name} - {cost}골드 (MP: {spell.mana_cost})\n"
        
        if learnable_text:
            embed.add_field(name="배울 수 있는 마법", value=learnable_text, inline=False)
        else:
            embed.add_field(name="배울 수 있는 마법", value="모든 마법을 배웠습니다.", inline=False)
    else:
        embed.add_field(name="배울 수 있는 마법", value="현재 레벨에서 배울 수 있는 마법이 없습니다.", inline=False)
    
    embed.add_field(name="배운 마법", value=", ".join(learned_spells) if learned_spells else "없음", inline=False)
    embed.add_field(name="배우 방법", value="!마법배우기 [마법명] - 마법 배우기", inline=False)
    
    await message.channel.send(embed=embed)

async def show_spell_list(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    learned_spells = spell_system.get_learned_spells(user_id)
    
    embed = discord.Embed(
        title="📖 마법 목록",
        description=f"{character.name}이(가) 배운 마법",
        color=discord.Color.purple()
    )
    
    if learned_spells:
        for spell_name in learned_spells:
            spell = spell_system.get_spell(spell_name)
            if spell:
                embed.add_field(
                    name=f"✨ {spell.name}",
                    value=f"{spell.description}\n마력 소모: {spell.mana_cost} | 위력: {spell.damage}",
                    inline=False
                )
    else:
        embed.add_field(name="마법", value="배운 마법이 없습니다.", inline=False)
    
    embed.add_field(name="시전 방법", value="!마법 [주문명] - 마법 시전", inline=False)
    
    await message.channel.send(embed=embed)

async def cast_spell(message, spell_name):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    
    # 마법 배웠는지 확인
    learned_spells = spell_system.get_learned_spells(user_id)
    if spell_name not in learned_spells:
        await message.channel.send(f"❌ {spell_name} 마법을 배우지 않았습니다.")
        return
    
    spell = spell_system.get_spell(spell_name)
    if not spell:
        await message.channel.send("❌ 존재하지 않는 마법입니다.")
        return
    
    if character.current_mp < spell.mana_cost:
        await message.channel.send(f"❌ 마력이 부족합니다. 필요: {spell.mana_cost}")
        return
    
    # 마법 시전
    success, message, damage = spell_system.cast_spell(spell, character.current_mp)
    
    if success:
        character.current_mp -= spell.mana_cost
        db.update_player(user_id, character.to_dict())
        
        embed = discord.Embed(
            title=f"✨ {spell.name} 시전!",
            description=message,
            color=discord.Color.purple()
        )
        
        if spell.spell_type == 'attack':
            embed.add_field(name="위력", value=damage, inline=True)
        elif spell.spell_type == 'defense':
            embed.add_field(name="회복량", value=damage, inline=True)
        
        embed.add_field(name="남은 MP", value=f"{character.current_mp}/{character.max_mp}", inline=True)
        
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(f"❌ {message}")

async def start_hp_battle(message):
    """Harry Potter 스타일 전투 시작"""
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    if user_id in active_hp_battles:
        await message.channel.send("❌ 이미 진행 중인 전투가 있습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    
    if not character.is_alive():
        await message.channel.send("❌ 캐릭터가 사망했습니다. !회복으로 회복하세요.")
        return
    
    # 랜덤한 적 생성
    enemies = ['마법사 거미', '불사용 기수', '바실리스크', '디멘터', '보가트']
    enemy_name = random.choice(enemies)
    enemy_level = character.level
    
    battle = HogwartsBattle(character, enemy_name, enemy_level)
    active_hp_battles[user_id] = battle
    
    embed = discord.Embed(
        title=f"⚡ 마법 대결 시작!",
        description=f"{enemy_name}(이)가 나타났습니다!",
        color=discord.Color.purple()
    )
    embed.add_field(name="상대", value=f"{character.name} vs {enemy_name}", inline=True)
    embed.add_field(name="HP", value="Harry Potter 스타일 전투", inline=True)
    embed.add_field(name="상대 HP", value=f"{character.current_hp}/{character.max_hp} vs {battle.enemy_current_hp}/{battle.enemy_max_hp}", inline=False)
    
    await message.channel.send(embed=embed)
    await show_hp_battle_actions(message)

async def show_hp_battle_actions(message):
    user_id = str(message.author.id)
    battle = active_hp_battles.get(user_id)
    
    if not battle:
        return
    
    embed = discord.Embed(
        title="🎯 마법 대결 행동",
        description="Harry Potter 스타일 전투!",
        color=discord.Color.purple()
    )
    
    learned_spells = spell_system.get_learned_spells(user_id)
    spell_list = ", ".join(learned_spells) if learned_spells else "배운 마법이 없습니다"
    
    embed.add_field(name="!공격", value="기본 공격", inline=True)
    embed.add_field(name="!마법 [주문]", value="마법 시전", inline=True)
    embed.add_field(name="!방어", value="방어 태세", inline=True)
    embed.add_field(name="!무장해제", value="적 약화", inline=True)
    embed.add_field(name="사용 가능한 마법", value=spell_list, inline=False)
    
    await message.channel.send(embed=embed)

async def perform_hp_battle_action(message, action: str, spell_name: str = None):
    user_id = str(message.author.id)
    battle = active_hp_battles.get(user_id)
    
    if not battle:
        await message.channel.send("❌ 진행 중인 전투가 없습니다.")
        return
    
    if action == 'attack':
        result = battle.process_turn('attack')
        await handle_hp_battle_result(message, result, user_id)
    elif action == 'spell' and spell_name:
        result = battle.process_turn('spell', spell_name)
        await handle_hp_battle_result(message, result, user_id)
    elif action == 'defend':
        result = battle.process_turn('defend')
        await handle_hp_battle_result(message, result, user_id)
    elif action == 'disarm':
        result = battle.process_turn('disarm')
        await handle_hp_battle_result(message, result, user_id)

async def handle_hp_battle_result(message, result, user_id):
    if 'error' in result:
        await message.channel.send(f"❌ {result['error']}")
        return
    
    for log in result.get('results', []):
        if isinstance(log, dict):
            if log.get('action') == 'defend':
                await message.channel.send(f"🛡️ {log['actor']}이(가) 방어 태세를 취합니다!")
            elif log.get('action') == 'disarm':
                await message.channel.send(f"⚔️ {log['actor']}이(가) 무장 해제 마법을 시전합니다!")
            else:
                damage = log.get('damage', 0)
                defender = log.get('defender', '')
                attacker = log.get('attacker', '')
                
                if log.get('defeated', False):
                    await message.channel.send(f"💥 {attacker}이(가) {defender}에게 {damage} 데미지를 입혔습니다!")
                else:
                    await message.channel.send(f"🗡️ {attacker}이(가) {defender}에게 {damage} 데미지를 입혔습니다!")
    
    if result.get('battle_end'):
        battle = active_hp_battles[user_id]
        del active_hp_battles[user_id]
        
        if result['winner'] == 'player':
            character = battle.player
            exp_gained = 50 * battle.enemy_level
            gold_gained = 30 * battle.enemy_level
            
            leveled_up = character.gain_exp(exp_gained)
            character.gold += gold_gained
            character.heal(character.max_hp // 2)
            character.restore_mp(character.max_mp // 2)
            
            db.update_player(user_id, character.to_dict())
            
            embed = discord.Embed(
                title="🎉 마법 대결 승리!",
                description=f"{battle.enemy_name}을(를) 물리쳤습니다!",
                color=discord.Color.gold()
            )
            embed.add_field(name="획득 경험치", value=exp_gained, inline=True)
            embed.add_field(name="획득 골드", value=gold_gained, inline=True)
            embed.add_field(name="하우스포인트", value=f"+{battle.player_house_points}", inline=True)
            
            if leveled_up:
                embed.add_field(name="🎊 레벨업!", value=f"현재 레벨: {character.level}", inline=False)
            
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("💀 마법 대결 패배... 하우스포인트를 획득했습니다.")
    else:
        battle = active_hp_battles[user_id]
        status = battle.get_battle_status()
        
        embed = discord.Embed(
            title=f"⚡ 마법 대결 진행 중 (턴 {status['turn']})",
            color=discord.Color.purple()
        )
        embed.add_field(name="내 HP", value=status['player_hp'], inline=True)
        embed.add_field(name="내 MP", value=status['player_mp'], inline=True)
        embed.add_field(name="적 HP", value=status['enemy_hp'], inline=True)
        
        await message.channel.send(embed=embed)
        await show_hp_battle_actions(message)

# 전직 관련 함수
async def show_job_advancement_info(message):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    current_stage = player_job_stages.get(user_id, 1)
    current_job = player_current_jobs.get(user_id, character.character_class.name)
    
    available_jobs = job_advancement.get_available_advancements(
        character.character_class.name, character.level, current_stage
    )
    
    embed = discord.Embed(
        title=f"⚔️ 전직 정보",
        description=f"현재: {current_job} (스테이지 {current_stage})",
        color=discord.Color.purple()
    )
    
    embed.add_field(name="레벨", value=character.level, inline=True)
    embed.add_field(name="클래스", value=character.character_class.name, inline=True)
    
    if available_jobs:
        embed.add_field(name="가능한 전직", value="", inline=False)
        
        for job in available_jobs:
            job_name = job['job_name']
            stage = job['stage']
            level_req = job['level_requirement']
            description = job['description']
            
            bonus_text = ""
            for stat, bonus in job['stat_bonus'].items():
                bonus_text += f"{stat}+{bonus} "
            
            embed.add_field(
                name=f"{stage}차: {job_name} (LV.{level_req}+)",
                value=f"{description}\n능력치: {bonus_text}",
                inline=False
            )
        
        embed.add_field(name="전직 방법", value="!전직 [직업이름]", inline=False)
    else:
        if current_stage == 1:
            embed.add_field(name="전직 조건", value="2차 전직: LV.20+\n3차 전직: LV.40+", inline=False)
        elif current_stage == 2:
            embed.add_field(name="전직 조건", value="3차 전직: LV.40+", inline=False)
        else:
            embed.add_field(name="전직", value="최고 스테이지에 도달했습니다!", inline=False)
    
    await message.channel.send(embed=embed)

async def perform_job_advancement(message, job_name):
    user_id = str(message.author.id)
    player_data = db.get_player(user_id)
    
    if not player_data:
        await message.channel.send("❌ 캐릭터가 존재하지 않습니다.")
        return
    
    character = CharacterFactory.from_dict(player_data)
    current_stage = player_job_stages.get(user_id, 1)
    
    available_jobs = job_advancement.get_available_advancements(
        character.character_class.name, character.level, current_stage
    )
    
    # 전직 가능한지 확인
    target_job = None
    for job in available_jobs:
        if job['job_name'] == job_name:
            target_job = job
            break
    
    if not target_job:
        await message.channel.send("❌ 전직할 수 없는 직업이거나 조건이 충족되지 않습니다.")
        return
    
    # 전직 비용
    cost = target_job['stage'] * 1000  # 2차: 2000, 3차: 3000
    
    if character.gold < cost:
        await message.channel.send(f"❌ 골드가 부족합니다. 전직 비용: {cost}골드")
        return
    
    # 전직 실행
    character.gold -= cost
    
    # 능력치 보너스 적용
    for stat, bonus in target_job['stat_bonus'].items():
        if stat == 'hp':
            character.max_hp += bonus
            character.current_hp += bonus
        elif stat == 'mp':
            character.max_mp += bonus
            character.current_mp += bonus
        elif stat == 'attack':
            character.attack += bonus
        elif stat == 'defense':
            character.defense += bonus
        elif stat == 'speed':
            character.speed += bonus
    
    # 스킬 추가
    for skill in target_job['new_skills']:
        if skill not in character.skills:
            character.skills.append(skill)
    
    # 직업 정보 업데이트
    player_job_stages[user_id] = target_job['stage']
    player_current_jobs[user_id] = job_name
    
    db.update_player(user_id, character.to_dict())
    
    embed = discord.Embed(
        title=f"🎊 전직 성공!",
        description=f"{character.character_class.name} → {job_name}",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="새로운 직업", value=job_name, inline=True)
    embed.add_field(name="스테이지", value=f"{target_job['stage']}차", inline=True)
    
    bonus_text = ""
    for stat, bonus in target_job['stat_bonus'].items():
        bonus_text += f"{stat}+{bonus} "
    
    embed.add_field(name="능력치 증가", value=bonus_text, inline=False)
    embed.add_field(name="새로운 스킬", value=", ".join(target_job['new_skills']), inline=False)
    
    await message.channel.send(embed=embed)

if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        print("DISCORD_TOKEN 환경 변수를 설정해주세요!")
    else:
        client.run(config.DISCORD_TOKEN)