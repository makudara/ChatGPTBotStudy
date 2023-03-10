import os
import re
import asyncio
import logging

import openai
import discord

import role_config

logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
token = os.environ['DISCORD_TOKEN']  #Discordのトークン
openai.api_key = os.environ['OPENAI_API_KEY'] #APIキー
LIMIT_MEMORY = 5
model_engine = "gpt-3.5-turbo"
bot_name = 'AnyaGPT'

# Todo: LangChain等を使ってトークンを節約できるかも？
# ref: https://note.com/npaka/n/n155e66a263a2
async def get_memories(message):
    memories = []
    thread = message.channel
    async for msg in thread.history(limit=None):
        mention_bots = [mention for mention in msg.mentions if mention.bot]
        # Chat_GPTの応答を記憶として追加 (コードとか聞くと長いので試しに停止)
        if msg.author.bot:
            pass
            #memories.append({'role': 'assistant', 'content': msg.content})
        # UserのBot向けの会話を記憶として追加
        elif mention_bots:
            content = re.sub('<@[0-9]+>', '', msg.content)
            memories.append({'role': 'user', 'content': content})
    return memories

@client.event
async def on_ready():
    logger.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global model_engine
    if message.author.bot:
        return
    if message.author == client.user:
        return

    if client.user in message.mentions:
        msg = await message.reply("アーニャ考え中🤔...", mention_author=False)
        # スレッドなら記憶を作成
        if type(message.channel) == discord.threads.Thread:
            thread = message.channel
        # スレッドがなければ作成
        else:
            channel = message.channel
            thread_title = re.sub('<@[0-9]+>', '', message.content)
            thread = await channel.create_thread(name=thread_title, reason="アーニャ返信中", type=discord.ChannelType.public_thread)
        try:
            prompt = message.content
            # スレッドなら記憶を作成
            if type(message.channel) == discord.threads.Thread:
                reply_chain = get_memories(message)
                reply_chain = await asyncio.gather(reply_chain)
                reply_chain = reply_chain[0][2:] # 入力文とローディングを除外
                reply_chain = reply_chain[::-1] # 時系列順にソート
                reply_chain = reply_chain[:LIMIT_MEMORY] # トークン量を節約
            else:
                reply_chain = []  
                
            if not prompt:
                await msg.delete()
                await message.channel.send("なんかいえ✋")
                return
            role_prompt = [role_config.get_role('Anya')]
            user_prompt = [{
                    "role": "user",
                    "content": prompt
                }]
            # 各プロンプトを結合
            messages = role_prompt + reply_chain + user_prompt
            logger.info("memory size: "+str(len(messages)))
            completion = openai.ChatCompletion.create(model=model_engine, messages=messages)
            total_tokens = completion["usage"]["total_tokens"]
            cost = total_tokens/1000*0.002
            logger.info(f'total_tokens: {total_tokens}: ${cost}')
            response = completion["choices"][0]["message"]["content"]
            await msg.delete()
            await thread.send(response, mention_author=False)
        except:
            import traceback
            traceback.print_exc()
            await msg.delete()
            await thread.thread_delete()
            await message.reply("アーニャ失敗した😵‍💫", mention_author=False)
            exit()

client.run(token)