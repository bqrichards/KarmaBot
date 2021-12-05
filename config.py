from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import discord
from discord.ext import commands
from discord import Emoji, PartialEmoji
from emoji import UNICODE_EMOJI_ENGLISH

CONFIG_FILE_NAME = 'config.txt'
CONFIG_SAVE_IGNORE_KEYS = ['upvote_emoji', 'downvote_emoji']


@dataclass
class KarmaBotConfig:
	leaderboard_return_limit: int = 10
	upvote_reaction: str = '⬆️'
	downvote_reaction: str = '⬇️'
	upvote_emoji: Optional[Emoji] = None
	downvote_emoji: Optional[Emoji] = None

	def load_emojis(self, bot: commands.Bot):
		"""
		Load emojis from reaction names
		:param bot: the KarmaBot discord bot
		"""

		if self.upvote_reaction not in UNICODE_EMOJI_ENGLISH:
			result = discord.utils.get(bot.emojis, name=self.upvote_reaction)
			if result:
				self.upvote_emoji = result

		if self.downvote_reaction not in UNICODE_EMOJI_ENGLISH:
			result = discord.utils.get(bot.emojis, name=self.downvote_reaction)
			if result:
				self.downvote_emoji = result

	def get_formatted_config(self):
		all_members = self.__dict__.items()
		writable_members = list(filter(lambda x: x[0] not in CONFIG_SAVE_IGNORE_KEYS, all_members))
		return '\n'.join(f'{key}={value}' for key, value in writable_members)

	def is_karma_reaction(self, emoji: Emoji | PartialEmoji | str):
		if isinstance(emoji, Emoji) or isinstance(emoji, PartialEmoji):
			return emoji.name in self._karma_reactions()

		return emoji in self._karma_reactions()

	def is_upvote(self, emoji: Emoji | PartialEmoji | str):
		if isinstance(emoji, Emoji) or isinstance(emoji, PartialEmoji):
			return emoji.name == self.upvote_reaction

		return emoji == self.upvote_reaction

	def is_downvote(self, emoji: Emoji | PartialEmoji | str):
		if isinstance(emoji, Emoji) or isinstance(emoji, PartialEmoji):
			return emoji.name == self.downvote_reaction

		return emoji == self.downvote_reaction

	def get_upvote_display(self):
		if self.upvote_emoji is not None:
			return f'<:{self.upvote_emoji.name}:{self.upvote_emoji.id}>'

		return self.upvote_reaction

	def get_downvote_display(self):
		if self.downvote_emoji is not None:
			return f'<:{self.downvote_emoji.name}:{self.downvote_emoji.id}>'

		return self.downvote_reaction

	def _karma_reactions(self):
		return [self.upvote_reaction, self.downvote_reaction]


@dataclass
class ConfigChangeAttempt:
	success: bool
	errorMessage: Optional[str]


def write_config(config):
	with open(CONFIG_FILE_NAME, 'w') as f:
		default_config = config.get_formatted_config()
		f.write(default_config)


def write_default_config():
	""" Writes config file with default values """
	write_config(KarmaBotConfig())


def _attempt_config_change(config, key, value, write_change=False) -> ConfigChangeAttempt:
	config_annotations = config.__annotations__
	valid_keys = config_annotations.keys()

	if key not in valid_keys:
		return ConfigChangeAttempt(False, f'Invalid config file key: {key}')

	if config_annotations[key] == 'int':
		try:
			value = int(value)
		except ValueError:
			return ConfigChangeAttempt(False, f'Invalid config value: {key}={value}, {value} should be a number')

	config.__setattr__(key, value)

	if write_change:
		write_config(config)

	return ConfigChangeAttempt(True, None)


def read_config() -> KarmaBotConfig:
	""" Reads config file from disk and returns a config object """
	config = KarmaBotConfig()

	with open(CONFIG_FILE_NAME, 'r') as f:
		for line in f:
			key_value = line.split('=')
			if len(key_value) != 2:
				print(f'Invalid config file line: {line}')
				continue

			key, value = key_value
			value = value.strip()
			attempt = _attempt_config_change(config, key, value)
			if not attempt.success:
				print(attempt.errorMessage)
				continue

	return config


def load_config() -> KarmaBotConfig:
	# Write default config
	if not os.path.exists(CONFIG_FILE_NAME):
		write_default_config()

	# Read config
	config = read_config()

	# Write in case of default values
	write_config(config)

	return config


def change_config(config, key, value) -> ConfigChangeAttempt:
	return _attempt_config_change(config, key, value, write_change=True)
