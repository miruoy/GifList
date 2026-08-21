###
# GifList — post random GIF/URLs from local lists, safe for unregistered users.
#
#   gif <name>   Posts a random URL from the list named <name> in gifs.json.
#   gifs         Lists the available names.
#
# All URLs come from a LOCAL file (gifs.json in this directory) — no network
# access is performed, so there is no command-injection risk, no rate-limit
# (429) issues, and unregistered users can use it safely.
###
import os
import json

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring
_ = PluginInternationalization('GifList')


def _load_gifs():
    """Load gifs.json from the plugin directory. Returns dict or {'__error__': ...}."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, 'gifs.json')
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        # normaliseer: naam -> lijst van urls
        gifs = {}
        for name, urls in data.items():
            if isinstance(urls, (list, tuple)):
                clean = [str(u).strip() for u in urls if u]
                if clean:
                    gifs[name] = clean
        return gifs
    except (OSError, ValueError) as e:
        return {'__error__': str(e)}


class GifList(callbacks.Plugin):
    """Posts random GIF/URLs from local lists (no network access)."""

    threaded = True
    priority = 100

    @internationalizeDocstring
    def gif(self, irc, msg, args, name):
        """<name>

        Posts a random URL from the list named <name> (defined in gifs.json).
        Use 'gifs' to see the available names.
        """
        if not name:
            irc.error(_('You must specify a name. Use "gifs" to list them.'), Raise=True)
        name = str(name).strip().lower()

        gifs = _load_gifs()
        if '__error__' in gifs:
            irc.error(_('Failed to load gifs.json: %s') % gifs['__error__'], Raise=True)
        if name not in gifs:
            avail = ', '.join(sorted(gifs.keys())) or '(none)'
            irc.error(format(_('Unknown name %s. Available: %s'), name, avail), Raise=True)

        import random
        url = random.choice(gifs[name])
        irc.reply(url)

    gif = wrap(gif, [additional('something')])

    @internationalizeDocstring
    def gifs(self, irc, msg, args):
        """takes no argument

        Lists the available GIF/URL list names (from gifs.json).
        """
        gifs = _load_gifs()
        if '__error__' in gifs:
            irc.error(_('Failed to load gifs.json: %s') % gifs['__error__'], Raise=True)
        if not gifs:
            irc.reply(_('No GIF lists configured.'))
            return
        irc.replies(['Available GIF lists:'] + sorted(gifs.keys()), joiner=' ')

    gifs = wrap(gifs)


Class = GifList

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
