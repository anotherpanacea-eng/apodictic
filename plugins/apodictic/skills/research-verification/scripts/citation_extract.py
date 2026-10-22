"""Conservative, offline citation-surface extraction from supplied Unicode text.

The producer recognizes a deliberately finite grammar. It does not read files,
resolve locators, verify quotations, or infer that an unmatched surface is absent.
All offsets are half-open Python character offsets in the caller's exact string.
"""

from bisect import bisect_right
import re
import unicodedata
from urllib.parse import urlsplit


class CitationExtractionError(ValueError):
    """The supplied text crosses the local extraction boundary."""


_DOI = re.compile(
    r"(?:doi:)?(10\.[0-9]{4,9}/[A-Za-z0-9][A-Za-z0-9._;/:+()\-]{0,255})",
    re.IGNORECASE | re.ASCII,
)
_BIB_PREFIX = re.compile(r"(.{1,64}), ([A-Z])\. \(([0-9]{4}[a-z]?)\)\.(.*)")
_AUTHOR_YEAR = re.compile(r"\(([^,\n]{1,64}), ([0-9]{4}[a-z]?)\)")
_FOOTNOTE = re.compile(r"\^([A-Za-z0-9_-]{1,32})")
_BARE_STOP = set('<>"\'\x60\\')
_TRAILING_PUNCTUATION = set(".,;:!?")
_CLUSTER_GAP = set(" \t,;")


def _span(start, end):
    return {"start": start, "end": end}


def _empty_normalized():
    return {"doi": None, "url": None, "title": None, "author": None, "year": None}


def _escaped(text, index):
    count = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        count += 1
        index -= 1
    return bool(count % 2)


def _mark(mask, start, end):
    mask[start:end] = b"\x01" * (end - start)


def _surname(value):
    return (1 <= len(value) <= 64 and value[0].isalpha()
            and value[-1].isalpha()
            and all(ch.isalpha() or ch in "-'\u2019" for ch in value))


def _year(value):
    return (len(value) in (4, 5) and value[:4].isascii()
            and value[:4].isdigit() and 1000 <= int(value[:4]) <= 2999
            and (len(value) == 4 or "a" <= value[4] <= "z"))


def _doi(value):
    match = _DOI.fullmatch(value)
    if not match:
        return None
    suffix = match.group(1).split("/", 1)[1]
    depth = 0
    for ch in suffix:
        if ch == "(":
            depth += 1
            if depth > 2:
                return None
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return None
    return match.group(1).lower() if depth == 0 else None


def _locator(value):
    doi = _doi(value)
    if doi is not None:
        result = _empty_normalized()
        result["doi"] = doi
        return result
    if not value.lower().startswith(("http://", "https://")):
        return None
    if len(value) > 2048 or not value.isascii():
        return None
    if any(ord(ch) <= 32 or ord(ch) == 127 or ch in '\\\"\'\x60<>[]{}'
           for ch in value):
        return None
    try:
        parsed = urlsplit(value)
        if (parsed.scheme.lower() not in ("http", "https") or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or parsed.netloc.endswith(":")):
            return None
        port = parsed.port
        if port is not None and not 0 <= port <= 65535:
            return None
    except ValueError:
        return None
    result = _empty_normalized()
    result["url"] = value
    if "(" in value or ")" in value:
        if (parsed.hostname.lower() not in ("doi.org", "dx.doi.org")
                or port is not None or parsed.query or parsed.fragment
                or not parsed.path.startswith("/")):
            return None
    if (parsed.hostname.lower() in ("doi.org", "dx.doi.org")
            and port is None and not parsed.query and not parsed.fragment
            and parsed.path.startswith("/")):
        result["doi"] = _doi(parsed.path[1:])
        if ("(" in value or ")" in value) and result["doi"] is None:
            return None
    return result


def _bibliography_prefix(line):
    match = _BIB_PREFIX.fullmatch(line)
    if not match or not _surname(match.group(1)) or not _year(match.group(3)):
        return None
    return (match.group(1), match.group(3)), match.group(4)


def _bibliography(line):
    prefix = _bibliography_prefix(line)
    if prefix is None:
        return None
    key, rest = prefix
    if not rest.startswith(" "):
        return key, None
    body = rest[1:]
    divider = body.rfind(". ")
    if divider < 1:
        return key, None
    title = body[:divider]
    if (len(title) > 512 or title != title.strip()
            or any(unicodedata.category(ch) == "Cc" for ch in title)):
        return key, None
    normalized = _locator(body[divider + 2:])
    if normalized is None:
        return key, None
    normalized["title"] = title
    normalized["author"], normalized["year"] = key
    return key, normalized


def _footnote_body(body):
    if not body.startswith(" "):
        return None
    body = body[1:]
    direct = _locator(body)
    if direct is not None:
        return direct
    bibliography = _bibliography(body)
    return bibliography[1] if bibliography else None


def _lines(text):
    lines = []
    pos = 0
    while pos < len(text):
        newline = text.find("\n", pos)
        end = len(text) if newline < 0 else newline
        full_end = end if newline < 0 else end + 1
        lines.append((pos, end, full_end))
        pos = full_end
    return lines


def _code_mask(text, lines):
    mask = bytearray(len(text))
    fence_char = None
    fence_length = 0
    for start, end, full_end in lines:
        line = text[start:end]
        indent = len(line) - len(line.lstrip(" "))
        marker = line[indent:indent + 1] if indent <= 3 else ""
        run_end = indent
        if marker in ("`", "~"):
            while run_end < len(line) and line[run_end] == marker:
                run_end += 1
        run_length = run_end - indent
        if fence_char is not None:
            _mark(mask, start, full_end)
            if (indent <= 3 and marker == fence_char
                    and run_length >= fence_length
                    and not line[run_end:].strip(" \t")):
                fence_char = None
            continue
        if indent <= 3 and marker in ("`", "~") and run_length >= 3:
            fence_char, fence_length = marker, run_length
            _mark(mask, start, full_end)
            continue
        pos = start
        while pos < end:
            if text[pos] != "`" or _escaped(text, pos):
                pos += 1
                continue
            run_end = pos + 1
            while run_end < end and text[run_end] == "`":
                run_end += 1
            width = run_end - pos
            close = run_end
            matched = False
            while close < end:
                if text[close] != "`":
                    close += 1
                    continue
                close_end = close + 1
                while close_end < end and text[close_end] == "`":
                    close_end += 1
                if close_end - close == width:
                    _mark(mask, pos, close_end)
                    pos = close_end
                    matched = True
                    break
                close = close_end
            if not matched:
                _mark(mask, pos, end)
                break
    return mask


def _paragraphs(text, lines):
    starts = [start for start, _, _ in lines]
    by_line = [None] * len(lines)
    index = 0
    while index < len(lines):
        start, end, _ = lines[index]
        if not text[start:end].strip(" \t"):
            index += 1
            continue
        last = index
        while (last + 1 < len(lines)
               and text[lines[last + 1][0]:lines[last + 1][1]].strip(" \t")):
            last += 1
        corridor = _span(start, lines[last][1])
        for current in range(index, last + 1):
            by_line[current] = corridor
        index = last + 1
    return starts, by_line


def _new_record(text, kind, start, end, normalized=None, *,
                reason=None, definition=None, corridor=None):
    return {
        "kind": kind,
        "status": "ambiguous" if reason else "extracted",
        "reason": reason,
        "span": _span(start, end),
        "raw_citation_text": text[start:end],
        "normalized_citation": normalized if normalized is not None else _empty_normalized(),
        "definition_span": definition,
        "quote_span": None,
        "claim_corridor_span": corridor,
        "attachment_method": "paragraph" if corridor is not None else "none",
    }


def _definition_like(text, start, end):
    opener = start
    while opener < end and text[opener] in " \t":
        opener += 1
    if opener >= end or text[opener] != "[":
        return False
    pos = opener + 1
    while pos < end:
        if text[pos] == "]" and not _escaped(text, pos):
            return pos + 1 < end and text[pos + 1] == ":"
        pos += 1
    return False


def _references_and_definitions(text, lines, mask):
    references = {}
    footnotes = {}
    reference_line = len(lines)
    for index, (start, end, _) in enumerate(lines):
        if not mask[start] and text[start:end] in ("References", "## References"):
            reference_line = index
            break
    for start, end, _ in lines[reference_line + 1:]:
        if mask[start]:
            continue
        candidate = _bibliography(text[start:end])
        if candidate:
            key, normalized = candidate
            references.setdefault(key, []).append((normalized, _span(start, end)))
    if reference_line < len(lines):
        _mark(mask, lines[reference_line][0], len(text))
    index = 0
    while index < reference_line:
        start, end, full_end = lines[index]
        if mask[start] or not _definition_like(text, start, end):
            index += 1
            continue
        after = index + 1
        while after < reference_line:
            next_start, next_end, _ = lines[after]
            content = text[next_start:next_end]
            if content.startswith("\t") or content.startswith("    "):
                after += 1
            else:
                break
        block_end = lines[after - 1][2] if after > index + 1 else full_end
        line = text[start:end]
        match = re.match(r"\[\^([A-Za-z0-9_-]{1,32})\]:(.*)", line)
        if match:
            normalized = None if after > index + 1 else _footnote_body(match.group(2))
            footnotes.setdefault(match.group(1), []).append((normalized, _span(start, end)))
        _mark(mask, start, block_end)
        index = after
    return references, footnotes


def _brackets(text, lines, base_mask, paragraph_starts, paragraph_by_line, footnotes):
    mask = bytearray(len(text))
    surfaces = []

    def footnote(start, end, label):
        options = footnotes.get(label, [])
        if not options:
            return _new_record(text, "footnote", start, end, reason="missing_definition")
        if len(options) > 1:
            return _new_record(text, "footnote", start, end, reason="multiple_definitions")
        normalized, definition = options[0]
        if normalized is None:
            return _new_record(text, "footnote", start, end, reason="unsupported_definition")
        return _new_record(text, "footnote", start, end,
                           normalized=normalized.copy(), definition=definition)

    for line_start, line_end, _ in lines:
        pos = line_start
        while pos < line_end:
            if text[pos] != "[" or base_mask[pos]:
                pos += 1
                continue
            opener = pos
            cursor = pos + 1
            bad = False
            while cursor < line_end and text[cursor] != "]":
                if text[cursor] in "[\\()":
                    bad = True
                    break
                cursor += 1
            if bad or cursor == line_end:
                _mark(mask, opener, line_end)
                surfaces.append((opener, line_end, None))
                break
            first_end = cursor + 1
            first_body = text[opener + 1:cursor]
            escaped = _escaped(text, opener)
            image = (opener > 0 and text[opener - 1] == "!"
                     and not _escaped(text, opener - 1))
            if first_end < line_end and text[first_end] == "(":
                cursor = first_end + 1
                depth = 1
                bad = False
                while cursor < line_end:
                    ch = text[cursor]
                    if ch in "\\[]":
                        bad = True
                        break
                    if ch == "(":
                        depth += 1
                        if depth > 3:
                            bad = True
                            break
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    cursor += 1
                if bad or cursor == line_end:
                    end = line_end
                    record = None
                else:
                    end = cursor + 1
                    destination = text[first_end + 1:cursor]
                    normalized = _locator(destination)
                    valid_label = (1 <= len(first_body) <= 200
                                   and first_body == first_body.strip(" \t")
                                   and "`" not in first_body)
                    record = None
                    if not escaped and not image and valid_label and normalized:
                        line_index = bisect_right(paragraph_starts, opener) - 1
                        record = _new_record(
                            text, "markdown_link", opener, end, normalized,
                            corridor=paragraph_by_line[line_index])
                _mark(mask, opener, end)
                surfaces.append((opener, end, record))
                pos = end
                continue
            if first_end < line_end and text[first_end] == "[":
                second_start = first_end
                cursor = second_start + 1
                bad = False
                while cursor < line_end and text[cursor] != "]":
                    if text[cursor] in "[\\()":
                        bad = True
                        break
                    cursor += 1
                if bad or cursor == line_end:
                    _mark(mask, opener, line_end)
                    surfaces.append((opener, line_end, None))
                    break
                second_end = cursor + 1
                second_body = text[second_start + 1:cursor]
                first_label = _FOOTNOTE.fullmatch(first_body)
                second_label = _FOOTNOTE.fullmatch(second_body)
                if first_label and second_label and not escaped and not image:
                    _mark(mask, opener, second_end)
                    surfaces.append((opener, first_end,
                                     footnote(opener, first_end, first_label.group(1))))
                    surfaces.append((second_start, second_end,
                                     footnote(second_start, second_end, second_label.group(1))))
                else:
                    _mark(mask, opener, second_end)
                    surfaces.append((opener, second_end, None))
                pos = second_end
                continue
            match = _FOOTNOTE.fullmatch(first_body)
            record = (footnote(opener, first_end, match.group(1))
                      if match and not escaped and not image else None)
            _mark(mask, opener, first_end)
            surfaces.append((opener, first_end, record))
            pos = first_end
    return mask, surfaces


def _quotes(text, lines, base_mask, bracket_mask):
    mask = bytearray(len(text))
    quotes = []
    for start, end, _ in lines:
        pos = start
        while pos < end:
            ch = text[pos]
            if (ch not in ('"', "\u201c") or base_mask[pos]
                    or bracket_mask[pos] or _escaped(text, pos)):
                pos += 1
                continue
            closer = '"' if ch == '"' else "\u201d"
            cursor = pos + 1
            found = False
            while cursor < end:
                candidate = text[cursor]
                if (base_mask[cursor] or bracket_mask[cursor]
                        or _escaped(text, cursor)):
                    cursor += 1
                    continue
                if candidate == closer:
                    found = True
                    break
                if candidate in ('"', "\u201c", "\u201d"):
                    break
                cursor += 1
            if found:
                _mark(mask, pos, cursor + 1)
                if cursor > pos + 1:
                    quotes.append((pos + 1, cursor, cursor + 1))
                pos = cursor + 1
            else:
                _mark(mask, pos, end)
                break
    return mask, quotes


def _trim_bare(token):
    end = len(token)
    counts = {ch: token.count(ch) for ch in "()[]{}"}
    while end:
        ch = token[end - 1]
        if ch in _TRAILING_PUNCTUATION:
            end -= 1
            continue
        if ch in ")]}":
            opening = {")": "(", "]": "[", "}": "{"}[ch]
            if counts[ch] > counts[opening]:
                counts[ch] -= 1
                end -= 1
                continue
        break
    return token[:end]


def _bare_prefix(text, pos):
    return (text[pos:pos + 4].lower() == "doi:" or text.startswith("10.", pos)
            or text[pos:pos + 7].lower() == "http://"
            or text[pos:pos + 8].lower() == "https://")


def _surface_scan(text, base_mask, bracket_mask, quote_mask, references,
                  paragraph_starts, paragraph_by_line, surfaces):
    pos = 0
    size = len(text)
    while pos < size:
        if base_mask[pos] or bracket_mask[pos] or quote_mask[pos]:
            pos += 1
            continue
        if text[pos] == "(" and not _escaped(text, pos):
            match = _AUTHOR_YEAR.match(text, pos)
            if match and _surname(match.group(1)) and _year(match.group(2)):
                end = match.end()
                if not (1 in base_mask[pos:end] or 1 in bracket_mask[pos:end]
                        or 1 in quote_mask[pos:end]):
                    key = match.group(1), match.group(2)
                    options = references.get(key, [])
                    if not options:
                        record = None
                    elif len(options) > 1:
                        normalized = _empty_normalized()
                        normalized["author"], normalized["year"] = key
                        record = _new_record(
                            text, "author_year", pos, end, normalized,
                            reason="multiple_definitions")
                    else:
                        normalized, definition = options[0]
                        if normalized is None:
                            only_key = _empty_normalized()
                            only_key["author"], only_key["year"] = key
                            record = _new_record(
                                text, "author_year", pos, end, only_key,
                                reason="unsupported_definition")
                        else:
                            line_index = bisect_right(paragraph_starts, pos) - 1
                            record = _new_record(
                                text, "author_year", pos, end, normalized.copy(),
                                definition=definition,
                                corridor=paragraph_by_line[line_index])
                    surfaces.append((pos, end, record))
                    pos = end
                    continue
        if _bare_prefix(text, pos):
            end = pos
            while end < size and not text[end].isspace() and text[end] not in _BARE_STOP:
                end += 1
            token = _trim_bare(text[pos:end])
            emission_end = pos + len(token)
            boundary = (pos == 0 or not (text[pos - 1].isalnum()
                        or text[pos - 1] in "_/" or _escaped(text, pos)))
            normalized = _locator(token) if boundary else None
            record = None
            if (normalized is not None and emission_end > pos
                    and not (1 in base_mask[pos:emission_end]
                             or 1 in bracket_mask[pos:emission_end]
                             or 1 in quote_mask[pos:emission_end])):
                kind = "url" if normalized["url"] is not None else "doi"
                line_index = bisect_right(paragraph_starts, pos) - 1
                record = _new_record(
                    text, kind, pos, emission_end, normalized,
                    corridor=paragraph_by_line[line_index])
            surfaces.append((pos, max(emission_end, pos + 1), record))
            pos = max(end, pos + 1)
            continue
        pos += 1


def _associate_quotes(text, surfaces, quotes):
    surfaces.sort(key=lambda surface: (surface[0], surface[1]))
    quote_ends = [end for _, _, end in quotes]
    records = []
    group_start = 0
    for index, (start, end, record) in enumerate(surfaces):
        if index and any(ch not in _CLUSTER_GAP for ch in
                         text[surfaces[index - 1][1]:start]):
            group_start = index
        next_cluster = (index + 1 < len(surfaces)
                        and all(ch in _CLUSTER_GAP
                                for ch in text[end:surfaces[index + 1][0]]))
        if record is None:
            continue
        if (record["status"] == "extracted" and group_start == index
                and not next_cluster):
            quote_index = bisect_right(quote_ends, start) - 1
            if quote_index >= 0:
                quote_start, quote_end, close_end = quotes[quote_index]
                if all(ch in " \t" for ch in text[close_end:start]):
                    record["quote_span"] = _span(quote_start, quote_end)
        records.append(record)
    return records


def extract_citations(text: str, *, media_type: str = "text/markdown") -> dict:
    """Return admitted citation surfaces and syntactically associated quote spans."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if not isinstance(media_type, str):
        raise TypeError("media_type must be str")
    if len(text) > 1_000_000:
        raise CitationExtractionError("text exceeds extraction limit")
    if "\r" in text or any(0xD800 <= ord(ch) <= 0xDFFF for ch in text):
        raise CitationExtractionError("text must be LF-normalized Unicode scalar content")
    result = {"schema_version": 1, "grammar": "m1-local-v1",
              "status": "no_matches", "coverage": "admitted_syntax_only",
              "citations": []}
    if media_type not in ("text/plain", "text/markdown"):
        result["status"] = "unsupported_format"
        return result
    if not text:
        return result
    lines = _lines(text)
    base_mask = _code_mask(text, lines)
    references, footnotes = _references_and_definitions(text, lines, base_mask)
    paragraph_starts, paragraph_by_line = _paragraphs(text, lines)
    bracket_mask, surfaces = _brackets(
        text, lines, base_mask, paragraph_starts, paragraph_by_line, footnotes)
    quote_mask, quotes = _quotes(text, lines, base_mask, bracket_mask)
    surfaces = [surface for surface in surfaces
                if 1 not in quote_mask[surface[0]:surface[1]]]
    _surface_scan(text, base_mask, bracket_mask, quote_mask, references,
                  paragraph_starts, paragraph_by_line, surfaces)
    result["citations"] = _associate_quotes(text, surfaces, quotes)
    if result["citations"]:
        result["status"] = "recognized_surfaces"
    return result
