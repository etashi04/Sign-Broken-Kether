# rc48 candidate: center digits and body symbols against actual same-line Hangul ink.
# Keep existing Latin baselines, font weights, advances and shader animation.
# rc45: cache nickname style ancestry and skip unneeded ordinary ink-offset scans.
# rc42: center nickname brackets and digits against the adjacent Korean ink.
# rc39: include digits in the existing mixed-Korean baseline correction.
# rc26: Latin ink up 3px at33px; corner quotes gain2px only inward.
# Keep native characters, quote line-break classes and reveal timing intact.
init 225 python:
    import builtins as _ko_latin_builtins
    import re as _ko_latin_re
    from renpy.text.text import Layout as _ko_latin_Layout, TextSegment as _ko_latin_Segment
    from renpy.text.textsupport import TEXT as _ko_latin_TEXT

    if not hasattr(_ko_latin_Layout, "_etashi_latin_init"):
        _ko_latin_Layout._etashi_latin_init = staticmethod(_ko_latin_Layout.__init__)
        _ko_latin_Layout._etashi_quote_paragraph = staticmethod(_ko_latin_Layout.glyphs_paragraph)
    if not hasattr(_ko_latin_Segment, "_etashi_latin_draw"):
        _ko_latin_Segment._etashi_latin_draw = staticmethod(_ko_latin_Segment.draw)
        _ko_latin_Segment._etashi_latin_bounds = staticmethod(_ko_latin_Segment.bounds)

    _ko_latin_regular_faces = frozenset((
        "fonts/ChillRoundFRegular.otf", "ChillRoundFRegular.otf",
        "fonts/ko/GowunDodum-Regular.ttf",
        "SourceHanSerifSC-Regular.otf", "fonts/SourceHanSerifSC-Regular.otf",
        "SourceHanSansLite.ttf", "fonts/SourceHanSansLite.ttf",
    ))

    _ko_nickname_style_cache = _ko_latin_builtins.dict()

    def _ko_nickname_style_clear():
        _ko_nickname_style_cache.clear()

    def _ko_nickname_style_matches(text_style):
        # Anonymous displayable properties do not alter the named parent chain.
        # Rebuilding styles invalidates this small cache for language/style changes.
        key = (text_style.name, text_style.parent)
        if key not in _ko_nickname_style_cache:
            _ko_nickname_style_cache[key] = any(name and name[0] == "nick_name_label"
                for name, properties in text_style.inspect())
        return _ko_nickname_style_cache[key]

    config.build_styles_callbacks.append(_ko_nickname_style_clear)

    def _ko_latin_layout_init(self, text, *args, **kwargs):
        plain = "".join(v for k, v in text.tokens if k == _ko_latin_TEXT)
        self._etashi_quote_gaps = {}
        self._etashi_nickname = bool(_preferences.language == "japanese"
            and not text.style.vertical
            and _ko_nickname_style_matches(text.style))
        self._etashi_nickname_hangul = []
        self._etashi_nickname_offsets = {}
        self._etashi_center_hangul = []
        self._etashi_center_references = None
        self._etashi_center_offsets = {}
        self._etashi_code_capitals = _ko_latin_builtins.set()
        # rc54: include compatibility jamo as a reference
        # for this exact concealed name; existing body text remains unchanged.
        self._etashi_jamo_name = bool(_preferences.language == "japanese"
            and plain == "ㅇ=ㅏㅋㅣ")
        self._etashi_center_active = bool(_preferences.language == "japanese"
            and not text.style.vertical and (self._etashi_jamo_name or _ko_latin_re.search(r"[가-힣]", plain))
            and not _ko_latin_re.search(r"[A-Za-z0-9０-９]{24,}", plain)
            and any(48 <= ord(c) <= 57 or 0xff10 <= ord(c) <= 0xff19
                or ord(c) in _ko_body_center_symbols for c in plain))
        self._etashi_code_scan = bool(self._etashi_center_active
            and _ko_latin_re.search(r"[A-Z]", plain)
            and (any(c in _ko_code_stems for c in plain)
                or _ko_latin_re.search(r"[A-Z]-[0-9]+등급", plain)))
        self._etashi_quote_active = bool(
            _preferences.language == "japanese"
            and (_ko_latin_re.search(r"[가-힣]", plain) or
                 _ko_latin_re.fullmatch(r"[\s!?！？「」『』（）()【】“”‘’…‥。、,.:;：；·~～〜—─–-]+", plain)))
        self._etashi_latin_mixed = bool(
            _preferences.language == "japanese"
            and _ko_latin_re.search(r"[가-힣]", plain)
            and _ko_latin_re.search(r"[A-Za-z0-9０-９]", plain)
            and not _ko_latin_re.search(r"[A-Za-z0-9０-９]{24,}", plain))
        return _ko_latin_Layout._etashi_latin_init(self, text, *args, **kwargs)

    def _ko_quote_paragraph(self, paragraph, direction):
        result, rtl = _ko_latin_Layout._etashi_quote_paragraph(self, paragraph, direction)
        if not rtl and getattr(self, "_etashi_nickname", False):
            self._etashi_nickname_hangul.extend((ts, g) for ts, gs in result
                if isinstance(ts, _ko_latin_Segment) and not ts.ruby_top and not ts.ruby_bottom
                for g in gs if 0xac00 <= g.character <= 0xd7a3)
        if not rtl and getattr(self, "_etashi_center_active", False):
            self._etashi_center_hangul.extend((ts, g) for ts, gs in result
                if isinstance(ts, _ko_latin_Segment) and not ts.ruby_top and not ts.ruby_bottom
                for g in gs if (0xac00 <= g.character <= 0xd7a3
                    or (self._etashi_jamo_name and 0x3130 <= g.character <= 0x318f)))
            _ko_mark_code_capitals(self, result)
        if rtl or not getattr(self, "_etashi_quote_active", False):
            return result, rtl
        # Apply after shaping but before native line-breaking; no spacer glyph
        # is inserted, so a closing quote cannot detach from its preceding word.
        flat = [(ts, g) for ts, gs in result for g in gs]
        gap = self.scale_int(2)
        for i, (ts, glyph) in enumerate(flat):
            if (not isinstance(ts, _ko_latin_Segment) or ts.vertical or ts.shader is not None
                    or ts.ruby_top or ts.ruby_bottom):
                continue
            char = chr(glyph.character)
            if char not in "「」『』":
                continue
            j = i + 1 if char in "「『" else i - 1
            # Ruby annotations do not sit on the body baseline.
            while 0 <= j < len(flat) and getattr(flat[j][0], "ruby_top", False):
                j += 1 if char in "「『" else -1
            if not 0 <= j < len(flat):
                continue
            neighbor = chr(flat[j][1].character)
            if neighbor == "\0" or neighbor.isspace():
                continue
            if char in "「『" and neighbor in "」』" or char in "」』" and neighbor in "「『":
                continue
            glyph.advance += gap
            # Closing ink moves right within its enlarged advance. Opening ink
            # stays still; the added advance creates its inward right margin.
            if char in "」』":
                self._etashi_quote_gaps[id(glyph)] = gap
        return result, rtl

    def _ko_latin_shader_safe(shader):
        # The ordinary NVL fade changes alpha only, so its ink can use the
        # same baseline as ADV. Keep moving/warping and composed effects out.
        return shader is None or getattr(shader, "shader", ()) == ("textshader.signi_nvl_soft",)

    def _ko_latin_offset(segment, layout):
        if (_preferences.language != "japanese"
                or not getattr(layout, "_etashi_latin_mixed", False)
                or segment.ruby_top or segment.ruby_bottom or segment.vertical
                or not _ko_latin_shader_safe(segment.shader)
                or segment.font not in _ko_latin_regular_faces):
            return 0
        return round(segment.size * 3.0 / 33.0)

    def _ko_latin_is_letter(glyph):
        # Keep the existing hook name for cached-layout and QA compatibility.
        return (48 <= glyph.character <= 57 or 65 <= glyph.character <= 90
                or 97 <= glyph.character <= 122 or 0xff10 <= glyph.character <= 0xff19)

    _ko_nickname_center_symbols = frozenset(map(ord, "[](){}<>［］（）｛｝〈〉《》【】〔〕!?！？~～〜—─–−-·•+=×÷%％&＆@#：:"))
    _ko_nickname_regular_faces = _ko_latin_regular_faces | frozenset(("fonts/ko/SignKoreanUIPunctuation-Regular.ttf",))

    # Baseline punctuation (period/comma/ellipsis) keeps its native low position.
    # Corner quotes are aligned as a PAIR envelope, never moved to the middle
    # independently: their opening-top/closing-bottom geometry is meaningful.
    _ko_body_center_symbols = frozenset(map(ord,
        "[](){}<>［］（）｛｝〈〉《》【】〔〕「」『』!?！？~～〜—─―–−-·•+=×÷%％&＆@#：:|｜♪♫♬"))
    _ko_body_corner_pairs = {ord("「"): "」", ord("」"): "「", ord("『"): "』", ord("』"): "『"}
    _ko_code_stems = frozenset("甲乙丙丁戊己庚辛壬癸")
    _ko_code_runs = _ko_latin_re.compile(r"(?<![A-Za-z0-9])[A-Z0-9甲乙丙丁戊己庚辛壬癸]+(?![A-Za-z0-9])")
    _ko_grade_runs = _ko_latin_re.compile(r"(?<![A-Za-z0-9])[A-Z]-[0-9]+(?=등급)")

    def _ko_mark_code_capitals(layout, segments):
        # Only the story's numbered laboratory IDs and letter-number grades.
        # Ordinary words/acronyms (JK, GL2, ANGLE2, GLES2, F4) retain the approved
        # Latin baseline. Formatting segments can split an ID without changing
        # its visible spelling; ruby and inline displayables are hard boundaries.
        if not layout._etashi_code_scan:
            return
        glyphs = []
        chars = []
        for ts, gs in segments:
            body = isinstance(ts, _ko_latin_Segment) and not ts.vertical and not ts.ruby_top and not ts.ruby_bottom
            for glyph in gs:
                glyphs.append(glyph)
                chars.append(chr(glyph.character) if body and 0 <= glyph.character <= 0x10ffff else "\ufffc")
        plain = "".join(chars)
        spans = []
        for match in _ko_code_runs.finditer(plain):
            token = match.group()
            if (len(token) < 24 and any(c in _ko_code_stems for c in token)
                    and any("0" <= c <= "9" for c in token)
                    and any("A" <= c <= "Z" for c in token)):
                spans.append(match.span())
        spans.extend(match.span() for match in _ko_grade_runs.finditer(plain))
        for start, end in spans:
            layout._etashi_code_capitals.update(id(glyphs[i]) for i in range(start, end)
                if "A" <= chars[i] <= "Z")

    def _ko_body_reference(layout, segment, glyph):
        # Build the index once per native layout, after line-breaking assigned
        # final baselines. No style.inspect scan and no per-symbol O(text) loop.
        references = layout._etashi_center_references
        if references is None:
            references = _ko_latin_builtins.dict()
            native_bounds = _ko_latin_Segment._etashi_latin_bounds
            batches = _ko_latin_builtins.dict()
            for ts, other in layout._etashi_center_hangul:
                batch_key = (round(other.y, 4), ts.size, id(ts))
                if batch_key not in batches:
                    batches[batch_key] = (ts, [])
                batches[batch_key][1].append(other)
            for batch_key, (ts, glyphs) in batches.items():
                key = batch_key[:2]
                reference = references.get(key, (100000, 100000, -100000, -100000))
                references[key] = native_bounds(ts, glyphs, reference, layout)
            layout._etashi_center_references = references
        return references.get((round(glyph.y, 4), segment.size))

    def _ko_body_glyph_offset(segment, layout, glyph):
        if (not getattr(layout, "_etashi_center_active", False)
                or segment.vertical or segment.ruby_top or segment.ruby_bottom
                or not _ko_latin_shader_safe(segment.shader)):
            return None
        cp = glyph.character
        if not (48 <= cp <= 57 or 0xff10 <= cp <= 0xff19 or cp in _ko_body_center_symbols
                or id(glyph) in layout._etashi_code_capitals):
            return None
        key = (id(segment), cp, round(glyph.y, 4))
        cache = layout._etashi_center_offsets
        if key in cache:
            return cache[key]
        reference = _ko_body_reference(layout, segment, glyph)
        if reference is None or reference[3] <= reference[1]:
            cache[key] = None
            return None
        native_bounds = _ko_latin_Segment._etashi_latin_bounds
        actual = native_bounds(segment, [glyph], (100000, 100000, -100000, -100000), layout)
        if cp in _ko_body_corner_pairs:
            pair = segment.glyphs(_ko_body_corner_pairs[cp], layout)
            for other in pair:
                other.x, other.y = glyph.x, glyph.y
            actual = native_bounds(segment, pair, actual, layout)
        if actual[3] <= actual[1]:
            cache[key] = 0
            return 0
        offset = round((actual[1] + actual[3] - reference[1] - reference[3]) / 2.0)
        cache[key] = offset
        return offset

    def _ko_latin_glyph_offset(segment, layout, glyph, ordinary_offset):
        if not getattr(layout, "_etashi_nickname", False):
            body_offset = _ko_body_glyph_offset(segment, layout, glyph)
            if body_offset is not None:
                return body_offset
        if (not getattr(layout, "_etashi_nickname", False)
                or segment.vertical or segment.ruby_top or segment.ruby_bottom
                or segment.shader is not None
                or segment.font not in _ko_nickname_regular_faces):
            return ordinary_offset if _ko_latin_is_letter(glyph) else 0
        if not (_ko_latin_is_letter(glyph) or glyph.character in _ko_nickname_center_symbols):
            return 0
        key = (id(segment), glyph.character, glyph.y)
        if key in layout._etashi_nickname_offsets:
            return layout._etashi_nickname_offsets[key]
        native_bounds = _ko_latin_Segment._etashi_latin_bounds
        reference = (100000, 100000, -100000, -100000)
        for ts, other in layout._etashi_nickname_hangul:
            if abs(other.y - glyph.y) < 1:
                reference = native_bounds(ts, [other], reference, layout)
        if reference[3] <= reference[1]:
            return ordinary_offset if _ko_latin_is_letter(glyph) else 0
        actual = native_bounds(segment, [glyph], (100000, 100000, -100000, -100000), layout)
        offset = round((actual[1] + actual[3] - reference[1] - reference[3]) / 2.0)
        layout._etashi_nickname_offsets[key] = offset
        return offset

    def _ko_latin_draw(self, glyphs, di, xo, yo, layout):
        offset = _ko_latin_offset(self, layout)
        original = _ko_latin_Segment._etashi_latin_draw
        quote_gaps = getattr(layout, "_etashi_quote_gaps", {})
        if (not offset and not quote_gaps and not getattr(layout, "_etashi_nickname", False)
                and not getattr(layout, "_etashi_center_active", False)):
            return original(self, glyphs, di, xo, yo, layout)
        groups = []
        for glyph in glyphs:
            movement = (quote_gaps.get(id(glyph), 0), _ko_latin_glyph_offset(self, layout, glyph, offset))
            if groups and groups[-1][0] == movement:
                groups[-1][1].append(glyph)
            else:
                groups.append((movement, [glyph]))
        for (dx, dy), group in groups:
            group = _ko_latin_builtins.list(group)
            if not dx and not dy:
                original(self, group, di, xo, yo, layout)
                continue
            if self.underline or self.strikethrough:
                underline, strike = self.underline, self.strikethrough
                self.underline = self.strikethrough = 0
                try:
                    original(self, group, di, xo+dx, yo-dy, layout)
                finally:
                    self.underline, self.strikethrough = underline, strike
                blanks = self.glyphs(" " * len(group), layout)
                for blank, glyph in zip(blanks, group):
                    blank.x, blank.y = glyph.x, glyph.y
                    blank.advance, blank.width = glyph.advance, glyph.width
                original(self, blanks, di, xo, yo, layout)
            else:
                original(self, group, di, xo+dx, yo-dy, layout)

    def _ko_latin_bounds(self, glyphs, bounds, layout):
        original = _ko_latin_Segment._etashi_latin_bounds
        bounds = original(self, glyphs, bounds, layout)
        offset = _ko_latin_offset(self, layout)
        quote_gaps = getattr(layout, "_etashi_quote_gaps", {})
        if (not offset and not quote_gaps and not getattr(layout, "_etashi_nickname", False)
                and not getattr(layout, "_etashi_center_active", False)):
            return bounds
        moved = [(g, quote_gaps.get(id(g), 0), _ko_latin_glyph_offset(self, layout, g, offset)) for g in glyphs]
        moved = [(g, dx, dy) for g, dx, dy in moved if dx or dy]
        if not moved:
            return bounds
        # Grow only the ink safety margin if a raised ascender needs it.
        # Restore native glyph positions before layout/slow-text timing uses them.
        for glyph, dx, dy in moved:
            glyph.x += dx
            glyph.y -= dy
        try:
            return original(self, _ko_latin_builtins.list(g for g, dx, dy in moved), bounds, layout)
        finally:
            for glyph, dx, dy in moved:
                glyph.x -= dx
                glyph.y += dy

    _ko_latin_Layout.__init__ = _ko_latin_layout_init
    _ko_latin_Layout.glyphs_paragraph = _ko_quote_paragraph
    _ko_latin_Segment.draw = _ko_latin_draw
    _ko_latin_Segment.bounds = _ko_latin_bounds
