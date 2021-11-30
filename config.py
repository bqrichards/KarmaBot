import os
from dataclasses import dataclass

CONFIG_FILE_NAME = 'config.txt'


@dataclass
class KarmaBotConfig:
	leaderboard_return_limit: int = 10


def write_default_config():
	""" Writes config file with default values """
	default_config = KarmaBotConfig()
	with open(CONFIG_FILE_NAME, 'w') as f:
		default_config = '\n'.join(f'{key}={value}' for key, value in default_config.__dict__.items())
		f.write(default_config)


def read_config() -> KarmaBotConfig:
	""" Reads config file from disk and returns a config object """
	config = KarmaBotConfig()
	config_annotations = config.__annotations__
	valid_keys = config_annotations.keys()

	with open(CONFIG_FILE_NAME, 'r') as f:
		for line in f:
			key_value = line.split('=')
			if len(key_value) != 2:
				print(f'Invalid config file line: {line}')
				continue

			key, value = key_value
			if key not in valid_keys:
				print(f'Invalid config file key: {key}')
				continue

			if config_annotations[key] == int:
				try:
					value = int(value)
				except ValueError:
					print(f'Invalid config value: {line}, {value} should be a number')
					continue

			config.__setattr__(key, value)

	return config


def load_config() -> KarmaBotConfig:
	# Write default config
	if not os.path.exists(CONFIG_FILE_NAME):
		write_default_config()

	# Read config
	config = read_config()

	return config
