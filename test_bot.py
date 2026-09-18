import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user}가 연결되었습니다!')

@bot.command(name='테스트')
async def test(ctx):
    await ctx.send("테스트 응답입니다!")

if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        bot.run(config.DISCORD_TOKEN)
    else:
        print("토큰이 없습니다.")