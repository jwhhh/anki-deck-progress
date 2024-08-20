# import the main window object (mw) from aqt
import re
from aqt import mw
from aqt.deckbrowser import DeckBrowserContent
from aqt.gui_hooks import deck_browser_will_render_content


def callback(browser, content: DeckBrowserContent) -> None:

    table = content.tree

    table = table.replace("<th class=count>Due</th>", "<th class=count>Due</th>\n<th class=count>Progress</th>\n<th></th>")

    for deck_name_id in mw.col.decks.all_names_and_ids():

        # Yes I am manipulating HTML with regexes. If it breaks I will fix it. Python has no built in HTML manipulator so this is the best I can do
        regex = re.compile(r'%DECK_NAME%.*?(\<td)\ align=center\ class=opts'.replace("%DECK_NAME%", deck_name_id.name), re.MULTILINE | re.DOTALL)
        match = regex.search(table)

        #print(f"Regex: {regex.pattern}")
        #print(f"Deck name: {deck_name_id.name}")
        #print(f"Match: {match}")
        #print(f"Groups: {match.groups()}")
        #print(f"Group start: {match.start(1)}")

        pre = table[0:match.start(1)]
        post = table[match.start(1):]

        total_cards = len(mw.col.find_cards(f"did:{deck_name_id.id}"))
        are_new = len(mw.col.find_cards(f"did:{deck_name_id.id} is:new"))
        seen = total_cards - are_new

        perc = seen / total_cards if total_cards > 0 else 0
        status_perc = f"{perc * 100:0.2f}%"
        status_abs = f"({seen} / {total_cards})"

        table = pre + r"<td class=zero-count> " + status_perc + r"</td>" + r"<td class=zero-count> " + status_abs + r"</td>" + post

    content.tree = table

    #print(f"Content tree: {content.tree}")


deck_browser_will_render_content.append(callback)
