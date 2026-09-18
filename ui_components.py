import discord
from discord.ui import Button, View, Select
from typing import Optional, Callable, Any

class ButtonView(View):
    def __init__(self, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.callback_data = None
    
    def add_callback(self, button: Button, callback: Callable):
        async def wrapper(interaction: discord.Interaction):
            await callback(interaction)
            self.callback_data = button.label
        button.callback = wrapper

class CharacterCreationView(View):
    def __init__(self, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.selected_class = None
    
    @discord.ui.button(label="전사", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def warrior_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_class = "전사"
        await interaction.response.edit_message(content="전사를 선택했습니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="마법사", style=discord.ButtonStyle.primary, emoji="🔮")
    async def mage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_class = "마법사"
        await interaction.response.edit_message(content="마법사를 선택했습니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="궁수", style=discord.ButtonStyle.primary, emoji="🏹")
    async def archer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_class = "궁수"
        await interaction.response.edit_message(content="궁수를 선택했습니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="도적", style=discord.ButtonStyle.primary, emoji="🗡️")
    async def rogue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_class = "도적"
        await interaction.response.edit_message(content="도적를 선택했습니다!", view=None)
        self.stop()

class BattleActionView(View):
    def __init__(self, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.action = None
        self.skill_name = None
    
    @discord.ui.button(label="방어", style=discord.ButtonStyle.success, emoji="🛡️")
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.action = "defend"
        await interaction.response.edit_message(content="방어 태세를 취합니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="도망", style=discord.ButtonStyle.danger, emoji="🏃")
    async def flee_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.action = "flee"
        await interaction.response.edit_message(content="도망을 시도합니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="인벤토리", style=discord.ButtonStyle.secondary, emoji="🎒")
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.action = "inventory"
        await interaction.response.edit_message(content="인벤토리를 엽니다!", view=None)
        self.stop()

class ShopCategorySelect(Select):
    def __init__(self, categories: dict):
        self.categories = categories
        options = [
            discord.SelectOption(
                label=category_name,
                description=description,
                emoji=emoji
            )
            for category_name, (description, emoji) in categories.items()
        ]
        super().__init__(
            placeholder="카테고리를 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.selected_category = None
    
    async def callback(self, interaction: discord.Interaction):
        self.selected_category = self.values[0]
        await interaction.response.edit_message(content=f"{self.selected_category} 카테고리를 선택했습니다!", view=None)

class ShopView(View):
    def __init__(self, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.selected_action = None
        self.selected_item = None
    
    @discord.ui.button(label="이전", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_action = "previous"
        await interaction.response.edit_message(view=None)
        self.stop()
    
    @discord.ui.button(label="다음", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_action = "next"
        await interaction.response.edit_message(view=None)
        self.stop()
    
    @discord.ui.button(label="구매", style=discord.ButtonStyle.success, emoji="💰")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_action = "buy"
        await interaction.response.edit_message(content="구매를 진행합니다!", view=None)
        self.stop()
    
    @discord.ui.button(label="나가기", style=discord.ButtonStyle.danger, emoji="❌")
    async def exit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_action = "exit"
        await interaction.response.edit_message(content="상점을 나갑니다.", view=None)
        self.stop()
