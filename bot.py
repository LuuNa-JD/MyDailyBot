import discord
from discord.ext import tasks, commands
import schedule
import asyncio
import json
from config import TOKEN, CHANNEL_ID
from scraper import scrape_all_sites
from db import clear_db

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

def load_keywords():
    with open('keywords.json', 'r') as f:
        data = json.load(f)
    return data['keywords']

def save_keywords(keywords):
    with open('keywords.json', 'w') as f:
        json.dump({"keywords": keywords}, f)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help pour les commandes"))
    print(f'We have logged in as {bot.user}')
    send_articles.start()

@tasks.loop(hours=24)
async def send_articles():
    channel = bot.get_channel(CHANNEL_ID)
    articles = scrape_all_sites()
    for title, link in articles:
        await channel.send(f"{title}\n{link}")

@bot.command(name='now')
async def send_articles_now(ctx):
    articles = scrape_all_sites()
    await ctx.send(f"{len(articles)} articles trouvés.")
    for title, link in articles:
        await ctx.send(f"{title}\n{link}")

@bot.command(name='clearall')
async def clear_all(ctx):
    await ctx.channel.purge()

@bot.command(name='clear')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@bot.command(name='cleardb')
async def clear_db_command(ctx):
    clear_db()
    await ctx.send("Base de données nettoyée.")

@bot.command(name='addkeyword')
async def add_keyword(ctx, *, keyword):
    keywords = load_keywords()
    if keyword.lower() not in keywords:
        keywords.append(keyword.lower())
        save_keywords(keywords)
        await ctx.send(f"Le mot-clé '{keyword}' est ajouté.")
    else:
        await ctx.send(f"Le mot-clé'{keyword}' existe déjà.")

@bot.command(name='removekeyword')
async def remove_keyword(ctx, *, keyword):
    keywords = load_keywords()
    if keyword.lower() in keywords:
        keywords.remove(keyword.lower())
        save_keywords(keywords)
        await ctx.send(f"Le mot-clé '{keyword}' est supprimé.")
    else:
        await ctx.send(f"Le mot-clé '{keyword}' est introuvable.")

@bot.command(name='listkeywords')
async def list_keywords(ctx):
    keywords = load_keywords()
    await ctx.send("Mots-clés: " + ", ".join(keywords))

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="Commandes du Bot", description="Voici les commandes actives:", color=0x00ff00)
    embed.add_field(name="!now", value="Affiche les articles du moment.", inline=False)
    embed.add_field(name="!clearall", value="Supprime l'ENSEMBLE des messages du channel.", inline=False)
    embed.add_field(name="!clear [amount]", value="Supprime un nombre défini de message dans le channel (default: 5).", inline=False)
    embed.add_field(name="!cleardb", value="Nettoie la base de données comprenant l'historique des articles scrapés.", inline=False)
    embed.add_field(name="!addkeyword <keyword>", value="Ajoute un mot-clé à la liste.", inline=False)
    embed.add_field(name="!removekeyword <keyword>", value="Supprime un mot-clé de la liste.", inline=False)
    embed.add_field(name="!listkeywords", value="Affiche la liste des mots-clés en cours d'utilisation.", inline=False)
    await ctx.send(embed=embed)

async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def job():
    asyncio.create_task(send_articles())

schedule.every().day.at("07:00").do(job)

async def main():
    await bot.start(TOKEN)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run_schedule())
    loop.run_until_complete(main())
