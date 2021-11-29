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


# guildid -> [username: (upvotes, downvotes)]
ranking_map = dict()


def ranking_sorter(username_karma_map):
	upvotes, downvotes = username_karma_map[1]
	return upvotes - downvotes


def record_ranking(guild: int, user: int, upvotes: int, downvotes: int):
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
	return any(reaction.emoji in KARMA_REACTIONS for reaction in message.reactions)


async def scan_for_karma(message):
	global ranking_map
	ranking_map = dict()
	print('Scanning...')
	async for msg in message.channel.history(limit=1000):
		if has_karma_reaction(msg):
			insert_message_into_ranking(msg)


async def format_leaderboard(guild):
	global ranking_map
	data = sorted(ranking_map[guild].items(), key=ranking_sorter)[:LEADERBOARD_RETURN_LIMIT]
	data_formatted = (f'{user_id}: {karma[0] - karma[1]} ({UPVOTE}{karma[0]}, {DOWNVOTE}{karma[1]})' for user_id, karma in data)
	return '\n'.join(data_formatted)


@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
	if message.content == '!k scan':
		await scan_for_karma(message)
		return
	elif message.content == '!k leaderboard':
		leaderboard = await format_leaderboard(message.guild.id)
		channel = client.get_channel(message.channel.id)
		await channel.send(leaderboard)
		return


client.run(TOKEN)
