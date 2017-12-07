import remy

import discord
from discord.ext import commands


class PinsCog:
	def __init__(self, client):
		self.client = client

	async def __local_check(self, ctx):
		return remy.dev_check(ctx)

	async def clone_channel(self, channel, name: str):
		perms = await self.create_overwrite_list(channel)
		new_channel = await channel.guild.create_text_channel(name, overwrites=perms, category=self.client.get_channel(channel.category_id))
		return new_channel

	async def create_overwrite_list(self, channel):
		overwrites = {}
		for role in channel.changed_roles:
			overwrites[role] = channel.overwrites_for(role)
		return overwrites

	@commands.command(name='clonepins', hidden=True)
	async def clone_pins(self, ctx):
		if ctx.message.channel_mentions:
			pin_channel = ctx.message.channel_mentions[0]
		else:
			pin_channel = await self.clone_channel(ctx.channel, 'cloned_pins')
		pin_list = await ctx.channel.pins()
		pin_list.reverse()
		webhook = await pin_channel.create_webhook(name='pin_cloner')
		pin_count = len(pin_list)
		for pin in pin_list:
			embed = discord.Embed(description=pin.content)
			if pin.attachments:
				data = pin.attachments[0]
				if data.height and data.width:
					embed.set_image(url=data.url)
			embed.set_author(name=pin.author.name, icon_url=pin.author.avatar_url_as(format='png'))
			await webhook.send(embed=embed, avatar_url=ctx.guild.icon_url, username=ctx.guild.name)
			await pin.upin()
		await webhook.delete()
		await ctx.send(f'**Clone Pins**```{pin_count} pins cloned to {pin_channel}.```')


def setup(client):
	client.add_cog(PinsCog(client))
