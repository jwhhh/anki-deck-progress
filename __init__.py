# import the main window object (mw) from aqt
import re
from aqt import mw
from aqt.deckbrowser import DeckBrowserContent
from aqt.gui_hooks import deck_browser_will_render_content


def find_num_of_cards(deck_name: str, query: str) -> int:
    """Helper function to find number of cards in a deck with a specific query"""
    if query:
        return len(mw.col.find_cards(f'"deck:{deck_name}" {query}'))
    else:
        return len(mw.col.find_cards(f'"deck:{deck_name}"'))


def callback(browser, content: DeckBrowserContent) -> None:

    table = content.tree

    table = table.replace("<th class=count>Due</th>", "<th class=count>Due</th>\n<th class=count>Progress</th>\n<th></th>")

    for deck_name_id in mw.col.decks.all_names_and_ids():

        # Look for the deck row by ID instead of name - this is more reliable
        # The HTML structure has: <tr class='deck' id='DECK_ID'>
        deck_id_pattern = rf"<tr[^>]*id='{deck_name_id.id}'[^>]*>.*?(<td[^>]*align=center[^>]*class=opts)"
        regex = re.compile(deck_id_pattern, re.MULTILINE | re.DOTALL)
        match = regex.search(table)
        
        if match is None:
            print(f"No match found for deck: {deck_name_id.name} (ID: {deck_name_id.id})")
            continue

        pre = table[0:match.start(1)]
        post = table[match.start(1):]

        # Include subdecks in card count using deck name instead of ID
        total_cards = find_num_of_cards(deck_name_id.name, "")
        are_new = find_num_of_cards(deck_name_id.name, "is:new")
        seen = total_cards - are_new

        # # Debug output
        # print(f"Deck: {deck_name_id.name} (ID: {deck_name_id.id})")
        # print(f"  Total cards: {total_cards}")
        # print(f"  New cards: {are_new}")
        # print(f"  Seen cards: {seen}")

        perc = seen / total_cards if total_cards > 0 else 0
        status_perc = f"{perc * 100:0.2f}%"
        status_abs = f"({seen} / {total_cards})"

        table = pre + r"<td class=zero-count> " + status_perc + r"</td>" + r"<td class=zero-count> " + status_abs + r"</td>" + post

    content.tree = table

    #print(f"Content tree: {content.tree}")


deck_browser_will_render_content.append(callback)
