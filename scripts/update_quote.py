"""Rotate daily tech and cybersecurity quote in README.md."""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys

QUOTES = [
    ("The quieter you become, the more you are able to hear.", "Kali Linux"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Security is not a product, but a process.", "Bruce Schneier"),
    ("There's no patch for human stupidity.", "Kevin Mitnick"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    (
        "The only truly secure system is one that is powered off, cast in"
        " concrete, and sealed in a room with armed guards.",
        "Gene Spafford",
    ),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    (
        "There are only two types of companies: those that have been hacked, and"
        " those that will be.",
        "Robert S. Mueller III",
    ),
    ("Given enough eyeballs, all bugs are shallow.", "Eric S. Raymond"),
    (
        "Any fool can write code that a computer can understand. Good"
        " programmers write code that humans can understand.",
        "Martin Fowler",
    ),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    (
        "The most dangerous phrase in the language is: 'We've always done it"
        " this way.'",
        "Grace Hopper",
    ),
    ("Never trust, always verify.", "Zero Trust Principle"),
    ("Complexity is the enemy of security.", "Gary McGraw"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    (
        "Technology trust is a good thing, but monitoring and checking is still"
        " better.",
        "Stephane Nappo",
    ),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    (
        "Controlling complexity is the essence of computer programming.",
        "Brian Kernighan",
    ),
    (
        "If debugging is removing bugs, then programming must be putting them"
        " in.",
        "Edsger W. Dijkstra",
    ),
    (
        "Bad programmers worry about the code. Good programmers worry about"
        " data structures.",
        "Linus Torvalds",
    ),
    (
        "Hacking is about understanding how rules work and exploring the"
        " boundaries.",
        "Anonymous",
    ),
    (
        "A good programmer is someone who looks both ways before crossing a"
        " one-way street.",
        "Doug Linder",
    ),
]

START_TAG = "<!-- DAILY_QUOTE:START -->"
END_TAG = "<!-- DAILY_QUOTE:END -->"
PATTERN = re.compile(rf"{re.escape(START_TAG)}.*?{re.escape(END_TAG)}", re.DOTALL)


def format_quote(quote: str, author: str) -> str:
    return f'{START_TAG}\n> *"{quote}"*  \n> — **{author}**\n{END_TAG}'


def pick_quote(offset: int = 0) -> tuple[str, str]:
    # ponytail: day-of-year rotation avoids external API downtime; upgrade to API if user requests it
    day = datetime.now(timezone.utc).timetuple().tm_yday + offset
    return QUOTES[day % len(QUOTES)]


def update_readme(readme_path: Path) -> bool:
    content = readme_path.read_text(encoding="utf-8")
    if START_TAG not in content:
        raise ValueError(f"Marker {START_TAG} not found in {readme_path}")

    quote, author = pick_quote()
    new_block = format_quote(quote, author)

    if new_block in content:
        quote, author = pick_quote(offset=1)
        new_block = format_quote(quote, author)

    new_content = PATTERN.sub(new_block, content, count=1)
    if new_content != content:
        readme_path.write_text(new_content, encoding="utf-8")
        print(f'Updated quote: {author} - "{quote}"')
        return True
    print("Quote unchanged.")
    return False


def _self_check() -> None:
    dummy = f"head\n{START_TAG}\nold\n{END_TAG}\ntail"
    assert PATTERN.search(dummy) is not None, "Pattern failed to match tag block"
    q, a = pick_quote()
    assert len(q) > 0 and len(a) > 0, "Empty quote or author"
    formatted = format_quote(q, a)
    replaced = PATTERN.sub(formatted, dummy)
    assert q in replaced and a in replaced, "Replacement failed"
    print("Self-check passed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _self_check()
    else:
        root = Path(__file__).resolve().parent.parent
        update_readme(root / "README.md")
