#!/usr/bin/python
# lyrics
# Transforms an input lyrics file into HTML
#
# Lyrics file format:
# [MM:SS timestamp] contents of the lyrics {noteworthy explanation=noteworthy text} contents of the lyrics

from argparse import ArgumentParser
from pathlib import Path

import re

HEADER_LINE_REGEX: re.Pattern = re.compile(r"^(#+)(.*)$")
SUB_LINE_REGEX: re.Pattern = re.compile(r"^=(.*)$")
INFO_LINE_REGEX: re.Pattern = re.compile(r"^\|(.*)\|$")
NOTE_LINE_REGEX: re.Pattern = re.compile(r"^\*(.*)\*$")
META_LINE_REGEX: re.Pattern = re.compile(r"^\.(.*)=(.*)$")
LYRIC_LINE_REGEX: re.Pattern = re.compile(r"^\[(\d\d:\d\d)\](.*)//(.*)$")


def make_html_safe(line: str) -> str:
    line = line.replace('"', "&quot;")
    line = line.replace("'", "&#x27;")
    return line


def parse_header_line(line: re.Match) -> str:
    size: str = line.group(1).strip()
    header: str = make_html_safe(line.group(2).strip())

    tag: str = f"h{len(size)}"
    return f"<{tag}>{header}</{tag}>"


def parse_sub_line(line: re.Match) -> str:
    subtitle: str = make_html_safe(line.group(1).strip())
    return f'<p class="subtitle"><i>{subtitle}</i></p>'


def parse_info_line(line: re.Match) -> str:
    info: str = make_html_safe(line.group(1).strip())
    return f"""\
  <div class="info-box">
    <p class="info">{info}</p>
  </div>
"""


def parse_note_line(line: re.Match) -> str:
    note: str = make_html_safe(line.group(1).strip())
    return f'<p class="note"><i>T/L Note: {note}</i></p>'


def parse_meta_line(line: re.Match) -> str:
    key: str = line.group(1).strip()
    value: str = make_html_safe(line.group(2).strip())
    match key:
        case "title":
            return f"""\
  <hr />
  <div class="meta">
    <h2 class="meta-title">{value}</h2>
"""
        case "en_title":
            return f'    <p class="meta-en-title">({value})</p>\n'
        case "artist":
            return f'    <p class="meta-artist">{value}</p>\n  </div>\n'
        case "info":
            return f"""\
  <div class="meta-info-box">
    <p class="meta-info">{value}</p>
  </div>
"""

    return f"parse error: {value}"


def parse_lyric_line(line: re.Match) -> str:
    timestamp: str = line.group(1)
    lyric: str = make_html_safe(line.group(2).strip())
    og: str = make_html_safe(line.group(3))

    output: str = f"""\
  <div class="lyric-box">
    <div class="lyric">
      <p class="lyric-time"><i>{timestamp}</i></p>
      <p class="lyric-text">"""

    inside_abbr: bool = False
    for c in lyric:
        if c == "{":
            inside_abbr = True
            output += '<abbr class="lyric-note" title="'
        elif inside_abbr and c == "=":
            output += '">'
        elif inside_abbr and c == "}":
            inside_abbr = False
            output += "</abbr>"
        else:
            output += c

    output += f"""</p>
    </div>
    <p class="lyric-og">{og}</p>
  </div>
"""

    return output


def parse_line(line: str) -> str:
    # Line break?
    if line == "---":
        return "  <hr />\n"

    # Break in the lyrics?
    if line == "[pause]":
        return "  <br />\n"

    # Instrumental?
    if line == "[instrumental]":
        return '<p class="instrumental">(instrumental)</p>'

    # Previous section repeats?
    if line == "[repeat]":
        return """\
  <br />
  <div class="lyric-box">
    <p class="lyric-og">(repeats until end)</p>
    <p class="lyric-faded">(repete até o final)</p>
  </div>
  <br />
"""

    # HTML tag?
    if line[0] == "<":
        return line

    # Header line? (# HEADER)
    if header_line := HEADER_LINE_REGEX.search(line):
        return parse_header_line(header_line)

    # Subtitle line? (= SUBTITLE)
    if sub_line := SUB_LINE_REGEX.search(line):
        return parse_sub_line(sub_line)

    # Info line? (|INFO|)
    if info_line := INFO_LINE_REGEX.search(line):
        return parse_info_line(info_line)

    # Note line? (*NOTE*)
    if note_line := NOTE_LINE_REGEX.search(line):
        return parse_note_line(note_line)

    # Meta line? (.KEY = VALUE)
    if meta_line := META_LINE_REGEX.search(line):
        return parse_meta_line(meta_line)

    # Lyrics line? ([MM:SS] LYRIC)
    if lyric_line := LYRIC_LINE_REGEX.search(line):
        return parse_lyric_line(lyric_line)

    # Default to a generic paragraph
    return f'<p class="paragraph">{line}</p>'


def generate_lyrics(filename: Path, infile) -> None:
    lyrics_out: Path = filename.with_suffix(".html")
    lyrics_out = lyrics_out.relative_to("lyrics/")

    with open(lyrics_out, "w") as f:
        f.write("""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Clube da Esquina</title>
    <link href="css/style.css" rel="stylesheet" />
  </head>
  <body>
    <script src="js/script.js" defer></script>
    <button id="theme-button">Dark</button>
    <div id="wrapper">
      <main id="main">
""")
        raw_mode: bool = False
        for line in infile:
            line = line.strip()
            if not line:
                continue

            if line == "===":
                raw_mode = not raw_mode
            elif raw_mode:
                f.write(line + "\n")
            else:
                result = parse_line(line)
                f.write(result)

        f.write("      </main>\n")
        f.write("    </div>\n")
        f.write("  </body>\n")
        f.write("</html>")


def main() -> None:
    lyrics_folder: Path = Path("lyrics")
    for file in lyrics_folder.glob("*.txt"):
        with open(file) as f:
            generate_lyrics(file, f)


if __name__ == "__main__":
    main()
