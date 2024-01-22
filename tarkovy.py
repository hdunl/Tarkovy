import discord
from discord.ext import commands
import requests
import re

search_results = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

BOT_TOKEN = 'YOUR_BOT_TOKEN'

def run_query(query, variables=None):
    headers = {"Content-Type": "application/json"}
    data = {'query': query}
    if variables:
        data['variables'] = variables

    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

@bot.command()
async def price(ctx, *, item_name: str):
    cleaned_item_name = re.sub(r'\W+', '', item_name)
    if len(cleaned_item_name) < 3:
        await ctx.send("Please provide at least 3 alphanumeric characters for the search.")
        return

    query = """
    {{
        items(name: "{0}") {{
            id
            name
            basePrice
            wikiLink
            iconLink
            sellFor {{
                price
                currency
                priceRUB
                source
            }}
        }}
    }}
    """.format(item_name)

    try:
        result = run_query(query)
        items = result['data']['items']

        if len(items) == 0:
            await ctx.send("No items found with that name.")
        elif len(items) == 1:
            await send_item_details(ctx, items[0])
        else:
            search_results[ctx.author.id] = items
            embed = discord.Embed(title="Multiple items found", description="Please type the number of the item you want details for:", color=0x5CDBF0)
            for idx, item in enumerate(items, 1):
                embed.add_field(name=f"{idx}: {item['name']}", value=f"ID: {item['id']}", inline=False)
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def quests(ctx, *, item_name: str):
    cleaned_item_name = re.sub(r'\W+', '', item_name)
    if len(cleaned_item_name) < 3:
        await ctx.send("Please provide at least 3 alphanumeric characters for the search.")
        return

    query = """
    query ($itemName: String!) {
        items(name: $itemName) {
            name
            usedInTasks {
                id
                name
                trader {
                    name
                }
                map {
                    name
                }
                experience
                wikiLink
                minPlayerLevel
                objectives {
                    type
                }
                restartable
                kappaRequired
                lightkeeperRequired
            }
        }
    }
    """

    variables = {
        "itemName": cleaned_item_name
    }

    try:
        result = run_query(query, variables)
        items = result.get('data', {}).get('items', [])

        if not items:
            await ctx.send(f"No items found with the name '{item_name}'.")
        else:
            if not items[0].get('usedInTasks'):
                await ctx.send(f"No tasks found related to '{item_name}'.")
            else:
                await send_related_tasks(ctx, items[0])

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

async def send_related_tasks(ctx, item):
    embed = discord.Embed(title=f"Related Tasks for {item['name']}", color=0x5CDBF0)
    tasks = item['usedInTasks']

    if not tasks:
        await ctx.send(f"No tasks found related to '{item['name']}'.")
        return

    reactions = []

    for idx, task in enumerate(tasks):
        task_info = (
            f"Trader: {task['trader']['name']}\n"
            f"Map: {task['map']['name'] if task['map'] else 'N/A'}\n"
            f"Experience Reward: {task['experience']} EXP\n"
            f"Minimum Player Level: {task['minPlayerLevel']}\n"
            f"Objectives: {' • '.join([obj['type'] for obj in task['objectives']])}\n"
            f"Restartable: {task['restartable']}\n"
            f"Kappa Required: {task['kappaRequired']}\n"
            f"Lightkeeper Required: {task['lightkeeperRequired']}"
        )

        if task['wikiLink']:
            task_info += f"\nWiki Link: [Link]({task['wikiLink']})"

        embed.add_field(name=f"{idx + 1}. {task['name']}", value=task_info, inline=False)
        reactions.append(str(idx + 1))

    message = await ctx.send(embed=embed)

    for reaction in reactions:
        await message.add_reaction(f"{reaction}\u20e3")
    
    search_results[message.id] = tasks

async def send_item_details(ctx, item):
    embed = discord.Embed(title=item['name'], color=0x5CDBF0)
    embed.add_field(name="ID", value=item['id'], inline=True)
    embed.add_field(name="Price", value=f"{item['basePrice']:,}₽", inline=True)

    if item['sellFor']:
        trader_prices = '\n'.join([f"{sf['source'].capitalize()}: {sf['priceRUB']:,}₽ ({sf['price']} {sf['currency']})" for sf in item['sellFor']])
        embed.add_field(name="Trader Prices", value=trader_prices, inline=False)

    if 'wikiLink' in item and item['wikiLink']:
        embed.add_field(name="Wiki Link", value=f"[Link]({item['wikiLink']})", inline=False)
    if 'iconLink' in item and item['iconLink']:
        embed.set_thumbnail(url=item['iconLink'])
    await ctx.send(embed=embed)

@bot.command()
async def ammo(ctx, *, ammo_name: str):
    query = """
    query GetAllAmmoDetails {
        ammo {
            item {
                name
            }
            weight
            caliber
            stackMaxSize
            tracer
            tracerColor
            ammoType
            projectileCount
            damage
            armorDamage
            fragmentationChance
            ricochetChance
            penetrationChance
            penetrationPower
            accuracyModifier
            recoilModifier
            initialSpeed
            lightBleedModifier
            heavyBleedModifier
            staminaBurnPerDamage
        }
    }
    """

    try:
        result = run_query(query)
        ammo_details = [a for a in result['data']['ammo'] if ammo_name.lower() in a['item']['name'].lower()]

        if not ammo_details:
            await ctx.send(f"No ammunition found with the name '{ammo_name}'.")
        else:
            await send_ammo_details(ctx, ammo_details[0])

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

async def send_ammo_details(ctx, ammo):
    embed = discord.Embed(title=ammo['item']['name'], color=0x5CDBF0)
    embed.add_field(name="Weight", value=f"{ammo['weight']} kg", inline=True)
    embed.add_field(name="Caliber", value=ammo['caliber'], inline=True)
    embed.add_field(name="Stack Max Size", value=ammo['stackMaxSize'], inline=True)
    embed.add_field(name="Tracer", value="Yes" if ammo['tracer'] else "No", inline=True)
    embed.add_field(name="Tracer Color", value=ammo['tracerColor'] if ammo['tracerColor'] else "N/A", inline=True)
    embed.add_field(name="Ammo Type", value=ammo['ammoType'], inline=True)
    embed.add_field(name="Projectile Count", value=ammo['projectileCount'] if ammo['projectileCount'] else "N/A", inline=True)
    embed.add_field(name="Damage", value=ammo['damage'], inline=True)
    embed.add_field(name="Armor Damage", value=ammo['armorDamage'], inline=True)
    embed.add_field(name="Fragmentation Chance", value=f"{ammo['fragmentationChance'] * 100}%", inline=True)
    embed.add_field(name="Ricochet Chance", value=f"{ammo['ricochetChance'] * 100}%", inline=True)
    embed.add_field(name="Penetration Chance", value=f"{ammo['penetrationChance'] * 100}%", inline=True)
    embed.add_field(name="Penetration Power", value=ammo['penetrationPower'], inline=True)
    embed.add_field(name="Accuracy Modifier", value=ammo['accuracyModifier'], inline=True)
    embed.add_field(name="Recoil Modifier", value=ammo['recoilModifier'], inline=True)
    embed.add_field(name="Initial Speed", value=f"{ammo['initialSpeed']} m/s", inline=True)
    embed.add_field(name="Light Bleed Modifier", value=ammo['lightBleedModifier'], inline=True)
    embed.add_field(name="Heavy Bleed Modifier", value=ammo['heavyBleedModifier'], inline=True)
    embed.add_field(name="Stamina Burn Per Damage", value=ammo['staminaBurnPerDamage'], inline=True)

    await ctx.send(embed=embed)

invalid_attempts = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    try:
        if message.author.id in search_results:
            try:
                choice = int(message.content.strip())
            except ValueError:
                choice = -1

            user_search = search_results[message.author.id]

            if 1 <= choice <= len(user_search['items']):
                selected_item = user_search['items'][choice - 1]

                if user_search['type'] == 'price':
                    await send_item_details(message.channel, selected_item)
                elif user_search['type'] == 'marketTrends':
                    await show_market_trends(message.channel, selected_item['id'])
                del search_results[message.author.id]
            else:
                await message.channel.send("Invalid selection. Please choose a valid number.")
                if message.author.id not in invalid_attempts:
                    invalid_attempts[message.author.id] = 0
                invalid_attempts[message.author.id] += 1

                if invalid_attempts[message.author.id] >= 2:
                    del search_results[message.author.id]
                    await message.channel.send("Search canceled due to repeated invalid selections.")
    except ValueError:
        if message.author.id in search_results:
            await message.channel.send("Invalid selection. Please choose a valid number.")
            if message.author.id not in invalid_attempts:
                invalid_attempts[message.author.id] = 0
            invalid_attempts[message.author.id] += 1

            if invalid_attempts[message.author.id] >= 2:
                del search_results[message.author.id]
                await message.channel.send("Search canceled due to repeated invalid selections.")

bot.run(BOT_TOKEN)
