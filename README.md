# GifList

A Limnoria plugin that posts random GIFs/URLs, safe for **unregistered**
users. Two sources:

- **Local lists** — URLs from `gifs.json` (no network access, no rate-limits).
  Each name maps to a list of GIF URLs; the bot picks one at random.
- **Giphy** — random GIFs fetched from the Giphy API for a search term
  (requires a free API key in `giphy.key`). Mark a name with `"__giphy__"`
  to use Giphy instead of a local list.

No shell is spawned, so there is no command-injection risk.

## Commands

| Command | Description |
| --- | --- |
| `gif <name>` | Posts a random GIF from the list/pool named `<name>`. |
| `gifs` | Lists the available list/pool names. |
| `random` | Posts a random GIF from a RANDOM list/pool. |

## Configuration

### Local lists — gifs.json

Edit `gifs.json` (in this directory) to add named URL lists. Each name maps
to a list of URLs, or to the string `"__giphy__"` to use Giphy for that term:

```json
{
  "bender": [
    "https://media.giphy.com/media/xxx/giphy.gif",
    "https://i.imgur.com/yyyy.gif"
  ],
  "fry": "__giphy__"
}
```

- A list of URLs → the bot picks one at random (local, no network).
- `"__giphy__"` → the bot fetches a random GIF from Giphy for that name as the
  search term (e.g. `gif fry` searches Giphy for "fry").

The shipped `gifs.json` is pre-filled with 15 real GIF URLs per name for:
bender, fry, professor, futurama, zoidberg, leela, sw, prequels, rebels,
badbatch, clonewars, vader, yoda, mandalorian, grogu, memes, cat, dog,
reaction, funny.

### Giphy API key — giphy.key

For Giphy-backed pools (`"__giphy__"`), put your free API key (one line, no
quotes/newline) in `giphy.key` in this directory:

```
<GIPHY_KEY_REMOVED>
```

Get a key at https://developers.giphy.com/dashboard/ (free tier).

> Note: `giphy.key` should NOT be committed to git — keep it local.
> `gifs.json` is safe to commit (it contains no secret).

## Usage examples

```
gif bender        # random Bender GIF (from local list in gifs.json)
gif fry           # random Fry GIF (from Giphy, if fry is "__giphy__")
random            # random GIF from a random pool
gifs              # show all available names
```

Aliases in the bot:

```
alias add bender "gif bender"
alias add fry    "gif fry"
alias add sw     "gif sw"
```

Now `@bender`, `@fry`, `@sw` each post a random GIF.

> Note: list/pool names are case-insensitive.

## Installation

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
- **`Giphy error: no Giphy API key configured`** — `giphy.key` is missing or
  empty. Add your key to `giphy.key` in the plugin directory.
- **`Giphy error: ...`** — network issue or API limit; the key may be invalid
  or rate-limited.
