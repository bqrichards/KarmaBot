import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import KarmaBotConfig, load_config, change_config
from karma import KarmaMap, format_karma_for_display, has_karma_reaction

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class KarmaBot(commands.Bot):
	karma_config: KarmaBotConfig


bot = KarmaBot(command_prefix='!')
karma_map: KarmaMap


def insert_reaction_change_into_ranking(payload: discord.RawReactionActionEvent):
	global karma_map
	karma_map.modify_message(payload)


def get_karma_for_user(guild: int, user: int):
	""" Get the karma of a user in a guild """
	global karma_map
	return karma_map.get_karma_for_user(guild, user)


async def scan_for_karma():
	""" Scan all guilds and channels for karma """
	print('Scanning...')

	for channel in bot.get_all_channels():
		if type(channel) != discord.channel.TextChannel:
			continue

		async for msg in channel.history(limit=bot.karma_config.scan_history_amount):
			if has_karma_reaction(msg, bot.karma_config):
				karma_map.add_message(msg)

	print('Done scanning')


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	bot.karma_config = load_config()
	bot.karma_config.load_emojis(bot)
	global karma_map
	karma_map = KarmaMap(bot.karma_config)
	await scan_for_karma()


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
	insert_reaction_change_into_ranking(payload)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
	insert_reaction_change_into_ranking(payload)


@bot.command()
async def leaderboard(ctx):
	leaderboard = await karma_map.get_leaderboard(ctx.guild.id, bot)
	await ctx.send(leaderboard)


@bot.command()
async def karma(ctx, target_user: discord.Member = None):
	global karma_map
	guild = ctx.guild.id
	user = ctx.author.id if target_user is None else target_user.id
	karma = get_karma_for_user(guild, user)
	reply = format_karma_for_display(karma, bot.karma_config)
	await ctx.reply(reply)


@bot.command()
async def config(ctx, target_key: str = None, target_value: str = None):
	if target_value is None or target_value is None:
		await ctx.reply(f'Usage: !config <target_key> <target_value>\nCurrent config:\n```{bot.karma_config.get_formatted_config()}```')
		return

	change_attempt = change_config(bot.karma_config, target_key, target_value)
	if change_attempt.success:
		await ctx.reply('Changed')
	else:
		await ctx.reply(f'Error! {change_attempt.errorMessage}')


bot.run(TOKEN)
