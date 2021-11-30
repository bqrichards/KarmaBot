import os
from dataclasses import dataclass
from typing import Optional

CONFIG_FILE_NAME = 'config.txt'


@dataclass
class KarmaBotConfig:
	leaderboard_return_limit: int = 10

	def get_formatted_config(self):
		return '\n'.join(f'{key}={value}' for key, value in self.__dict__.items())


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

	if config_annotations[key] == int:
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

	return config


def change_config(config, key, value) -> ConfigChangeAttempt:
	return _attempt_config_change(config, key, value, write_change=True)
