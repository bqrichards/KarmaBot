import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import KarmaBotConfig, load_config, change_config
from karma import format_karma_for_display

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class KarmaBot(commands.Bot):
	karma_config: KarmaBotConfig


bot = KarmaBot(command_prefix='!')

# guild_id -> [user_id: (upvotes, downvotes)]
ranking_map = dict()


def ranking_sorter(username_karma_map):
	""" Sorter for (username_id, (upvotes, downvote)) """
	upvotes, downvotes = username_karma_map[1]
	return downvotes - upvotes


def record_ranking(guild: int, user: int, upvotes: int, downvotes: int):
	""" Record this guild, user, and relative upvote/downvote """
	# Check if guild exists
	if guild not in ranking_map:
		ranking_map[guild] = dict()

	# Check if user exists
	if user not in ranking_map[guild]:
		ranking_map[guild][user] = (0, 0)

	# Update karma
	old_upvotes, old_downvotes = ranking_map[guild][user]
	ranking_map[guild][user] = (old_upvotes + upvotes, old_downvotes + downvotes)


def insert_message_into_ranking(message):
	""" Given a message with at least one karma reaction, insert into karma record """
	guild = message.guild.id
	user = message.author.id
	upvotes = 0
	downvotes = 0
	for reaction in message.reactions:
		if bot.karma_config.is_upvote(reaction.emoji):
			upvotes += 1
		elif bot.karma_config.is_downvote(reaction.emoji):
			downvotes += 1

	record_ranking(guild, user, upvotes, downvotes)


def get_karma_for_user(guild: int, user: int):
	""" Get the karma of a user in a guild """
	return ranking_map[guild][user]


def has_karma_reaction(message):
	""" Returns if this message has any karma reactions """
	return any(bot.karma_config.is_karma_reaction(reaction.emoji) for reaction in message.reactions)


async def scan_for_karma():
	""" Scan all guilds and channels for karma """
	print('Scanning...')

	for channel in bot.get_all_channels():
		if type(channel) != discord.channel.TextChannel:
			continue

		async for msg in channel.history(limit=1000):
			if has_karma_reaction(msg):
				insert_message_into_ranking(msg)

	print('Done scanning')


async def format_leaderboard(guild):
	""" Returns a karma leaderboard for a given guild """
	global ranking_map
	if guild not in ranking_map:
		return 'No data for this guild yet.'

	data = sorted(ranking_map[guild].items(), key=ranking_sorter)[:bot.karma_config.leaderboard_return_limit]
	data_formatted = []
	for user_id, karma in data:
		user = await bot.fetch_user(user_id)
		username = user.display_name if user is not None else '<unknown>'
		karma_display = format_karma_for_display(karma, bot.karma_config)
		data_formatted.append(f'{username}: {karma_display}')

	return '\n'.join(data_formatted)


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	bot.karma_config = load_config()
	bot.karma_config.load_emojis(bot)
	await scan_for_karma()


@bot.command()
async def leaderboard(ctx):
	leaderboard = await format_leaderboard(ctx.guild.id)
	await ctx.send(leaderboard)


@bot.command()
async def karma(ctx, target_user: discord.Member = None):
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
