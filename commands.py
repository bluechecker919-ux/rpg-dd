import discord
from discord.ext import commands
from rpg_system import CharacterFactory, Character
from battle_system import Battle, EnemyFactory
from item_system import ItemFactory, Inventory, ItemType
from database import Database
import config

class RPGCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.active_battles = {}  # user_id: Battle
        self.cooldown = {}  # user_id: last_command_time
    
    def check_cooldown(self, user_id: str, cooldown_time: float = 1.0) -> bool:
        """명령어 쿨다운 체크"""
        import time
        current_time = time.time()
        
        if user_id in self.cooldown:
            if current_time - self.cooldown[user_id] < cooldown_time:
                return False  # 쿨다운 중
        
        self.cooldown[user_id] = current_time
        return True
    
    @commands.command(name='캐릭터생성')
    async def create_character(self, ctx, name: str, class_name: str):
        """새로운 캐릭터를 생성합니다."""
        user_id = str(ctx.author.id)
        
        # 쿨다운 체크
        if not self.check_cooldown(user_id, 2.0):
            return  # 쿨다운 중인 경우 무시
        
        if self.db.get_player(user_id):
            await ctx.send("❌ 이미 캐릭터가 존재합니다!")
            return
        
        valid_classes = ['전사', '마법사', '궁수', '도적']
        if class_name not in valid_classes:
            await ctx.send(f"❌ 올바른 클래스를 선택해주세요: {', '.join(valid_classes)}")
            return
        
        character = CharacterFactory.create_character(user_id, name, class_name)
        self.db.create_player(user_id, character.to_dict())
        
        # 인벤토리 생성
        inventory = Inventory()
        self.db.create_inventory(user_id, inventory.to_dict())
        
        embed = discord.Embed(
            title=f"🎭 캐릭터 생성 완료!",
            description=f"{name}님이 {class_name}(으)로 모험을 시작합니다!",
            color=discord.Color.green()
        )
        embed.add_field(name="이름", value=character.name, inline=True)
        embed.add_field(name="클래스", value=character.character_class.name, inline=True)
        embed.add_field(name="레벨", value=character.level, inline=True)
        embed.add_field(name="HP", value=f"{character.current_hp}/{character.max_hp}", inline=True)
        embed.add_field(name="MP", value=f"{character.current_mp}/{character.max_mp}", inline=True)
        embed.add_field(name="골드", value=character.gold, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='내정보')
    async def show_character_info(self, ctx):
        """내 캐릭터 정보를 표시합니다."""
        user_id = str(ctx.author.id)
        player_data = self.db.get_player(user_id)
        
        if not player_data:
            await ctx.send("❌ 캐릭터가 존재하지 않습니다. `!캐릭터생성 [이름] [클래스]`로 캐릭터를 생성하세요.")
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
        embed.add_field(name="공격력", value=character.attack, inline=True)
        embed.add_field(name="방어력", value=character.defense, inline=True)
        embed.add_field(name="속도", value=character.speed, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='전투시작')
    async def start_battle(self, ctx):
        """전투를 시작합니다."""
        user_id = str(ctx.author.id)
        player_data = self.db.get_player(user_id)
        
        if not player_data:
            await ctx.send("❌ 캐릭터가 존재하지 않습니다.")
            return
        
        if user_id in self.active_battles:
            await ctx.send("❌ 이미 진행 중인 전투가 있습니다.")
            return
        
        character = CharacterFactory.from_dict(player_data)
        
        if not character.is_alive():
            await ctx.send("❌ 캐릭터가 사망했습니다. `!회복`으로 회복하세요.")
            return
        
        enemy = EnemyFactory.create_enemy(character.level)
        battle = Battle(character, enemy)
        self.active_battles[user_id] = battle
        
        embed = discord.Embed(
            title=f"⚔️ 전투 시작!",
            description=f"{enemy.name}(이)가 나타났습니다!",
            color=discord.Color.red()
        )
        embed.add_field(name="적 정보", value=f"LV.{enemy.level} {enemy.name}", inline=True)
        embed.add_field(name="적 HP", value=f"{enemy.current_hp}/{enemy.max_hp}", inline=True)
        embed.add_field(name="내 HP", value=f"{character.current_hp}/{character.max_hp}", inline=True)
        
        await ctx.send(embed=embed)
        await self.show_battle_actions(ctx)
    
    async def show_battle_actions(self, ctx):
        user_id = str(ctx.author.id)
        battle = self.active_battles.get(user_id)
        
        if not battle:
            return
        
        embed = discord.Embed(
            title="🎯 행동 선택",
            description="전투 중 행동을 선택하세요:",
            color=discord.Color.gold()
        )
        embed.add_field(name="!공격", value="기본 공격", inline=True)
        embed.add_field(name="!스킬 [스킬명]", value="스킬 사용", inline=True)
        embed.add_field(name="!방어", value="방어 태세", inline=True)
        embed.add_field(name="!도망", value="전투 도망", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='공격')
    async def attack(self, ctx):
        """전투 중 기본 공격을 수행합니다."""
        user_id = str(ctx.author.id)
        battle = self.active_battles.get(user_id)
        
        if not battle:
            await ctx.send("❌ 진행 중인 전투가 없습니다.")
            return
        
        result = battle.process_turn('attack')
        await self.handle_battle_result(ctx, result)
    
    @commands.command(name='스킬')
    async def use_skill(self, ctx, skill_name: str):
        """전투 중 스킬을 사용합니다."""
        user_id = str(ctx.author.id)
        battle = self.active_battles.get(user_id)
        
        if not battle:
            await ctx.send("❌ 진행 중인 전투가 없습니다.")
            return
        
        result = battle.process_turn('skill', skill_name)
        await self.handle_battle_result(ctx, result)
    
    @commands.command(name='방어')
    async def defend(self, ctx):
        """전투 중 방어 태세를 취합니다."""
        user_id = str(ctx.author.id)
        battle = self.active_battles.get(user_id)
        
        if not battle:
            await ctx.send("❌ 진행 중인 전투가 없습니다.")
            return
        
        result = battle.process_turn('defend')
        await self.handle_battle_result(ctx, result)
    
    @commands.command(name='도망')
    async def flee(self, ctx):
        """전투에서 도망칩니다."""
        user_id = str(ctx.author.id)
        battle = self.active_battles.get(user_id)
        
        if not battle:
            await ctx.send("❌ 진행 중인 전투가 없습니다.")
            return
        
        # 50% 확률로 도망 성공
        import random
        if random.random() < 0.5:
            del self.active_battles[user_id]
            await ctx.send("🏃 도망에 성공했습니다!")
        else:
            await ctx.send("❌ 도망에 실패했습니다! 적의 공격!")
            result = battle.process_turn('attack')
            await self.handle_battle_result(ctx, result)
    
    async def handle_battle_result(self, ctx, result):
        user_id = str(ctx.author.id)
        
        if 'error' in result:
            await ctx.send(f"❌ {result['error']}")
            return
        
        # 전투 로그 표시
        for log in result.get('results', []):
            if isinstance(log, dict):
                if log.get('action') == 'defend':
                    await ctx.send(f"🛡️ {log['actor']}이(가) 방어 태세를 취합니다!")
                else:
                    damage = log.get('damage', 0)
                    defender = log.get('defender', '')
                    attacker = log.get('attacker', '')
                    skill = log.get('skill', '')
                    
                    if skill:
                        await ctx.send(f"✨ {attacker}이(가) {skill} 사용! {defender}에게 {damage} 데미지!")
                    else:
                        await ctx.send(f"🗡️ {attacker}이(가) {defender}에게 {damage} 데미지를 입혔습니다!")
        
        if result.get('battle_end'):
            battle = self.active_battles[user_id]
            del self.active_battles[user_id]
            
            if result['winner'] == 'player':
                # 전투 보상
                character = battle.player
                exp_gained = battle.enemy.exp_reward
                gold_gained = battle.enemy.gold_reward
                
                leveled_up = character.gain_exp(exp_gained)
                character.gold += gold_gained
                
                # HP/MP 회복
                character.heal(character.max_hp // 2)
                character.restore_mp(character.max_mp // 2)
                
                self.db.update_player(user_id, character.to_dict())
                
                embed = discord.Embed(
                    title="🎉 전투 승리!",
                    description=f"{battle.enemy.name}을(를) 물리쳤습니다!",
                    color=discord.Color.green()
                )
                embed.add_field(name="획득 경험치", value=exp_gained, inline=True)
                embed.add_field(name="획득 골드", value=gold_gained, inline=True)
                
                if leveled_up:
                    embed.add_field(name="🎊 레벨업!", value=f"현재 레벨: {character.level}", inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("💀 전투 패배... 캐릭터가 사망했습니다.")
        else:
            # 전투 상태 표시
            battle = self.active_battles[user_id]
            status = battle.get_battle_status()
            
            embed = discord.Embed(
                title=f"⚔️ 전투 진행 중 (턴 {status['turn']})",
                color=discord.Color.orange()
            )
            embed.add_field(name="내 HP", value=status['player_hp'], inline=True)
            embed.add_field(name="내 MP", value=status['player_mp'], inline=True)
            embed.add_field(name="적 HP", value=status['enemy_hp'], inline=True)
            
            await ctx.send(embed=embed)
            await self.show_battle_actions(ctx)
    
    @commands.command(name='회복')
    async def heal_character(self, ctx):
        """캐릭터를 회복합니다."""
        user_id = str(ctx.author.id)
        player_data = self.db.get_player(user_id)
        
        if not player_data:
            await ctx.send("❌ 캐릭터가 존재하지 않습니다.")
            return
        
        character = CharacterFactory.from_dict(player_data)
        
        if character.is_alive():
            await ctx.send("❌ 캐릭터가 이미 살아있습니다.")
            return
        
        cost = character.level * 10
        if character.gold < cost:
            await ctx.send(f"❌ 골드가 부족합니다. 필요: {cost}골드")
            return
        
        character.gold -= cost
        character.current_hp = character.max_hp
        character.current_mp = character.max_mp
        
        self.db.update_player(user_id, character.to_dict())
        
        await ctx.send(f"✅ {cost}골드를 지불하고 회복했습니다!")
    
    @commands.command(name='인벤토리')
    async def show_inventory(self, ctx):
        """인벤토리를 표시합니다."""
        user_id = str(ctx.author.id)
        inventory_data = self.db.get_inventory(user_id)
        
        if not inventory_data:
            await ctx.send("❌ 인벤토리가 존재하지 않습니다.")
            return
        
        inventory = Inventory()
        inventory.items = inventory_data['items']
        inventory.equipped = inventory_data['equipped']
        
        embed = discord.Embed(
            title="🎒 인벤토리",
            description=f"슬롯: {len(inventory.items)}/{inventory.max_slots}",
            color=discord.Color.purple()
        )
        
        # 장비 표시
        equipped_text = ""
        for slot, item in inventory.equipped.items():
            if item:
                equipped_text += f"{slot}: {item['name']}\n"
            else:
                equipped_text += f"{slot}: 없음\n"
        
        embed.add_field(name="장비", value=equipped_text or "장착한 장비가 없습니다.", inline=False)
        
        # 아이템 표시
        if inventory.items:
            items_text = ""
            for item_id, quantity in inventory.items.items():
                item = ItemFactory.create_item(item_id)
                items_text += f"{item.name} x{quantity}\n"
            embed.add_field(name="아이템", value=items_text, inline=False)
        else:
            embed.add_field(name="아이템", value="인벤토리가 비어있습니다.", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='상점')
    async def show_shop(self, ctx):
        """상점 아이템을 표시합니다."""
        shop_items = ItemFactory.get_shop_items()
        
        embed = discord.Embed(
            title="🏪 상점",
            description="아이템을 구매하려면 `!구매 [아이템ID]`를 입력하세요.",
            color=discord.Color.gold()
        )
        
        for item in shop_items:
            item_type = item.item_type.value
            stat_text = ""
            if item.stat_bonus:
                stat_text = " ("
                for stat, bonus in item.stat_bonus.items():
                    stat_text += f"{stat}+{bonus} "
                stat_text = stat_text.strip() + ")"
            
            embed.add_field(
                name=f"{item.name} - {item.price}골드",
                value=f"{item_type}{stat_text}\nID: {item.item_id}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='구매')
    async def buy_item(self, ctx, item_id: str):
        """상점에서 아이템을 구매합니다."""
        user_id = str(ctx.author.id)
        player_data = self.db.get_player(user_id)
        inventory_data = self.db.get_inventory(user_id)
        
        if not player_data or not inventory_data:
            await ctx.send("❌ 캐릭터가 존재하지 않습니다.")
            return
        
        character = CharacterFactory.from_dict(player_data)
        inventory = Inventory()
        inventory.items = inventory_data['items']
        inventory.equipped = inventory_data['equipped']
        
        item = ItemFactory.create_item(item_id)
        
        if item.item_id == 'unknown':
            await ctx.send("❌ 존재하지 않는 아이템입니다.")
            return
        
        if character.gold < item.price:
            await ctx.send(f"❌ 골드가 부족합니다. 필요: {item.price}골드")
            return
        
        if not inventory.add_item(item):
            await ctx.send("❌ 인벤토리가 가득 찼습니다.")
            return
        
        character.gold -= item.price
        self.db.update_player(user_id, character.to_dict())
        self.db.update_inventory(user_id, inventory.to_dict())
        
        await ctx.send(f"✅ {item.name}을(를) {item.price}골드에 구매했습니다!")
    
    @commands.command(name='사용')
    async def use_item(self, ctx, item_id: str):
        """아이템을 사용합니다."""
        user_id = str(ctx.author.id)
        player_data = self.db.get_player(user_id)
        inventory_data = self.db.get_inventory(user_id)
        
        if not player_data or not inventory_data:
            await ctx.send("❌ 캐릭터가 존재하지 않습니다.")
            return
        
        character = CharacterFactory.from_dict(player_data)
        inventory = Inventory()
        inventory.items = inventory_data['items']
        inventory.equipped = inventory_data['equipped']
        
        item = ItemFactory.create_item(item_id)
        
        if item.item_id == 'unknown':
            await ctx.send("❌ 존재하지 않는 아이템입니다.")
            return
        
        if inventory.get_item_quantity(item_id) <= 0:
            await ctx.send("❌ 인벤토리에 해당 아이템이 없습니다.")
            return
        
        if not item.consumable:
            await ctx.send("❌ 사용할 수 없는 아이템입니다.")
            return
        
        # 아이템 효과 적용
        if 'hp' in item.stat_bonus:
            character.heal(item.stat_bonus['hp'])
            await ctx.send(f"❤️ HP가 {item.stat_bonus['hp']} 회복되었습니다!")
        
        if 'mp' in item.stat_bonus:
            character.restore_mp(item.stat_bonus['mp'])
            await ctx.send(f"💙 MP가 {item.stat_bonus['mp']} 회복되었습니다!")
        
        inventory.remove_item(item_id)
        self.db.update_player(user_id, character.to_dict())
        self.db.update_inventory(user_id, inventory.to_dict())
    
    @commands.command(name='장착')
    async def equip_item(self, ctx, item_id: str):
        """아이템을 장착합니다."""
        user_id = str(ctx.author.id)
        inventory_data = self.db.get_inventory(user_id)
        
        if not inventory_data:
            await ctx.send("❌ 인벤토리가 존재하지 않습니다.")
            return
        
        inventory = Inventory()
        inventory.items = inventory_data['items']
        inventory.equipped = inventory_data['equipped']
        
        item = ItemFactory.create_item(item_id)
        
        if item.item_id == 'unknown':
            await ctx.send("❌ 존재하지 않는 아이템입니다.")
            return
        
        if inventory.get_item_quantity(item_id) <= 0:
            await ctx.send("❌ 인벤토리에 해당 아이템이 없습니다.")
            return
        
        # 적절한 슬롯 결정
        slot_mapping = {
            ItemType.WEAPON: 'weapon',
            ItemType.ARMOR: 'armor'
        }
        
        slot = slot_mapping.get(item.item_type)
        if not slot:
            await ctx.send("❌ 장착할 수 없는 아이템입니다.")
            return
        
        if inventory.equip_item(item, slot):
            self.db.update_inventory(user_id, inventory.to_dict())
            await ctx.send(f"✅ {item.name}을(를) 장착했습니다!")
        else:
            await ctx.send("❌ 장착에 실패했습니다.")
    
    @commands.command(name='도움말')
    async def show_help(self, ctx):
        """도움말을 표시합니다."""
        embed = discord.Embed(
            title="📖 정통 판타지 RPG 봇 도움말",
            description="디스코드에서 RPG를 즐겨보세요!",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="캐릭터 관리", value="`!캐릭터생성 [이름] [클래스]` - 캐릭터 생성\n`!내정보` - 내 캐릭터 정보", inline=False)
        embed.add_field(name="전투", value="`!전투시작` - 전투 시작\n`!공격` - 기본 공격\n`!스킬 [스킬명]` - 스킬 사용\n`!방어` - 방어 태세\n`!도망` - 전투 도망\n`!회복` - 캐릭터 회복", inline=False)
        embed.add_field(name="아이템", value="`!인벤토리` - 인벤토리 확인\n`!상점` - 상점 목록\n`!구매 [아이템ID]` - 아이템 구매\n`!사용 [아이템ID]` - 아이템 사용\n`!장착 [아이템ID]` - 아이템 장착", inline=False)
        embed.add_field(name="클래스", value="전사, 마법사, 궁수, 도적", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RPGCommands(bot))
