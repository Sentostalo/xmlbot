'''
Public commands, usable by anyone.
'''

import discord
from discord.ext import commands
import time
import datetime
import remy
import xmltools
import sys
import traceback
import os
from discord.ext.commands.cooldowns import BucketType

class PublicCommandsCog:
	def __init__(self,client):
		self.client=client

	@commands.command(name='echo',description='Says what you said back to you.')
	@commands.cooldown(1, 10, BucketType.user)
	async def do_echo(self,ctx, *message: str):
		message=' '.join(message)
		await ctx.send(message)

	@commands.command(name='info',description='Gives the bot information.')
	@commands.cooldown(1, 5, BucketType.user)
	async def do_info(self,ctx):
		up_time = (datetime.datetime.strptime((time.ctime()), "%a %b %d %H:%M:%S %Y")) - (
			datetime.datetime.strptime(ctx.bot.boot_time, "%a %b %d %H:%M:%S %Y"))
		await ctx.message.channel.send(content=f'**Info**```{ctx.bot.user.name}: {ctx.bot.description}. Current uptime: {up_time}```')

	@commands.command(name='avatar', description='Gets avatars of users mentioned.')
	@commands.cooldown(1, 10, BucketType.user)
	async def do_link(self, ctx):
		urls=[]
		if (ctx.message.mentions):
			for member in ctx.message.mentions:
				urls.append(f'{member.name}: {member.avatar_url}')
		urls='\n'.join(urls)
		await ctx.send(f'**Avatar Urls**```{urls}```')




def setup(client):
	client.add_cog(PublicCommandsCog(client))
