import os
import discord
import openai

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
token = os.environ['DISCORD_TOKEN']  #Discordのトークン
openai.api_key = os.environ['OPENAI_API_KEY'] #APIキー
model_engine = "gpt-3.5-turbo"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global model_engine
    if message.author.bot:
        return
    if message.author == client.user:
        return

    if message.content.startswith('/gpt'):
        msg = await message.reply("生成中...", mention_author=False)
        try:
            prompt = message.content[4::]
            if not prompt:
                await msg.delete()
                await message.channel.send("質問内容がありません")
                return
            completion = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {
                    "role": "system",
                    "content": "日本語で返答してください。"
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
            await message.reply("エラーが発生しました", mention_author=False)

client.run(token)