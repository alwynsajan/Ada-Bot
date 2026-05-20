import discord

from config import DISCORD_TOKEN
from services.ada_graph import run_ada_graph
from services.llm import classify_user_intent

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user not in message.mentions:
        return

    user_message = message.content.replace(f"<@{client.user.id}>", "").strip()
    user_message = user_message.replace(f"<@!{client.user.id}>", "").strip()

    if not user_message:
        await message.channel.send("Hi! Ask me for the latest AI news.")
        return

    try:
        intent = classify_user_intent(user_message)

        if intent == "fetch_news":
            await message.channel.send("Fetching latest AI news...")
        else:
            await message.channel.send("Thinking...")

        result = run_ada_graph(user_message, intent)

        if intent == "fetch_news":
            news_items = result["news_items"]

            if not news_items:
                await message.channel.send("No AI news found right now.")
                return

            for index, item in enumerate(news_items, start=1):
                news_message = (
                    f"**{index}. {item['title']}**\n\n"
                    f"{item['summary']}\n\n"
                    f"Score: {item['score']}\n"
                    f"🔗 {item['url']}"
                )

                await message.channel.send(news_message)

        else:
            await message.channel.send(result["response"])

    except Exception as error:
        await message.channel.send(f"Something went wrong: {error}")


client.run(DISCORD_TOKEN)