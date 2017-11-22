import discord
from discord.ext import commands
import time
import datetime
import sys,traceback
from threading import Thread
import functools


bot_information=dict(
    XMLBot=dict(
        token=('token'),
		commands=0,
		logs=0,
		events=0,
		description='XMLBot, for Atelier801 related work',
		prefix='x!',
		is_bot=True,
		default_ext=['cogs.owner_commands','cogs.dev_commands','cogs.xmlbot_tools',],
        ),
	),
)

def get_bot(name):
    for bots in bot_information:
        if bots.lower()==name.lower() or name.lower() in bots.lower() and name.lower() != 'bot':
            return True,bot_information[bots]
    return False,name

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('Function {}() timeout {} seconds exceeded.'.format(func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def dev_check(ctx):
	try:
		return (ctx.bot.primary_guild.get_member_named(ctx.author.name)).top_role.position >= discord.utils.get(
			ctx.bot.primary_guild.roles, name='Developer').position
	except Exception as e:
		print(e)
		return False
