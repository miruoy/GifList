# GifList

A Limnoria plugin that posts a random GIF/URL from a **local** list, safe for
**unregistered** users. No network access is performed — the URLs come from a
local `gifs.json` file — so there is no command-injection risk and no
rate-limit (HTTP 429) issues.

## Commands

| Command | Description |
| --- | --- |
| `gif <name>` | Posts a random URL from the list named `<name>`. |
| `gifs` | Lists the available list names. |

## Configuration: gifs.json

Edit `gifs.json` (in this directory) to add your own named URL lists. Each
name maps to a list of URLs:

```json
{
  "bender": [
    "https://i.imgur.com/l85WHJg.gif",
    "https://i.imgur.com/xxxxxxxx.gif"
  ],
  "futurama": [
    "https://i.imgur.com/l85WHJg.gif",
    "https://i.imgur.com/yyyyyyyy.gif"
  ]
}
```

Then create aliases in the bot:

```
alias add bender "gif bender"
alias add futurama "gif futurama"
```

Now `@bender` (or `gif bender`) posts a random GIF from the `bender` list.

> Note: list names are case-insensitive.

## Installation

Copy the plugin directory into your bot's plugin path, then load it:

```bash
cp -r GifList /path/to/your/bot/plugins/
rm -rf /path/to/your/bot/plugins/GifList/__pycache__
# in the bot:
load GifList
```

If you are replacing a previously loaded copy and the bot keeps running old
code, remove the `__pycache__` directory and `touch` the `.py` files (or
unload, delete, re-copy under a new name, then load) before reloading — a
stale `.pyc` will keep the old code live.

## Troubleshooting

- **`Unknown name X. Available: ...`** — the name is not in `gifs.json`.
  Add it, or check the spelling (case-insensitive).
- **`Failed to load gifs.json: ...`** — the JSON file is missing or invalid.
  Fix `gifs.json` in the plugin directory.
