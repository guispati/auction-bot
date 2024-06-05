import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

items = {
    '⚔️': ('Sigil Espada Divina', 1),
    '🛡️': ('Sigil Proteção', 4),
    '🌟': ('Pena Luz/Sombra 4x', 3),
    '✨': ('Pena Luz/Sombra 1x', 2),
	'🌀': ('Pena Espaço/Tempo 4x', 2),
    '💫': ('Pena Espaço/Tempo 1x', 3),
    '🔥': ('Baú Pet Senhor do Fogo', 2),
    '🃏': ('Carta MVP', 3),
    '🧩': ('Carta MVP (Fragmento)', 5),
}

user_choices = {item: [] for item, _ in items.values()}
auction_message = None

async def create_auction_embed():
    embed = discord.Embed(
		title="Leilão OnlyFans",
		description="**Limitado a 1 item de cada por pessoa**\n"
					"Quando estiver faltando 5 minutos para o fim do leilão o bid ficará liberado para todos (quem pegar primeiro)\n"
					"No jogo, dê bid no item que aparecer na posição que o bot colocar o seu nick (seguindo a referência fixada no canal)\n"
					"**POR FAVOR, NUNCA DÊ BID EM CIMA DO COLEGUINHA!**\n\n"
					"Reaja com o emoji correspondente para bidar em um item:\n",
		color=discord.Color.blue()
	)
    embed.set_footer(text="Created by Spati v1.0")

    for emote, (item, amount) in items.items():
        users = '\n'.join([f"{i+1}. {user}" for i, user in enumerate(user_choices[item])]) if user_choices[item] else 'Ninguém'
        remaining = amount - len(user_choices[item])
        embed.add_field(
            name=f"{emote}: {item} (Disponível: {remaining})", 
            value=users,
            inline=False
        )

    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='start_auction')
async def start_auction(ctx):
    global auction_message
    
    auction_message = await ctx.send(embed=await create_auction_embed())
    
    for emote in items.keys():
        await auction_message.add_reaction(emote)

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

    chosen_item, amount = items[reaction.emoji]

    if len(user_choices[chosen_item]) >= amount:
        await user.send(f"Desculpe, o item {chosen_item} não está mais disponível no leilão.")
        await reaction.remove(user)
        return

    user_choices[chosen_item].append(user.name)
    await update_auction_message()

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if reaction.message.id != auction_message.id:
        return

    if reaction.emoji not in items:
        return

    chosen_item, _ = items[reaction.emoji]

    if user.name in user_choices[chosen_item]:
        user_choices[chosen_item].remove(user.name)
        await update_auction_message()

bot.run(discord_token)
