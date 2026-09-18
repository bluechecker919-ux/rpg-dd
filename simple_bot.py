import discord
import config

# 가장 기본적인 설정
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user}로 로그인했습니다!')

@client.event
async def on_message(message):
    # 봇 자신의 메시지 무시
    if message.author.bot:
        return
    
    # 간단한 명령어 처리
    if message.content.startswith('!테스트'):
        await message.channel.send("테스트 응답!")
    
    if message.content.startswith('!핑'):
        await message.channel.send("퐁!")

if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        client.run(config.DISCORD_TOKEN)
    else:
        print("토큰이 없습니다.")