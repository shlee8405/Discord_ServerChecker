from dotenv import load_dotenv
import os
import discord
import aiohttp
import asyncio
from datetime import datetime, time, timedelta

load_dotenv()

intents = discord.Intents.default() 
intents.messages = True  
client = discord.Client(intents=intents)
server_url= os.getenv("SERVER_URL")
api_version =  os.getenv("API_VERSION")
phone_number = os.getenv("PHONE_NUMBER")
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = int(os.getenv('CHANNEL_ID'))

async def server_check():
    while True:
        now = datetime.now().time() # 서버 재시각 시간이 1시. 그때 시도 안함.
        if time(0, 50) < now < time(1, 10):
            current_datetime = datetime.now()
            target_datetime = current_datetime.replace(hour=1, minute=11, second=0, microsecond=0)
            if now > time(1, 10):
                target_datetime += timedelta(days=1)
            wait_seconds = (target_datetime - current_datetime).total_seconds()
            await asyncio.sleep(wait_seconds)
        else:
            async with aiohttp.ClientSession() as session:
                try:
                    url = f"{server_url}/api/members/check/phones?phoneNumber={phone_number}"
                    headers = {
                        "Content-Type": "application/json",
                        "X-API-VERSION": api_version,
                    }
                    async with session.get(url, headers=headers) as response:
                        print(f"Status code: {response.status}")
                        response_text = await response.text()  
                        print(f"Response: {response_text}")
                        if 500 <= response.status < 600:
                            channel = client.get_channel(channel_id)  
                            await channel.send('서버 오류가 감지되었습니다!')
                            break
                except aiohttp.ClientError as e:
                    print(f"HTTP 요청 실패: {e}")
                    channel = client.get_channel(channel_id)
                    await channel.send('서버 오류가 감지되었습니다!')
                    break
                except asyncio.TimeoutError as e:
                    print(f"요청 시간 초과: {e}")
                    channel = client.get_channel(channel_id)
                    await channel.send('서버 오류가 감지되었습니다!')
                    break
                except Exception as e: 
                    print(f"오류 발생: {e}")
                    channel = client.get_channel(channel_id)
                    await channel.send('서버 오류가 감지되었습니다!')
                    break
                finally:
                    await asyncio.sleep(600) # 서버 확인할 시간 설정 
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await server_check()

client.run(discord_bot_token)