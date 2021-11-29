import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

UPVOTE = '⬆️'
DOWNVOTE = '⬇️'
KARMA_REACTIONS = [UPVOTE, DOWNVOTE]
LEADERBOARD_RETURN_LIMIT = 10

bot = commands.Bot(command_prefix='!')

# guild_id -> [user_id: (upvotes, downvotes)]
ranking_map = dict()


def ranking_sorter(username_karma_map):
	""" Sorter for (username_id, (upvotes, downvote)) """
	upvotes, downvotes = username_karma_map[1]
	return upvotes - downvotes


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
		if reaction.emoji == UPVOTE:
			upvotes += 1
		elif reaction.emoji == DOWNVOTE:
			downvotes += 1

	record_ranking(guild, user, upvotes, downvotes)


def get_karma_for_user(guild: int, user: int):
	""" Get the karma of a user in a guild """
	return ranking_map[guild][user]


def has_karma_reaction(message):
	""" Returns if this message has any karma reactions """
	return any(reaction.emoji in KARMA_REACTIONS for reaction in message.reactions)


async def scan_for_karma():
	""" Scan all guilds and channels for karma """
	global ranking_map
	ranking_map = dict()
	print('Scanning...')

	for channel in bot.get_all_channels():
		if type(channel) != discord.channel.TextChannel:
			continue

		async for msg in channel.history(limit=1000):
			if has_karma_reaction(msg):
				insert_message_into_ranking(msg)

	print('Done scanning')


def format_karma_for_display(karma):
	""" Formats karma for display with total, upvotes, and downvotes """
	upvote_count, downvote_count = karma
	total_karma = upvote_count - downvote_count
	return f'{total_karma} ({UPVOTE} {upvote_count}, {DOWNVOTE} {downvote_count})'


async def format_leaderboard(guild):
	""" Returns a karma leaderboard for a given guild """
	global ranking_map
	data = sorted(ranking_map[guild].items(), key=ranking_sorter)[:LEADERBOARD_RETURN_LIMIT]
	data_formatted = []
	for user_id, karma in data:
		user = await bot.fetch_user(user_id)
		username = user.display_name if user is not None else '<unknown>'
		karma_display = format_karma_for_display(karma)
		data_formatted.append(f'{username}: {karma_display}')

	return '\n'.join(data_formatted)


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
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
	reply = format_karma_for_display(karma)
	await ctx.reply(reply)


bot.run(TOKEN)
