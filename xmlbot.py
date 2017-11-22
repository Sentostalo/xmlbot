import discord
from discord.ext import commands
import time
import datetime
import remy
import sys
import traceback
import os

valid_bot, bot_data = remy.get_bot('xml')


def get_prefixes(discord_client, message):
	prefixes = [bot_data['prefix'], '?']
	return commands.when_mentioned_or(*prefixes)(discord_client, message)


client = commands.Bot(command_prefix=get_prefixes, description=bot_data['description'], game=discord.Game(name='Setup'))


async def setup():
	if not hasattr(client, 'boot_time'):
		client.boot_time = (time.ctime())
	if not hasattr(client, 'primary_channel'):
		client.primary_channel = client.get_channel(bot_data['commands'])
	if not hasattr(client, 'events_channel') and bot_data['events']:  # this is for xmlbot only
		client.events_channel = client.get_channel(bot_data['events'])
	if not hasattr(client, 'logs_channel'):
		client.logs_channel = client.get_channel(bot_data['logs'])
	if not hasattr(client, 'primary_guild'):
		client.primary_guild = client.primary_channel.guild
	if not hasattr(client, 'bot_data'):
		client.bot_data = bot_data


def main():
	if valid_bot:
		client.run(bot_data['token'], bot=bot_data['is_bot'])
	else:
		print('Invalid bot specified.')
		raise SystemExit()


@client.event
async def on_ready():
	started = False
	if not started:
		await setup()
		if __name__ == '__main__':
			loadedcogs = []
			failedcogs = []
			for extension in bot_data['default_ext']:
				try:
					client.load_extension(extension)
					print(f'Extension {extension} loaded.')
					loadedcogs.append(extension)
				except Exception:
					print(f'Failed to load extension {extension}.', file=sys.stderr)
					traceback.print_exc()
					failedcogs.append(extension)
			loadedcogs = ' '.join(loadedcogs)
			await client.cogs['DevCommandsCog'].add_log(f'Connection established, {client.user.name} online. Primary channel is #{client.primary_channel} of {client.primary_guild}.\nCogs loaded: {loadedcogs}')
			if len(failedcogs) != 0:
				failedcogs = ' '.join(failedcogs)
				await client.cogs['DevCommandsCog'].add_log(f'The following cogs failed to load: {failedcogs}')
		await client.change_presence(game=discord.Game(name='Testing'))
		started=True


main()
