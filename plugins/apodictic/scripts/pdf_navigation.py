"""Offline exact geometry for the opt-in PDF navigation projection.

Coordinates use integer thousandths of a point. No platform font queries,
width heuristics, rounding, or runtime downloads are involved.
"""
from functools import lru_cache
from pathlib import Path
import json
import re
from collections import namedtuple
from decimal import Decimal

Ref = namedtuple("Ref", "number generation")
Stream = namedtuple("Stream", "attributes data")


class Name(str):
    """PDF names are distinct from literal string data."""


class NavigationRefusal(ValueError):
    """A named geometry/input refusal; messages must not include source prose."""


class MetricsUnavailable(NavigationRefusal):
    """Installed pinned metric inputs cannot be verified."""


@lru_cache(maxsize=1)
def metrics():
    root = Path(__file__).resolve().parent / "pdf_metrics"
    try:
        table = json.loads((root / "helvetica-winansi.json").read_bytes())
        if (not isinstance(table, dict) or set(table) != {"schema", "sources", "notice", "glyphs"}
                or table["schema"] != "apodictic.helvetica-winansi-metrics.v1"):
            raise MetricsUnavailable("N metrics schema or shape")
        # Source filenames come only from the pinned recipe, never the mutable
        # table. Regeneration verifies the exact roster and checksums before use.
        import importlib.util
        spec = importlib.util.spec_from_file_location("_apodictic_pdf_metrics", root / "generate.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if table["sources"] != module.SOURCES:
            raise MetricsUnavailable("N metrics source roster")
        expected = module.generate()
        if table != expected:
            raise MetricsUnavailable("N derived metrics mismatch")
        return expected["glyphs"]
    except MetricsUnavailable:
        raise
    except (OSError, UnicodeError, ValueError, TypeError, AttributeError, KeyError, ImportError):
        raise MetricsUnavailable("N metrics unavailable or malformed") from None


def _glyphs(text):
    try:
        encoded = text.encode("cp1252")
    except (AttributeError, UnicodeEncodeError):
        raise NavigationRefusal("N unsupported glyph encoding") from None
    table = metrics()
    for byte in encoded:
        glyph = table.get(str(byte))
        if glyph is None:
            raise NavigationRefusal("N control or undefined glyph")
        yield glyph


def advance(text):
    """Exact advance at size 11; prefix ink does not define a hit region."""
    return sum(11 * glyph["advance"] for glyph in _glyphs(text))


def ink_rectangle(text, prefix, item_index):
    """Smallest translated ink bounding box, or None for mapped whitespace.

    Every glyph in the linked text requires trustworthy ink, except explicitly
    mapped whitespace. Prefixes require known advances, including whitespace.
    """
    if type(item_index) is not int or item_index < 0:
        raise NavigationRefusal("N invalid emitted item index")
    x = 72000 + advance(prefix)
    baseline = (734 - 14 * (item_index % 45 + 1)) * 1000
    boxes = []
    for glyph in _glyphs(text):
        left, bottom, right, top = glyph["box"]
        if not glyph["whitespace"]:
            if right <= left or top <= bottom:
                raise NavigationRefusal("N non-whitespace glyph lacks ink bounds")
            boxes.append((x + 11 * left, baseline + 11 * bottom,
                          x + 11 * right, baseline + 11 * top))
        x += 11 * glyph["advance"]
    if not boxes:
        return None
    rect = (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))
    require_contained(rect)
    return rect


def require_contained(rect):
    if len(rect) != 4 or any(type(n) is not int for n in rect):
        raise NavigationRefusal("N invalid exact rectangle")
    left, bottom, right, top = rect
    if not (0 <= left < right <= 612000 and 0 <= bottom < top <= 792000):
        raise NavigationRefusal("N empty or clipped hit rectangle")


def overlaps(a, b):
    """Positive-area intersection only; boundary touching is permitted."""
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def decimal(value):
    """Exact PDF decimal spelling from integer thousandths of a point."""
    if type(value) is not int:
        raise NavigationRefusal("N invalid exact coordinate")
    sign = "-" if value < 0 else ""
    whole, fraction = divmod(abs(value), 1000)
    return sign + str(whole) + ((".%03d" % fraction).rstrip("0") if fraction else "")


def layout(snapshot, annotations, title, insertion_offsets, fid_sort_key):
    """Authoritative emitted sequence and owned hit regions from insertion records.

    The exporter supplies gated offsets and its existing finding sort key.
    Finding identity never comes from searching comment text. Each link tuple
    contains (finding_id, source_item, source_rect, destination_item, dest_rect).
    """
    if not isinstance(snapshot, str) or not isinstance(annotations, list):
        raise NavigationRefusal("N malformed layout input")
    if len(annotations) != len(insertion_offsets):
        raise NavigationRefusal("N missing insertion ownership")
    records = []
    seen = set()
    for annotation, offset in zip(annotations, insertion_offsets):
        if not isinstance(annotation, dict):
            raise NavigationRefusal("N malformed annotation")
        fid = annotation.get("finding_id")
        if not isinstance(fid, str) or not re.fullmatch(r"F-[A-Za-z0-9]+-[0-9]{2,}", fid) or fid in seen:
            raise NavigationRefusal("N malformed or duplicate finding identity")
        seen.add(fid)
        comment = annotation.get("comment")
        if not isinstance(comment, str) or not comment.strip() or "\n" in comment or "\r" in comment:
            raise NavigationRefusal("N comment has no single-line visible destination: " + fid)
        if type(offset) is not int or not 0 <= offset <= len(snapshot):
            raise NavigationRefusal("N invalid insertion offset: " + fid)
        if "[" + fid + "]" in snapshot:
            raise NavigationRefusal("N snapshot already contains marker: " + fid)
        records.append((offset, fid, annotation))
    # Ascending assembly has the same final splice order as descending insertion
    # in the legacy exporter, including adjacent co-located finding markers.
    pieces, markers, consumed, length = [], [], 0, 0
    for offset, fid, annotation in sorted(records, key=lambda r: (r[0], fid_sort_key(r[1]) or "")):
        text = snapshot[consumed:offset]
        pieces.append(text)
        length += len(text)
        marker = "[" + fid + "]"
        markers.append((fid, length, marker))
        pieces.append(marker)
        length += len(marker)
        consumed = offset
    pieces.append(snapshot[consumed:])
    marked = "".join(pieces)
    lines = marked.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    original_lines = snapshot.split("\n")
    if original_lines and original_lines[-1] == "":
        original_lines.pop()
    if len(lines) != len(original_lines):
        raise NavigationRefusal("N marker would create an unbound manuscript line")
    items = [("show", title), ("skip",)] + [("show", line) for line in lines]
    items += [("skip",), ("show", "Findings"), ("skip",)]
    marker_regions = {}
    for fid, position, marker in markers:
        line_number = marked.count("\n", 0, position)
        start = marked.rfind("\n", 0, position) + 1
        item = 2 + line_number
        marker_regions[fid] = (item, ink_rectangle(marker, marked[start:position], item))
    comment_regions = {}
    for annotation in sorted(annotations, key=lambda a: fid_sort_key(a["finding_id"]) or ""):
        fid, comment = annotation["finding_id"], annotation["comment"]
        regions = []
        for offset in range(0, len(comment), 90):
            chunk = comment[offset:offset + 90]
            item = len(items)
            rect = ink_rectangle(chunk, "", item)
            items.append(("show", chunk))
            if rect is not None:
                regions.append((item, rect))
        items.append(("skip",))
        if not regions:
            raise NavigationRefusal("N comment lacks trustworthy visible ink: " + fid)
        comment_regions[fid] = regions
    links = []
    for fid, marker in marker_regions.items():
        destination = comment_regions[fid][0]
        links.append((fid, *marker, *destination))
        for chunk in comment_regions[fid]:
            links.append((fid, *chunk, *marker))
    links.sort(key=lambda link: (link[1], link[2][0], link[2][1], fid_sort_key(link[0]) or ""))
    per_page = {}
    for fid, item, rect, target_item, target_rect in links:
        page_regions = per_page.setdefault(item // 45, [])
        if any(overlaps(rect, other) for other in page_regions):
            raise NavigationRefusal("N overlapping hit rectangles: " + fid)
        page_regions.append(rect)
    return items, links


class _Parser:
    """Bounded parser for the uncompressed PDF 1.4 dialect emitted here.

    Streams are consumed by their declared Length, never an endobj/endstream
    regex. Literal strings are data, so action-looking prose is not an action.
    """
    def __init__(self, data, position=0):
        self.data, self.position = data, position

    def whitespace(self):
        while self.position < len(self.data):
            if self.data[self.position] in b" \t\r\n\f\x00":
                self.position += 1
            elif self.data[self.position:self.position + 1] == b"%":
                end = self.data.find(b"\n", self.position)
                self.position = len(self.data) if end < 0 else end + 1
            else:
                break

    def take(self, token):
        if not self.data.startswith(token, self.position):
            raise NavigationRefusal("N PDF syntax")
        self.position += len(token)

    def value(self, depth=0):
        if depth > 64:
            raise NavigationRefusal("N PDF nesting limit")
        self.whitespace()
        if self.data.startswith(b"<<", self.position):
            self.position += 2
            result = {}
            while True:
                self.whitespace()
                if self.data.startswith(b">>", self.position):
                    self.position += 2
                    return result
                key = self.value(depth + 1)
                if not isinstance(key, Name) or key in result:
                    raise NavigationRefusal("N duplicate or invalid PDF dictionary key")
                result[key] = self.value(depth + 1)
        if self.data.startswith(b"[", self.position):
            self.position += 1
            result = []
            while True:
                self.whitespace()
                if self.data.startswith(b"]", self.position):
                    self.position += 1
                    return result
                result.append(self.value(depth + 1))
        if self.data.startswith(b"/", self.position):
            self.position += 1
            match = re.match(rb"[^\s\x00()<>\[\]{}/%]+", self.data[self.position:])
            if match is None:
                raise NavigationRefusal("N empty PDF name")
            raw = match.group()
            self.position += len(raw)
            if re.search(rb"#(?![0-9A-Fa-f]{2})", raw):
                raise NavigationRefusal("N malformed PDF name escape")
            raw = re.sub(rb"#([0-9A-Fa-f]{2})", lambda m: bytes([int(m[1], 16)]), raw)
            return Name(raw.decode("latin-1"))
        if self.data.startswith(b"(", self.position):
            self.position += 1
            nesting, result = 1, bytearray()
            while self.position < len(self.data):
                byte = self.data[self.position]
                self.position += 1
                if byte == 92:
                    if self.position >= len(self.data):
                        break
                    following = self.data[self.position]
                    self.position += 1
                    if 48 <= following <= 55:
                        digits = bytes([following])
                        while len(digits) < 3 and self.position < len(self.data) and 48 <= self.data[self.position] <= 55:
                            digits += self.data[self.position:self.position + 1]
                            self.position += 1
                        result.append(int(digits, 8) & 255)
                    elif following in (10, 13):
                        if following == 13 and self.data[self.position:self.position + 1] == b"\n":
                            self.position += 1
                    else:
                        result.append({110: 10, 114: 13, 116: 9, 98: 8, 102: 12}.get(following, following))
                elif byte == 40:
                    nesting += 1
                    result.append(byte)
                elif byte == 41:
                    nesting -= 1
                    if nesting == 0:
                        return bytes(result)
                    result.append(byte)
                else:
                    result.append(byte)
            raise NavigationRefusal("N unterminated PDF literal")
        match = re.match(rb"(?:[-+]?(?:\d+\.\d*|\.\d+|\d+)|null|true|false)(?=[\s\x00()<>\[\]{}/%]|$)",
                         self.data[self.position:])
        if match is None:
            raise NavigationRefusal("N unsupported PDF value")
        token = match.group()
        self.position += len(token)
        if token in (b"null", b"true", b"false"):
            return {b"null": None, b"true": True, b"false": False}[token]
        if b"." in token:
            return Decimal(token.decode("ascii"))
        number = int(token)
        reference = re.match(rb"\s+(\d+)\s+R(?=[\s\x00()<>\[\]{}/%]|$)", self.data[self.position:])
        if reference:
            self.position += len(reference.group())
            return Ref(number, int(reference[1]))
        return number


def parse_pdf(data):
    """Validate xref, exact object boundaries and stream lengths independently."""
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    if not isinstance(data, bytes) or not data.startswith(header):
        raise NavigationRefusal("N PDF 1.4 header")
    ending = re.search(rb"\nstartxref\n(\d+)\n%%EOF\n\Z", data)
    if not ending:
        raise NavigationRefusal("N PDF final trailer")
    xref_offset = int(ending[1])
    parser = _Parser(data, xref_offset)
    parser.take(b"xref\n0 ")
    match = re.match(rb"(\d+)\n", data[parser.position:])
    if not match:
        raise NavigationRefusal("N xref subsection")
    count = int(match[1])
    if not 2 <= count <= len(data) // 20:
        raise NavigationRefusal("N xref size")
    parser.position += len(match.group())
    parser.take(b"0000000000 65535 f\r\n")
    offsets = []
    for _ in range(1, count):
        match = re.match(rb"(\d{10}) 00000 n\r\n", data[parser.position:])
        if not match:
            raise NavigationRefusal("N xref entry")
        offsets.append(int(match[1]))
        parser.position += len(match.group())
    parser.take(b"trailer\n")
    trailer = parser.value()
    if trailer != {"Size": count, "Root": Ref(1, 0)} or set(trailer) != {"Size", "Root"}:
        raise NavigationRefusal("N trailer identity or extra fields")
    if parser.position != ending.start():
        raise NavigationRefusal("N trailer boundary")
    if offsets != sorted(set(offsets)) or offsets[0] != len(header) or offsets[-1] >= xref_offset:
        raise NavigationRefusal("N xref offset ownership")
    objects = {}
    for number, offset in enumerate(offsets, 1):
        parser = _Parser(data, offset)
        parser.take(("%d 0 obj\n" % number).encode("ascii"))
        obj = parser.value()
        if data.startswith(b"\nstream\n", parser.position):
            if not isinstance(obj, dict) or type(obj.get("Length")) is not int or obj["Length"] < 0:
                raise NavigationRefusal("N stream Length")
            parser.take(b"\nstream\n")
            end = parser.position + obj["Length"]
            if end > xref_offset:
                raise NavigationRefusal("N stream Length outside body")
            stream = data[parser.position:end]
            parser.position = end
            parser.take(b"\nendstream")
            obj = Stream(obj, stream)
        parser.take(b"\nendobj\n")
        next_offset = offsets[number] if number < len(offsets) else xref_offset
        if parser.position != next_offset:
            raise NavigationRefusal("N object boundary or unreferenced bytes")
        objects[number] = obj
    return objects


def _forbidden(value):
    if isinstance(value, Stream):
        return _forbidden(value.attributes)
    if isinstance(value, dict):
        return any(key in ("A", "AA", "JS", "JavaScript", "Launch", "URI", "QuadPoints")
                   or _forbidden(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_forbidden(item) for item in value)
    return isinstance(value, Name) and value in ("JavaScript", "Launch", "URI", "GoToR", "GoToE")


def check_structure(data, expected_streams, links):
    """Verify actual objects against authoritative item/region ownership.

    This runs independently of fresh-byte equality. It never accepts a PDF
    manifest, sidecar or link dictionary's claim about its own finding identity.
    """
    try:
        objects = parse_pdf(data)
        if any(_forbidden(obj) for obj in objects.values()):
            raise NavigationRefusal("N forbidden action or annotation feature")
        if objects.get(1) != {"Type": Name("Catalog"), "Pages": Ref(2, 0)}:
            raise NavigationRefusal("N catalog")
        tree = objects.get(2)
        if not isinstance(tree, dict) or set(tree) != {"Type", "Kids", "Count"} or tree["Type"] != Name("Pages"):
            raise NavigationRefusal("N page tree")
        pages = tree["Kids"]
        if not isinstance(pages, list) or len(pages) != len(expected_streams) or type(tree["Count"]) is not int or tree["Count"] != len(pages):
            raise NavigationRefusal("N page count")
        if any(not isinstance(ref, Ref) or ref.generation != 0 for ref in pages) or len(set(pages)) != len(pages):
            raise NavigationRefusal("N page references")
        if [ref.number for ref in pages] != [3 + 2 * index for index in range(len(pages))]:
            raise NavigationRefusal("N deterministic page object order")
        visited, annotation_refs = {1, 2}, []
        font_reference = None
        for index, ref in enumerate(pages):
            page = objects.get(ref.number)
            owned = [link for link in links if link[1] // 45 == index]
            keys = {"Type", "Parent", "MediaBox", "Resources", "Contents"} | ({"Annots"} if owned else set())
            if not isinstance(page, dict) or set(page) != keys or page["Type"] != Name("Page") or page["Parent"] != Ref(2, 0):
                raise NavigationRefusal("N page dictionary or link ownership")
            if not isinstance(page["MediaBox"], list) or any(type(n) not in (int, Decimal) for n in page["MediaBox"]) or page["MediaBox"] != [0, 0, 612, 792]:
                raise NavigationRefusal("N MediaBox")
            resources = page["Resources"]
            if not isinstance(resources, dict) or set(resources) != {"Font"} or not isinstance(resources["Font"], dict) or set(resources["Font"]) != {"F1"}:
                raise NavigationRefusal("N font resource")
            font = resources["Font"]["F1"]
            if not isinstance(font, Ref) or font.generation != 0 or (font_reference is not None and font != font_reference):
                raise NavigationRefusal("N font reference")
            font_reference = font
            content_ref = page["Contents"]
            if not isinstance(content_ref, Ref) or content_ref.generation != 0:
                raise NavigationRefusal("N content reference")
            if content_ref.number != ref.number + 1 or font.number != 3 + 2 * len(pages):
                raise NavigationRefusal("N deterministic content/font object order")
            stream = objects.get(content_ref.number)
            if not isinstance(stream, Stream) or set(stream.attributes) != {"Length"} or stream.data != expected_streams[index]:
                raise NavigationRefusal("N page text state or content fidelity")
            visited.update((ref.number, content_ref.number, font.number))
            refs = page.get("Annots", [])
            if not isinstance(refs, list) or len(refs) != len(owned):
                raise NavigationRefusal("N forward/return coverage")
            for link_ref, (fid, item, rect, target_item, target_rect) in zip(refs, owned):
                if not isinstance(link_ref, Ref) or link_ref.generation != 0 or link_ref in annotation_refs:
                    raise NavigationRefusal("N duplicated or invalid link reference: " + fid)
                annotation_refs.append(link_ref)
                link = objects.get(link_ref.number)
                required = {"Type", "Subtype", "Rect", "Border", "Dest"}
                if not isinstance(link, dict) or set(link) != required or link["Type"] != Name("Annot") or link["Subtype"] != Name("Link"):
                    raise NavigationRefusal("N link dictionary: " + fid)
                exact_rect = [Decimal(value).scaleb(-3) for value in rect]
                if (not isinstance(link["Rect"], list) or any(type(n) not in (int, Decimal) for n in link["Rect"])
                        or not isinstance(link["Border"], list) or any(type(n) not in (int, Decimal) for n in link["Border"])
                        or link["Rect"] != exact_rect or link["Border"] != [0, 0, 0]):
                    raise NavigationRefusal("N hit geometry: " + fid)
                destination = [pages[target_item // 45], Name("XYZ"),
                               Decimal(target_rect[0]).scaleb(-3), Decimal(target_rect[3]).scaleb(-3), None]
                if (not isinstance(link["Dest"], list) or len(link["Dest"]) != 5
                        or any(type(link["Dest"][n]) not in (int, Decimal) for n in (2, 3))
                        or link["Dest"] != destination):
                    raise NavigationRefusal("N destination identity or geometry: " + fid)
                visited.add(link_ref.number)
        if font_reference is None or objects.get(font_reference.number) != {
                "Type": Name("Font"), "Subtype": Name("Type1"), "BaseFont": Name("Helvetica"), "Encoding": Name("WinAnsiEncoding")}:
            raise NavigationRefusal("N Helvetica font")
        if set(objects) != visited:
            raise NavigationRefusal("N orphan or extra objects")
        if [ref.number for ref in annotation_refs] != list(range(font_reference.number + 1, font_reference.number + 1 + len(links))):
            raise NavigationRefusal("N deterministic link object order")
        return []
    except (NavigationRefusal, KeyError, TypeError, ValueError, IndexError, ArithmeticError) as exc:
        return [str(exc) if isinstance(exc, NavigationRefusal) else "N malformed PDF structure"]
