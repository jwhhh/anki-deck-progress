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

        # Yes I am manipulating HTML with regexes. If it breaks I will fix it. Python has no built in HTML manipulator so this is the best I can do
        # Escape special regex characters in deck name
        escaped_deck_name = re.escape(deck_name_id.name)
        # Try multiple regex patterns to find the deck row
        patterns = [
            r'%DECK_NAME%.*?(\<td)\ align=center\ class=opts',
            r'%DECK_NAME%.*?(\<td)\ align=center\ class=opts',
            r'%DECK_NAME%.*?(\<td[^>]*align=center[^>]*class=opts)',
            r'%DECK_NAME%.*?(\<td[^>]*class=opts)',
        ]
        
        match = None
        for pattern in patterns:
            regex = re.compile(pattern.replace("%DECK_NAME%", escaped_deck_name), re.MULTILINE | re.DOTALL)
            match = regex.search(table)
            if match:
                print(f"Found match with pattern: {pattern}")
                break
        
        if match is None:
            print(f"No match found for deck: {deck_name_id.name}")
            # Let's also print a snippet of the table to see what we're working with
            deck_line_start = table.find(deck_name_id.name)
            if deck_line_start != -1:
                snippet = table[deck_line_start:deck_line_start + 200]
                print(f"Table snippet around deck name: {snippet}")
            continue

        pre = table[0:match.start(1)]
        post = table[match.start(1):]

        # Include subdecks in card count using deck name instead of ID
        total_cards = find_num_of_cards(deck_name_id.name, "")
        are_new = find_num_of_cards(deck_name_id.name, "is:new")
        seen = total_cards - are_new

        # Debug output
        print(f"Deck: {deck_name_id.name} (ID: {deck_name_id.id})")
        print(f"  Total cards: {total_cards}")
        print(f"  New cards: {are_new}")
        print(f"  Seen cards: {seen}")

        perc = seen / total_cards if total_cards > 0 else 0
        status_perc = f"{perc * 100:0.2f}%"
        status_abs = f"({seen} / {total_cards})"

        table = pre + r"<td class=zero-count> " + status_perc + r"</td>" + r"<td class=zero-count> " + status_abs + r"</td>" + post

    content.tree = table

    #print(f"Content tree: {content.tree}")


deck_browser_will_render_content.append(callback)
