def format_karma_for_display(karma, upvote, downvote):
	""" Formats karma for display with total, upvotes, and downvotes """
	upvote_count, downvote_count = karma
	total_karma = upvote_count - downvote_count
	return f'{total_karma} ({upvote} {upvote_count}, {downvote} {downvote_count})'
