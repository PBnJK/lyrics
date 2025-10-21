#!/usr/bin/env -S bash -c 'exec "`dirname $0`/.venv/bin/python" "$0" "$@"'
# lyrics
# Transforms an input lyrics file into HTML
#
# Lyrics file format:
# [MM:SS timestamp] contents of the lyrics {noteworthy explanation=noteworthy text} contents of the lyrics

from pathlib import Path

import re
from unidecode import unidecode

HEADER_LINE_REGEX: re.Pattern = re.compile(r"^(#+)(.*)$")
SUB_LINE_REGEX: re.Pattern = re.compile(r"^=(.*)$")
INFO_LINE_REGEX: re.Pattern = re.compile(r"^\|(.*)\|$")
NOTE_LINE_REGEX: re.Pattern = re.compile(r"^\*(.*)\*$")
META_LINE_REGEX: re.Pattern = re.compile(r"^\.(.*)=(.*)$")
LYRIC_LINE_REGEX: re.Pattern = re.compile(r"^\[(\d\d:\d\d)\](.*)//(.*)$")
REM_LINE_REGEX: re.Pattern = re.compile(r"^\[!(.*)//(.*)\]")
SPOILER_LINE_REGEX: re.Pattern = re.compile(r"\[\?(.*?)=(.*)\]")


def make_html_safe(line: str) -> str:
    line = line.replace('"', "&quot;")
    line = line.replace("'", "&#x27;")
    return line


def parse_header_line(line: re.Match) -> str:
    size: str = line.group(1).strip()
    header: str = line.group(2).strip()

    tag: str = f"h{len(size)}"
    return f"<{tag}>{header}</{tag}>\n"


def parse_sub_line(line: re.Match) -> str:
    subtitle: str = line.group(1).strip()
    return f'<p class="subtitle"><i>{subtitle}</i></p>\n'


def parse_info_line(line: re.Match) -> str:
    info: str = line.group(1).strip()
    return f"""\
  <div class="info-box">
    <p class="info">{info}</p>
  </div>
"""


def parse_note_line(line: re.Match) -> str:
    note: str = line.group(1).strip()
    return f'<p class="note"><i>T/L Note: {note}</i></p>\n'


def parse_meta_line(line: re.Match, out: dict) -> str:
    key: str = line.group(1).strip()
    value: str = line.group(2).strip()
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
            return f'    <p class="meta-artist">{value}</p>\n'
        case "composer":
            return f'    <p class="meta-small">Comp.: {value}</p>\n'
        case "arranger":
            return f'    <p class="meta-small">Arr.: {value}</p>\n'
        case "producer":
            return f'    <p class="meta-small">Prod.: {value}</p>\n'
        case "lyricist":
            return f'    <p class="meta-small">Lyr.: {value}</p>\n'
        case "album_name":
            out["album"] = value
            return ""
        case "album_artist":
            out["artist"] = [artist.strip() for artist in value.split(",")]
            out["artist_list"] = ", ".join(f"{artist}" for artist in out["artist"])
            return ""
        case "album_genre":
            out["genre"] = [genre.strip() for genre in value.split(",")]
            out["genre_list"] = ", ".join(f"{genre}" for genre in out["genre"])
            return ""
        case "album_year":
            out["year"] = value
            return ""
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
    og: str = line.group(3)

    output: str = f"""\
  <div class="lyric-box">
    <p class="lyric-time"><i>{timestamp}</i></p>
    <p class="lyric-text">"""

    inside_abbr: bool = False
    for c in lyric:
        if c == "{":
            inside_abbr = True
            output += '<span class="abbr lyric-note" data-title="'
        elif inside_abbr and c == "=":
            output += '">'
        elif inside_abbr and c == "}":
            inside_abbr = False
            output += "</span>"
        else:
            output += c

    output += f"""</p>
    <p class="lyric-og">{og}</p>
  </div>
"""

    return output


def parse_rem_line(line: re.Match) -> str:
    en_reminder: str = line.group(1).strip()
    pt_reminder: str = line.group(2).strip()

    return f"""\
  <div class="lyric-box">
    <p class="lyric-text lyric-command-left">({en_reminder})</p>
    <p class="lyric-og lyric-command-right">({pt_reminder})</p>
  </div>
"""


def parse_spoiler_line(line: re.Match) -> str:
    spoiler_type: str = line.group(1).strip()
    spoiler: str = line.group(2).strip()

    match spoiler_type:
        case "img":
            return f'<div class="spoiler-img">{spoiler}<p class="spoiler-img-info">Hover to reveal</p></div>'
        case "span":
            return f'<span class="spoiler-span">{spoiler}</span>'

    return f'<p class="spoiler-span">{spoiler}</p>'


def parse_line(line: str, out: dict) -> str:
    # Line break?
    if line == "---":
        return "  <hr />\n"

    # Meta box closer?:
    if line == ".end":
        return "  </div>\n"

    # Break in the lyrics?
    if line == "[pause]":
        return "  <br />\n"

    # Instrumental?
    if line == "[instrumental]":
        return '<p class="instrumental">(instrumental)</p>\n'

    # Previous section repeats?
    if line == "[repeat]":
        return """\
  <br />
  <div class="lyric-box">
    <p class="lyric-text lyric-command-left">(repeats until end)</p>
    <p class="lyric-og lyric-command-right">(repete até o final)</p>
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
        return parse_meta_line(meta_line, out)

    # Lyrics line? ([MM:SS] LYRIC)
    if lyric_line := LYRIC_LINE_REGEX.search(line):
        return parse_lyric_line(lyric_line)

    # Reminder line? ([!ENGLISH REMINDER // PORTUGUESE REMINDER])
    if reminder_line := REM_LINE_REGEX.search(line):
        return parse_rem_line(reminder_line)

    inline_pos: int = 0
    inline_str: str = ""

    # Spoiler line? ([?SPOILER TYPE=SPOILER])
    for m in SPOILER_LINE_REGEX.finditer(line):
        inline_str += line[inline_pos : m.start(0)]
        inline_str += parse_spoiler_line(m)
        inline_pos = m.end(0)

    if inline_str:
        return inline_str + line[inline_pos:]

    # Default to a generic paragraph
    return f'<p class="paragraph">{line}</p>'


def generate_lyrics(filename: Path, infile) -> dict:
    lyrics_out: Path = filename.with_suffix(".html")
    lyrics_out = lyrics_out.relative_to("lyrics/")

    out: dict = {}

    with open(lyrics_out, "w") as f:
        output: str = """\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{album} - {artist} lyrics</title>
    <link href="css/style.css" rel="stylesheet" />
  </head>
  <body>
    <script src="js/script.js" defer></script>
    <header>
        <a class="button" id="back-button" href=".">To index</a>
        <button class="button" id="theme-button">Dark</button>
    </header>
    <div id="wrapper">
      <main id="main">
"""
        raw_mode: bool = False
        for line in infile:
            line = line.strip()
            if not line:
                continue

            if line == "===":
                raw_mode = not raw_mode
            elif raw_mode:
                output += line + "\n"
            else:
                output += parse_line(line, out)

        output = output.format(album=out["album"], artist=out["artist_list"])

        f.write(output)
        f.write("      </main>\n")
        f.write("    </div>\n")
        f.write("  </body>\n")
        f.write("</html>")

    return out


def searchify(s: list[str]) -> str:
    search: str = ""

    for term in s:
        search += term
        if (l_term := term.lower()) != term:
            search += l_term

        if (u_term := unidecode(term)) != term:
            search += u_term

            if (lu_term := u_term.lower()) != u_term:
                search += lu_term

    return search


def main() -> None:
    lyrics_folder: Path = Path("lyrics")

    with open("js/db.js", "w") as db:
        db.write("const db = {\n")
        for file in lyrics_folder.glob("*.txt"):
            name: str = file.with_suffix("").name
            db.write(f'\t"{name}": {{\n')

            with open(file) as f:
                out = generate_lyrics(file, f)

            album_name: str = out["album"]
            album_artist: str = ", ".join(f'"{artist}"' for artist in out["artist"])
            album_genre: str = ", ".join(f'"{genre}"' for genre in out["genre"])
            album_year: str = out["year"]

            album_search: str = ""
            album_search += album_name + unidecode(album_name)
            album_search += searchify(out["artist"])
            album_search += searchify(out["genre"])
            album_search += album_year

            db.write(f'\t\t"album": "{album_name}",\n')
            db.write(f'\t\t"artist": [{album_artist}],\n')
            db.write(f'\t\t"genre": [{album_genre}],\n')
            db.write(f'\t\t"year": "{album_year}",\n')
            db.write(f'\t\t"search": "{album_search}",\n')
            db.write("\t},\n")

        db.write("\n}\n")


if __name__ == "__main__":
    main()
