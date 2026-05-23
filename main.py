import discord
import asyncio

from config import DISCORD_TOKEN
from database.db import init_db
from services.ada_graph import run_ada_graph
from services.llm import classify_user_intent

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def format_popularity(score):
    if score >= 500:
        return "★★★★★ Extremely Popular"

    if score >= 300:
        return "★★★★☆ Very Popular"

    if score >= 150:
        return "★★★☆☆ Popular"

    if score >= 75:
        return "★★☆☆☆ Moderately Popular"

    return "★☆☆☆☆ Low Popularity"


@client.event
async def on_ready():
    init_db()
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
        intent = await asyncio.to_thread(classify_user_intent, user_message)

        if intent == "fetch_news":
            await message.channel.send("Fetching latest AI news...")
        elif intent == "answer_question":
            await message.channel.send("Thinking...")

        result = await asyncio.to_thread(run_ada_graph, user_message, intent)

        if intent == "fetch_news":
            news_items = result["news_items"]

            if not news_items:
                await message.channel.send("No AI news found right now.")
                return

            for index, item in enumerate(news_items, start=1):
                news_message = (
                    f"**{index}. {item['title']}**\n\n"
                    f"{item['summary']}\n\n"
                    f"Popularity: {format_popularity(item['popularity'])}\n"
                    f"Storage: {item['storage_status']}\n"
                    f"🔗 {item['url']}"
                )

                await message.channel.send(news_message)

        else:
            response = result["response"]

            if len(response) > 1900:
                response = response[:1900] + "..."

            await message.channel.send(response)

    except Exception as error:
        await message.channel.send(f"Something went wrong: {error}")


client.run(DISCORD_TOKEN)