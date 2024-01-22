# Tarkovy Discord Bot for Escape from Tarkov

## Introduction

This is a Discord bot that provides information about items, quests, and ammunition in the game Escape from Tarkov. The bot fetches data from the Tarkov.dev API to provide details about in-game items, quests, and ammunition.

## Features

- **Price Command**: Get information about the price, sell prices from traders, and other details of in-game items.

- **Quests Command**: Find quests related to specific in-game items. The bot provides information about the quests, including traders, maps, experience rewards, objectives, and more.

- **Ammo Command**: Retrieve information about different types of ammunition in the game. This includes details like weight, caliber, stack size, damage, armor damage, and more.

## How to Use

1. Clone this repository to your local machine.

2. Install the required Python packages using `pip install discord.py requests'.

3. Replace `'YOUR_BOT_TOKEN'` in the code with your Discord bot's token.

4. Run the bot using `python bot.py`.

## Commands

- `!price [item_name]`: Get price information and details about an item.

- `!quests [item_name]`: Find quests related to a specific item.

- `!ammo [ammo_name]`: Retrieve information about different types of ammunition.

## Setup

To use this bot, you need to set up your own Discord bot and obtain its token. Instructions on how to set up a Discord bot can be found in the [Discord Developer Portal](https://discord.com/developers/applications).

## Dependencies

- Discord.py: A Python library for interacting with the Discord API.

- Requests: A Python library for making HTTP requests.

## API Used

This bot uses the [Tarkov.dev API](https://api.tarkov.dev/graphql) to fetch in-game data. Full credit for all provided data goes to them.
