import urllib.parse

import requests
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
import logging
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Gio
import urllib

# create an instance of logger at a module level
logger = logging.getLogger(__name__)


def url_to_pixbuf(url):
    response = urllib.request.urlopen(url)
    input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None)
    return Pixbuf.new_from_stream(input_stream, None)


def get_description(hit):
    return "💓 {like_count} | 💬 {comment_count} | by {creator[name]}".format(**hit)


class ThingiverseExtension(Extension):

    def __init__(self):
        super(ThingiverseExtension, self).__init__()

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        description = "Type in your query and press Enter..."

        extensionResults = []
        q = event.get_argument()
        if event.get_argument() is not None:
            extensionResults.append(ExtensionResultItem(
                icon='icons/thingiverse.svg',
                name=f"Show results for {event.get_argument()} on thingiverse",
                description=description,
                on_enter=OpenUrlAction(
                    f"https://www.thingiverse.com/search?q={event.get_argument()}&type=things&sort=relevant")
            ))
            query = urllib.parse.quote(event.get_argument())
            response = requests.get(
                f"https://api.thingiverse.com/search/{query}?page=1&per_page=20&sort=relevant&type=things", headers={
                    'Authorization': "bearer af60e225ad82ab927303fcc2f8b98552"
                })
            results = response.json()
            for hit in results["hits"]:
                extensionResults.append(ExtensionResultItem(
                    # icon=url_to_pixbuf(hit['thumbnail']),
                    icon='icons/thingiverse.svg',
                    name=hit['name'],
                    description=get_description(hit),
                    on_enter=OpenUrlAction(hit["public_url"])
                ))
        if len(extensionResults) == 0:
            extensionResults.append(ExtensionResultItem(
                icon='icons/thingiverse.svg',
                name="Search Things!",
                description=description,
            ))
        else:
            extensionResults = [] + extensionResults
        return RenderResultListAction(extensionResults)


if __name__ == '__main__':
    ThingiverseExtension().run()
