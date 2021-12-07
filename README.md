# KarmaBot

## Commands

### All commands

| key                     | description                                                      |
|-------------------------|------------------------------------------------------------------|
| `!karma [user]`         | Replies with the karma of the user                               |
| `!leaderboard`          | Sends message containing leaderboard of users with highest karma |
| `!config <key> <value>` | Changes config option                                            |


## Config

### Changing config

There are two ways to change KarmaBot's configuration. 

1. Edit the `config.txt` file.
2. Use the `!config <key> <value>` command.

### All config options

| key                      | description                                                 | type   | default |
|--------------------------|-------------------------------------------------------------|--------|---------|
| leaderboard_return_limit | The maximum number of users displayed in the leaderboards   | number | 10      |
| upvote_reaction          | The emoji OR name of server emote that represents upvotes   | string | ⬆️      |
| downvote_reaction        | The emoji OR name of server emote that represents downvotes | string | ⬇️      | 
| scan_history_amount      | The number of messages to scan in each channel for karma    | number | 2000    |

## License

See [LICENSE](https://github.com/bqrichards/KarmaBot/blob/main/LICENSE)
