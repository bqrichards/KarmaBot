import config
from dataclasses import dataclass
import discord
from discord.ext import commands
from config import KarmaBotConfig


@dataclass
class KarmaSummary:
	"""
	The amount of upvotes, downvotes, and total karma of a user
	"""
	upvotes: int
	downvotes: int
	total: int


class KarmaUser:
	_upvotes: int
	_downvotes: int

	def __init__(self):
		self._upvotes = 0
		self._downvotes = 0

	def add_message(self, message: discord.Message, config: KarmaBotConfig):
		upvotes = 0
		downvotes = 0
		for reaction in message.reactions:
			if config.is_upvote(reaction.emoji):
				upvotes += 1
			elif config.is_downvote(reaction.emoji):
				downvotes += 1

		self._upvotes += upvotes
		self._downvotes += downvotes

	def get_karma(self):
		return KarmaSummary(self._upvotes, self._downvotes, self._upvotes - self._downvotes)

	def modify_message(self, payload: discord.RawReactionActionEvent, config: KarmaBotConfig):
		if payload.event_type == 'REACTION_ADD':
			if config.is_upvote(payload.emoji):
				self._upvotes += 1
			else:
				self._downvotes += 1
		else:
			if config.is_upvote(payload.emoji):
				self._upvotes -= 1
			else:
				self._downvotes -= 1


def ranking_sorter(userid_karma_map: tuple[int, KarmaUser]):
	""" Sorter for (username_id, (upvotes, downvote)) """
	karma = userid_karma_map[1].get_karma()
	return karma.downvotes - karma.upvotes


class KarmaGuild:
	_internal_map: dict[int, KarmaUser]

	def __init__(self):
		self._internal_map = dict()

	def get_user(self, user_id: int):
		return self._internal_map[user_id]

	def add_message(self, message: discord.Message, config: KarmaBotConfig):
		# Check if user exists
		if message.author.id not in self._internal_map:
			self._internal_map[message.author.id] = KarmaUser()

		self.get_user(message.author.id).add_message(message, config)

	async def get_leaderboard(self, bot: commands.Bot):
		data = sorted(self._internal_map.items(), key=ranking_sorter)[
			   :bot.karma_config.leaderboard_return_limit]
		data_formatted = []
		for user_id, user_summary in data:
			user = await bot.fetch_user(user_id)
			username = user.display_name if user is not None else '<unknown>'
			karma_display = format_karma_for_display(user_summary.get_karma(), bot.karma_config)
			data_formatted.append(f'{username}: {karma_display}')

		return '\n'.join(data_formatted)

	def modify_message(self, payload: discord.RawReactionActionEvent, config: KarmaBotConfig):
		self.get_user(payload.user_id).modify_message(payload, config)


class KarmaMap:
	_internal_map: dict[int, KarmaGuild]
	_config: KarmaBotConfig

	def __init__(self, config: KarmaBotConfig):
		self._internal_map = dict()
		self._config = config

	def _get_guild(self, guild_id: int):
		return self._internal_map[guild_id]

	def _initialize_guild(self, guild_id: int):
		"""
		Create a guild if one does not exist
		:param guild_id: the id of the guild
		"""
		if guild_id not in self._internal_map:
			self._internal_map[guild_id] = KarmaGuild()

	def get_karma_for_user(self, guild_id: int, user_id: int):
		"""
		Get the karma for a specific user
		:param guild_id: the guild id
		:param user_id: the user id
		:return: the user's karma
		"""
		return self._get_guild(guild_id).get_user(user_id).get_karma()

	async def get_leaderboard(self, guild_id: int, bot: commands.Bot):
		if guild_id not in self._internal_map:
			return 'No data for this guild yet.'

		return await self._get_guild(guild_id).get_leaderboard(bot)

	def add_message(self, message: discord.Message):
		"""
		Insert a message into the map
		:param message: the message to insert
		"""
		self._initialize_guild(message.guild.id)
		self._get_guild(message.guild.id).add_message(message, self._config)

	def modify_message(self, payload: discord.RawReactionActionEvent):
		self._get_guild(payload.guild_id).modify_message(payload, self._config)


def format_karma_for_display(karma_summary: KarmaSummary, bot_config: config.KarmaBotConfig):
	""" Formats karma for display with total, upvotes, and downvotes """
	formatted_upvote = bot_config.get_upvote_display()
	formatted_downvote = bot_config.get_downvote_display()
	return f'{karma_summary.total} ({formatted_upvote} {karma_summary.upvotes}, {formatted_downvote} {karma_summary.downvotes})'


def has_karma_reaction(message: discord.Message, config: KarmaBotConfig):
	""" Returns if this message has any karma reactions """
	return any(config.is_karma_reaction(reaction.emoji) for reaction in message.reactions)
