import config


def format_karma_for_display(karma, bot_config: config.KarmaBotConfig):
	""" Formats karma for display with total, upvotes, and downvotes """
	upvote_count, downvote_count = karma
	total_karma = upvote_count - downvote_count
	formatted_upvote = bot_config.get_upvote_display()
	formatted_downvote = bot_config.get_downvote_display()
	return f'{total_karma} ({formatted_upvote} {upvote_count}, {formatted_downvote} {downvote_count})'
