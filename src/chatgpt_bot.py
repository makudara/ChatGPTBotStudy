import os
import discord
import openai

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
token = os.environ['DISCORD_TOKEN']  #Discordのトークン
openai.api_key = os.environ['OPENAI_API_KEY'] #APIキー
model_engine = "gpt-3.5-turbo-0301"

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
            await message.reply("エラーが発生しました", mention_author=False)

client.run(token)