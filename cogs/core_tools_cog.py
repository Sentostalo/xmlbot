import datetime
import os
import remy
import sys
import time
import traceback

import discord
from discord.ext import commands


class CoreCog:
	def __init__(self, client):
		self.client = client

	async def __local_check(self, ctx):
		return remy.dev_check(ctx)

	def clean_log_check(self, msg):
		return not msg.author == self.client.user

	def get_cogs(self):
		cogs = []
		files = os.listdir(os.path.dirname(os.path.realpath(__file__)))
		for file in files:
			if file.endswith('.py'):
				cog_name = file.replace('.py', '')
				cogs.append(f'cogs.{cog_name}')
		return cogs

	def find_cog(self, to_find):
		coglist = self.get_cogs()
		for cog in coglist:
			if to_find in cog:
				return cog

	async def add_log(self, info):
		info = f'[{time.ctime()}] {info}'
		await self.client.logs_channel.send(info)
		print(info)


	@commands.command(name='dev', hidden=True)
	async def do_test(self, ctx):
		pass

	@commands.command(name='echo', description='Says what you said back to you.')
	async def do_echo(self, ctx, *message: str):
		message = ' '.join(message)
		await ctx.send(message)

	@commands.command(name='exit', hidden=True)
	async def exit(self, ctx):
		exit_time = (time.ctime())
		up_time = (datetime.datetime.strptime(exit_time, "%a %b %d %H:%M:%S %Y")) - (
			datetime.datetime.strptime(ctx.bot.boot_time, "%a %b %d %H:%M:%S %Y"))
		try:
			await ctx.message.delete()
			await self.add_log(
				f'{ctx.author.nick} ({str(ctx.author)}) commanded {ctx.bot.user.name} exit from Channel #{ctx.message.channel.name} in {ctx.message.guild}. Total uptime: {up_time}\n\u200B')
		except Exception as e:
			print(f'Error in logout log output: {e}')
		await ctx.bot.logout()

	@commands.command(name='clean', hidden=True)
	async def cleanlog(self, ctx):
		cleared = await ctx.channel.purge(limit=100, check=self.clean_log_check)
		await ctx.message.channel.send(
			content=f'**Clean log**```{len(cleared)} non-log messages found in my log channel and cleared.```',
			delete_after=2)

	@commands.command(name='devrole', hidden=True)
	async def give_dev(self, ctx):
		given = []
		for my_guilds in ctx.bot.guilds:
			to_give = my_guilds.get_member_named(str(ctx.author))
			if to_give is not None and ctx.message.guild != my_guilds:
				try:
					dev_role = discord.utils.get(my_guilds.roles, name='Dev')
					given.append(
						f'{ctx.author} found in dev server {my_guilds}, {dev_role.name} role given.')
					await to_give.add_roles(dev_role)
				except (TypeError, discord.errors.Forbidden):
					given.append(
						f'{my_guilds} is either not a dev server or I do not have the permissions to give you the dev role.')
			elif ctx.message.guild == my_guilds:
				given.append(f'Cannot give dev role in current server {my_guilds}.')
			else:
				given.append(f'{ctx.author} not found in dev server {my_guilds}')
		given = '\n'.join(given)
		await ctx.message.channel.send(f'**Dev Role**```{given}```')

	@commands.command(name='load', hidden=True)
	async def cog_load(self, ctx, *, cog: str):
		cog = self.find_cog(cog)
		if cog is not None:
			try:
				ctx.bot.load_extension(cog)
				await ctx.send(f'**Load**```Successfully loaded Extension [{cog}]```')
			except (SyntaxError, ModuleNotFoundError, AttributeError) as e:
				await ctx.send(f'**Load**```Could not load cog. Error: {type(e).__name__} - {e}```')
		else:
			await ctx.send(f'**Load**```Cog does not exist.```')


	@commands.command(name='unload', hidden=True)
	async def cog_unload(self, ctx, *, cog: str):
		cog = self.find_cog(cog)
		core_cog = str(os.path.basename(__file__)).replace('.py', '')
		if cog == f'cogs.{core_cog}':
			await ctx.send(f'**Unload**```You cannot unload {cog}.```')
		elif cog is not None:
			try:
				ctx.bot.unload_extension(cog)
				await ctx.send(f'**Unload**```Successfully unloaded Extension [{cog}]```')
			except (SyntaxError, ModuleNotFoundError, AttributeError) as e:
				await ctx.send(f'**Unload**```Could not load cog. Error: {type(e).__name__} - {e}```')
		else:
			await ctx.send(f'**Unload**```Cog does not exist.```')


	@commands.command(name='reload', aliases=['rel'], hidden=True)
	async def cog_reload(self, ctx, *, cog: str):
		cog = self.find_cog(cog)
		core_cog = str(os.path.basename(__file__)).replace('.py', '')
		if cog == f'cogs.{core_cog}':
			await ctx.send(f'**Reload**```You cannot reload {cog}.```')
		elif cog is not None:
			try:
				ctx.bot.unload_extension(cog)
				reload_msg = await ctx.send(f'**Reload**```Unloading [{cog}]...```')
				ctx.bot.load_extension(cog)
				await reload_msg.edit(content=f'**Reload**```Loading [{cog}]...```')
				await reload_msg.edit(content=f'**Reload**```Successfully reloaded Extension [{cog}]```')
			except Exception as e:
				await reload_msg.edit(content=f'**Reload**```Could not reload cog. Error: {type(e).__name__} - {e}```')
		else:
			await ctx.send(f'**Reload**```Cog does not exist.```')


	@commands.command(name='loadedcogs', aliases=['loaded'], hidden=True)
	async def show_cogs(self, ctx):
		loadedcogs = []
		for i in ctx.bot.cogs.values():
			loadedcogs.append(str(i.__module__))
		loadedcogs = '\n'.join(loadedcogs)
		await ctx.send(f'**Loaded cogs**```\n{loadedcogs}```')

	@commands.command(name='allcogs', aliases=['cogs'], hidden=True)
	async def all_cogs(self, ctx):
		allcogs = self.get_cogs()
		allcogs = '\n'.join(allcogs)
		await ctx.send(f'**Available cogs**```\n{allcogs}```')

	@commands.command(name='clear', hidden=True)
	async def do_clear(self, ctx, amount: int):
		cleared = await ctx.message.channel.purge(limit=amount)
		await ctx.message.channel.send(content=f'{len(cleared)} messages cleared.', delete_after=2)


def setup(client):
	client.add_cog(CoreCog(client))
