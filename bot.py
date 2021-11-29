import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

UPVOTE = '⬆️'
DOWNVOTE = '⬇️'
KARMA_REACTIONS = [UPVOTE, DOWNVOTE]
LEADERBOARD_RETURN_LIMIT = 10

client = discord.Client()


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


def has_karma_reaction(message):
	""" Returns if this message has any karma reactions """
	return any(reaction.emoji in KARMA_REACTIONS for reaction in message.reactions)


async def scan_for_karma():
	""" Scan all guilds and channels for karma """
	global ranking_map
	ranking_map = dict()
	print('Scanning...')
	for channel in client.get_all_channels():
		if type(channel) != discord.channel.TextChannel:
			continue

		async for msg in channel.history(limit=1000):
			if has_karma_reaction(msg):
				insert_message_into_ranking(msg)


async def format_leaderboard(guild):
	""" Returns a karma leaderboard for a given guild """
	global ranking_map
	data = sorted(ranking_map[guild].items(), key=ranking_sorter)[:LEADERBOARD_RETURN_LIMIT]
	data_formatted = (f'{user_id}: {karma[0] - karma[1]} ({UPVOTE}{karma[0]}, {DOWNVOTE}{karma[1]})' for user_id, karma in data)
	return '\n'.join(data_formatted)


@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	await scan_for_karma()


@client.event
async def on_message(message):
	if message.content == '!k leaderboard':
		leaderboard = await format_leaderboard(message.guild.id)
		channel = client.get_channel(message.channel.id)
		await channel.send(leaderboard)
		return


client.run(TOKEN)
