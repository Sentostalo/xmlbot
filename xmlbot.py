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
	prefixes = [bot_data['prefix'], '?', '>']
	return commands.when_mentioned_or(*prefixes)(discord_client, message)


class XMLBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	async def setup(self):
		if not hasattr(self, 'boot_time'):
			self.boot_time = (time.ctime())
		if not hasattr(self, 'primary_channel'):
			self.primary_channel = self.get_channel(bot_data['commands'])
		if not hasattr(self, 'events_channel') and 'events' in bot_data:  # this is for xmlbot only
			self.events_channel = self.get_channel(bot_data['events'])
		if not hasattr(self, 'logs_channel'):
			self.logs_channel = self.get_channel(bot_data['logs'])
		if not hasattr(self, 'primary_guild'):
			self.primary_guild = self.primary_channel.guild
		if not hasattr(self, 'bot_data'):
			self.bot_data = bot_data


	async def on_ready(self):
		started = False
		if not started:
			await self.setup()
			if __name__ == '__main__':
				loadedcogs = []
				failedcogs = []
				for extension in bot_data['default_ext']:
					try:
						self.load_extension(extension)
						print(f'Extension {extension} loaded.')
						loadedcogs.append(extension)
					except (SyntaxError, ModuleNotFoundError, NameError):
						print(f'Failed to load extension {extension}.', file=sys.stderr)
						if extension == 'cogs.core_cog':
							print(f'Critical error, Core cog failed to load. Bot cannot run without this functionality.', file=sys.stderr)
							raise SystemExit
						traceback.print_exc()
						failedcogs.append(extension)
				loadedcogs = ' '.join(loadedcogs)
				await self.cogs['CoreCog'].add_log(f'Connection established, {self.user.name} online. Primary channel is #{self.primary_channel} of {self.primary_guild}.\nCogs loaded: {loadedcogs}')
				if len(failedcogs) != 0:
					failedcogs = ' '.join(failedcogs)
					await self.cogs['CoreCog'].add_log(f'The following cogs failed to load: {failedcogs}')
			await client.change_presence(game=discord.Game(name='Testing'))
			started=True

client=XMLBot(command_prefix=get_prefixes, description=bot_data['description'], game=discord.Game(name='Setup'))

def main():
	if valid_bot:
		client.run(bot_data['token'], bot=bot_data['is_bot'])
	else:
		print('Invalid bot specified.')
		raise SystemExit()


main()
