import datetime
import os
import remy
import sys
import time
import traceback
import xmltools

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class PublicCommandsCog:
	def __init__(self, client):
		self.client = client

	async def __local_check(self, ctx):
		return not isinstance(ctx.channel, discord.DMChannel)

	@commands.command(name='info', description='Gives the bot information.')
	@commands.cooldown(1, 5, BucketType.user)
	async def do_info(self, ctx):
		up_time = (datetime.datetime.strptime((time.ctime()), "%a %b %d %H:%M:%S %Y")) - (
			datetime.datetime.strptime(ctx.bot.boot_time, "%a %b %d %H:%M:%S %Y"))
		await ctx.message.channel.send(
			content=f'**Info**```{ctx.bot.user.name}: {ctx.bot.description}. Current uptime: {up_time}```')

	@commands.command(name='avatar', description='Gets avatars of users mentioned.')
	@commands.cooldown(1, 10, BucketType.user)
	async def do_link(self, ctx):
		urls = []
		if ctx.message.mentions:
			for member in ctx.message.mentions:
				urls.append(f'{member.name}: {member.avatar_url}')
		urls = '\n'.join(urls)
		if urls:
			await ctx.send(f'**Avatar Urls**```{urls}```')
		else:
			await ctx.send(f'**Avatar Urls**```No users specified.```')


def setup(client):
	client.add_cog(PublicCommandsCog(client))
