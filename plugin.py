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


def _load_giphy_key():
    """Lees de Giphy API-key uit giphy.key (1 regel). Returns '' als niet gevonden."""
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, 'giphy.key')
    try:
        with open(p, encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''

_GIPHY_KEY = _load_giphy_key()

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


def _giphy_random(term, api_key, limit=50):
    """Haal een random gif-URL van Giphy voor <term>. Returns (url, error)."""
    if not api_key:
        return (None, 'no Giphy API key configured')
    import urllib.request, urllib.parse, json
    q = urllib.parse.quote(term)
    url = ('https://api.giphy.com/v1/gifs/search?api_key=%s&q=%s&limit=%d'
           % (api_key, q, limit))
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 (GifList/Limnoria)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        gifs = data.get('data', [])
        if not gifs:
            return (None, 'no gifs found for %s' % term)
        import random
        g = random.choice(gifs)
        # gebruik de KORTE giphy-url: media.giphy.com/media/<id>/giphy.gif
        gid = g.get('id', '')
        if gid:
            return ('https://media.giphy.com/media/%s/giphy.gif' % gid, None)
        # fallback: originele url
        return (g.get('images', {}).get('original', {}).get('url') or
                g.get('url', ''), None)
    except (urllib.error.URLError, ValueError, OSError) as e:
        return (None, str(e))


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

        # Als het een giphy-pool is, haal een random gif van Giphy
        if isinstance(gifs[name], str) and gifs[name] == '__giphy__':
            (url, err) = _giphy_random(name, _GIPHY_KEY)
            if err:
                irc.error(_('Giphy error: %s') % err, Raise=True)
            irc.reply(url)
            return

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


    @internationalizeDocstring
    def gifrnd(self, irc, msg, args):
        """takes no argument

        Posts a random GIF from a RANDOM list (picks a random name first,
        then a random GIF from that list — local or Giphy). Named 'gifrnd'
        to avoid clashing with other plugins' 'random' command.
        """
        gifs = _load_gifs()
        if '__error__' in gifs:
            irc.error(_('Failed to load gifs.json: %s') % gifs['__error__'], Raise=True)
        names = [n for n in gifs if n != '__error__']
        if not names:
            irc.reply(_('No GIF lists configured.'))
            return
        import random as _r
        name = _r.choice(names)
        # giphy-pool?
        if isinstance(gifs[name], str) and gifs[name] == '__giphy__':
            (url, err) = _giphy_random(name, _GIPHY_KEY)
            if err:
                irc.error(_('Giphy error: %s') % err, Raise=True)
            irc.reply(url)
            return
        url = _r.choice(gifs[name])
        irc.reply(url)

    gifrnd = wrap(gifrnd)

Class = GifList

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
