import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

items = {
    '⚔️': 'Sigil Espada Divina',
    '🛡️': 'Sigil Proteção',
    '👑': 'King Statue Chest',
    '🔥': 'Baú Pet Senhor do Fogo',
    '🌟': 'Pena Luz/Sombra (L)',
    '✨': 'Pena Luz/Sombra',
    '🌀': 'Pena Espaço/Tempo (L)',
    '💫': 'Pena Espaço/Tempo',
}

user_choices = {item: [] for item in items.values()}
auction_message = None

async def create_auction_embed():
    current_date = datetime.now().strftime("%Y-%m-%d")
    embed = discord.Embed(
        title=f"Leilão OnlyFans - {current_date}",
        description="**Limitado a 1 item de cada por pessoa**\n"
                    "Quando estiver faltando 5 minutos para o fim do leilão o bid ficará liberado para todos (quem pegar primeiro)\n"
                    "No jogo, dê bid no item que aparecer na posição que o bot colocar o seu nick (seguindo a referência fixada no canal)\n"
                    "**POR FAVOR, NUNCA DÊ BID EM CIMA DO COLEGUINHA!**\n\n"
                    "Reaja com o emoji correspondente para bidar em um item:\n",
        color=discord.Color.blue()
    )
    for emote, item in items.items():
        users = '\n'.join([f"{i+1}. {user.display_name}" for i, user in enumerate(user_choices[item])]) if user_choices[item] else 'Ninguém'
        embed.add_field(
            name=f"{emote}: {item}", 
            value=users,
            inline=False
        )

    embed.set_footer(text="Created by Spati v1.0")
    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='start_auction')
@commands.has_permissions(administrator=True)
async def start_auction(ctx):
    global auction_message
    
    auction_message = await ctx.send(embed=await create_auction_embed())
    
    for emote in items.keys():
        await auction_message.add_reaction(emote)
    
    await ctx.message.delete()
    
    thread = await auction_message.create_thread(
	    name=f"Utilize este espaço para discussões necessárias sobre este leilão",
	)

async def update_auction_message():
    global auction_message
    if auction_message is None:
        return

    await auction_message.edit(embed=await create_auction_embed())

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.id != auction_message.id:
        return

    if reaction.emoji not in items:
        return

    guild = reaction.message.guild
    member = guild.get_member(user.id)

    chosen_item = items[reaction.emoji]

    user_choices[chosen_item].append(member)
    await update_auction_message()

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if reaction.message.id != auction_message.id:
        return

    if reaction.emoji not in items:
        return

    guild = reaction.message.guild
    member = guild.get_member(user.id)

    chosen_item = items[reaction.emoji]

    if member in user_choices[chosen_item]:
        user_choices[chosen_item].remove(member)
        await update_auction_message()

bot.run(discord_token)
