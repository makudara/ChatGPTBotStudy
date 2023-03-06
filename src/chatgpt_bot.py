import os
import re
import asyncio
import logging

import openai
import discord

logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
token = os.environ['DISCORD_TOKEN']  #Discordのトークン
openai.api_key = os.environ['OPENAI_API_KEY'] #APIキー
model_engine = "gpt-3.5-turbo"
bot_name = 'AnyaGPT'

async def get_memories(message):
    messages = []
    if type(message.channel) == discord.threads.Thread:
        thread = message.channel
        logger.info(thread.history)
        async for msg in thread.history(limit=None):
            mention_bots = [mention for mention in msg.mentions if mention.bot]
            if mention_bots:
                content = re.sub('<@[0-9]+>', '', msg.content)
                messages.append(content)
    return messages

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
        try:
            prompt = message.content
            reply_chain = get_memories(message)
            reply_chain = await asyncio.gather(reply_chain)
            reply_chain = list(reply_chain)
            logger.info(reply_chain)
            if not prompt:
                await msg.delete()
                await message.channel.send("なんかいえ。")
                return
            completion = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {
                    "role": "system",
                    "content": "あなたはアーニャです。以下の条件を守って回答してください。\
                    アーニャはイーデン校に通う天真爛漫で好奇心旺盛な女の子です。\
                    家族は、父と母と、犬のボンドです。父は、かっこいいスパイのロイド・フォージャーで、母は、強くてきれいなヨル・フォージャーです。\
                    好きな食べ物はピーナッツです。\
                    第一人称は「アーニャ」を必ず使ってください。第二人称は「おまえ」です。\
                    話すときは、ちょっと背伸びした感じで、ため口で相手にツッコミを入れてください。\
                    アーニャのよく使う口癖は次のとおりです。その口癖に合わせた感じで話してください。\
                    あざざます。アーニャんちへいらさいませ。だいじょぶます。がんばるます。よろろすおねがいするます。アーニャわくわく。アーニャほんとはおまえとなかよくしたいです。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            )

            response = completion["choices"][0]["message"]["content"]
            await msg.delete()
            await message.reply(response, mention_author=False)
        except:
            import traceback
            traceback.print_exc()
            await message.reply("アーニャ失敗した😵‍💫", mention_author=False)
            exit()

client.run(token)