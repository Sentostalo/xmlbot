import _pickle as pickle
import asyncio
import datetime
import forumscraping
import functools
import os
import remy
import sys
import time
import traceback
import xmltools

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class XMLToolsCog:
	def __init__(self, client):
		self.client = client
		if self.client.events_channel and not hasattr(self, 'events_channel'):
			self.events_channel = self.client.events_channel
		elif not hasattr(self, 'events_channel'):
			self.events_channel = self.client.primary_channel
		self.background_task = self.client.loop.create_task(self.my_background_task())

	def __unload(self):
		self.background_task.cancel()

	async def __local_check(self, ctx):
		return not isinstance(ctx.channel, discord.DMChannel)

	def setup_timing(self):
		n = datetime.datetime.now() + datetime.timedelta(hours=1)
		new_date = datetime.datetime(year=n.year, month=n.month, day=n.day, hour=n.hour)
		if new_date.hour % 2 == 0:  # if the next hour is even
			next_update = new_date
		else:  # if the next hour is odd
			next_update = new_date + datetime.timedelta(hours=1)
		wait_time = next_update - datetime.datetime.now()
		return wait_time.total_seconds()

	def compare_reviews(self, new_reviews):
		changed_reviews = {}
		try:
			with open('reviews.txt', 'rb') as file:
				old_reviews = (pickle.load(file))
				for category in new_reviews:
					if not (old_reviews[category] == new_reviews[category]):
						changed_reviews[category] = new_reviews[category]
			return changed_reviews
		except (FileNotFoundError, pickle.UnpicklingError):
			return

	async def sub_role(self, ctx, category, add):
		category = category.strip().upper()
		role = (discord.utils.get(ctx.guild.roles, name=category))
		if role:
			if add:  # if the doesnt have the role
				if role not in ctx.author.roles:  # if they dont already have role
					await ctx.author.add_roles(role)
					await ctx.send(f'**Sub**```Successfully added subscription to {category}!```')
				else:  # if they have the role already
					await ctx.send(f'**Sub**```You\'re already subscribed to {category}.```')
			elif not add:  # if to remove
				if role in ctx.author.roles:  # if they have the role
					await ctx.author.remove_roles(role)
					await ctx.send(f'**Sub**```Successfully removed subscription to {category}!```')
				else:  # if they don't have the role
					await ctx.send(f'**Sub**```You\'re not subscribed to {category}.```')
		else:  # if the role doesn't exist, or it's not a subscribable guild
			raise AttributeError

	async def announce_new_reviews(self, categories):
		for channel_id in (382643448114708480, 361706712513904640):
			announcement = []
			mentionroles = []
			channel = (self.client.get_channel(channel_id))
			for perm in categories:
				role = (discord.utils.get(channel.guild.roles, name=perm))
				await role.edit(mentionable=True)
				mentionroles.append(role)
				emote = (discord.utils.get(channel.guild.emojis, name=perm))
				announcement.append(f'{role.mention} has a new review: {categories[perm]} {str(emote)} ')
			announcement = '\n'.join(announcement)
			await channel.send(announcement)
			for role in mentionroles:
				await role.edit(mentionable=False)

	async def fetch_reviews(self, client, first, automated):
		if automated:  # if this is an automated fetch called by the background task
			if first:  # if this is on startup
				await self.events_channel.send('Scraping cog initialised. Getting latest reviews and Mapcrew list.')
				reviews = await forumscraping.get_reviews_via_redir(client)

				# fetching mapcrew on startup
				try:
					mapcrew_page = await forumscraping.get_html(client, 'https://atelier801.com/staff-ajax?role=16')
					func_get_mapcrew = functools.partial(forumscraping.get_mapcrew, mapcrew_page)
					mapcrew_list = await self.client.loop.run_in_executor(None, func_get_mapcrew)
					if len(mapcrew_list) > 5:  # if the fetch ran successfully
						with open('mapcrew.txt', 'wb') as file:  # save the mapcrew list
							pickle.dump(mapcrew_list, file)
						await self.events_channel.send('Mapcrew successfully fetched and saved.')
					else:
						await self.events_channel.send('Mapcrew list failed to fetch. Reverted to previously saved edition.')
				except Exception as e:
					print(e)
			else:  # if it has been two hours since last fetch
				await self.events_channel.send('2 hours since last fetch. Getting latest reviews.')
				reviews = await forumscraping.get_reviews_via_redir(client)
			next_fetch_time = (await self.client.loop.run_in_executor(None, self.setup_timing))  # get the next fetch time, which at any given time is the time until the next even hour
			d = (datetime.timedelta(seconds=next_fetch_time))
			await self.events_channel.send(
				f'Reviews successfully fetched. Next review fetching scheduled in {datetime.timedelta(days=d.days,seconds=d.seconds)}')

		else:  # if this is a user commanded fetch
			await self.events_channel.send('Fetching reviews due to user command.')
			reviews = await forumscraping.get_reviews_via_redir(client)
		changed = self.compare_reviews(reviews)  # compare the new and old reviews
		if changed:
			links = []
			for cat, url in changed.items():
				links.append(f'{cat}: {url}')
			links = ', '.join(links)
			await self.events_channel.send(f'There are new reviews: {links}')
			await self.announce_new_reviews(changed)
		else:
			await self.events_channel.send('No new reviews since last checked.')

		with open('reviews.txt', 'wb') as file:  # save the newest sets of reviews
			pickle.dump(reviews, file)

		await self.events_channel.send('Reviews successfully saved.')

		if automated:  # if this is an automated fetch, return the next scheduled fetching time
			return next_fetch_time

	async def my_background_task(self):
		first_fetch = True
		await self.client.wait_until_ready()
		while not self.client.is_closed():
			with aiohttp.ClientSession() as client:
				next_fetch = await self.fetch_reviews(client, first_fetch, True)
				first_fetch = False
				await asyncio.sleep(next_fetch)


	@commands.check(remy.dev_check)
	@commands.command(name='get', hidden=True)
	async def user_get_reviews(self, ctx):
		with aiohttp.ClientSession() as client:
			await self.fetch_reviews(client, False, False)

	@commands.command(name='reviews', aliases=['review'], description='Gets the reviews. If a perm category is specified, gets only that review.')
	@commands.cooldown(1, 10, BucketType.user)
	async def show_reviews(self, ctx, *category):
		try:
			with open('reviews.txt', 'rb') as file:
				reviews = (pickle.load(file))
			if category:
				category = ' '.join(category)
				category_name = category.strip().upper().replace(' ', '')
				if category_name in reviews:
					await ctx.send(
						f'**Review for {category_name}** *(Fetched every two hours)*```\n{reviews[category_name]}```')
				else:
					await ctx.send(f'**Reviews** ```\nCategory {category} not found.```')
			else:
				links = []
				for cat, url in reviews.items():
					links.append(f'{cat}: {url}')
				links = '\n'.join(links)
				await ctx.send(f'**Reviews** *(Fetched every two hours)*```\n{links}```')
		except (FileNotFoundError, pickle.UnpicklingError):
			await ctx.send('**Reviews**```An error occured in fetching the reviews list.```')

	@commands.command(name='mapcrew', aliases=['mc'], description='Returns a list of the current Mapcrew.')
	@commands.cooldown(1, 10, BucketType.user)
	async def show_mapcrew(self, ctx):
		try:
			with open('mapcrew.txt', 'rb') as file:
				mapcrew_list = (pickle.load(file))
			mapcrew_list = '\n'.join(mapcrew_list)
			await ctx.send(f'**Mapcrew**```\n{mapcrew_list}```')
		except (FileNotFoundError, pickle.UnpicklingError):
			await ctx.send('**Mapcrew**```An error occured in fetching the Mapcrew list.```')

	@commands.cooldown(1, 5, BucketType.user)
	@commands.command(name='sub', description='Subscribes you to recieve notifications about a perm category. Example usage: [x!sub P5]')
	async def do_sub(self, ctx, category):
		try:
			await self.sub_role(ctx, category, True)
		except AttributeError:
			pass

	@commands.cooldown(1, 5, BucketType.user)
	@commands.command(name='unsub', description='Unsubscribes you from a perm category. Example usage: [x!unsub P5]')
	async def do_unsub(self, ctx, category):
		try:
			await self.sub_role(ctx, category, False)
		except AttributeError:
			pass


def setup(client):
	client.add_cog(XMLToolsCog(client))
