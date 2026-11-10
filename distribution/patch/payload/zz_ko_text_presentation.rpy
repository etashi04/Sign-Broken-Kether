# rc48 candidate: include musical/symbol-only Korean utterances and format marks.
# rc43: include Japanese prolonged-sound marks used as Korean dialogue rules.
# User-requested Korean text presentation, 2026-11-06.
# Applied to TEXT tokens after Ren'Py separates formatting tags and interpolates.
# The v05 source translation values remain unchanged by this display filter.
init 180 python:
    import re as _ko_spacing_re
    import unicodedata as _ko_spacing_unicode
    _ko_previous_replace_text = config.replace_text
    _ko_horizontal_space = r"[ \t\u00a0\u2000-\u200a\u202f\u3000]+"

    def _ko_is_korean_or_symbol_text(value):
        # Singing lines such as ♪―― contain no Hangul. Unicode punctuation,
        # symbols and invisible layout marks still form a punctuation utterance.
        # Letters/numbers from foreign prose or identifiers do not pass this gate.
        return bool(_ko_spacing_re.search(r"[가-힣]", value) or
            value and all(c.isspace() or c in "ーｰ" or _ko_spacing_unicode.category(c)[0] in "PS"
                or _ko_spacing_unicode.category(c) == "Cf" for c in value))

    def ko_normalize_display_text(value):
        if _preferences.language != "japanese":
            return value
        # Leave untranslated Japanese holds, foreign prose, and glitch streams
        # intact. Punctuation-only TEXT tokens may be split off by formatting tags.
        if not _ko_is_korean_or_symbol_text(value):
            return value
        value = _ko_spacing_re.sub(r"([「『])" + _ko_horizontal_space, r"\1", value)
        value = _ko_spacing_re.sub(_ko_horizontal_space + r"([」』])", r"\1", value)
        return value.replace("!", "！").replace("?", "？")

    def _ko_replace_display_text(value):
        if _ko_previous_replace_text is not None:
            value = _ko_previous_replace_text(value)
        return ko_normalize_display_text(value)

    config.replace_text = _ko_replace_display_text

    # The fullwidth !/? normalization above keeps a uniform punctuation width.
    # Its original 1-em advance plus corner-quote side bearings left a visible
    # blank gap. Use the font's own halfwidth-alternate positioning (halt) on
    # those punctuation runs only. Do not change spaces, words or source tags.
    from renpy.text.text import Text as _ko_punct_Text
    from renpy.text.textsupport import TEXT as _ko_TEXT, TAG as _ko_TAG

    if not hasattr(_ko_punct_Text, "_etashi_punctuation_base"):
        _ko_punct_Text._etashi_punctuation_base = staticmethod(_ko_punct_Text.apply_custom_tags)

    def _ko_dash_neighbor(tokens, index, direction):
        # Formatting tags do not break adjacency. Explicit spacing, inline
        # images, waits and line breaks do, so authored separators stay intact.
        index += direction
        while 0 <= index < len(tokens):
            kind, value = tokens[index]
            if kind == _ko_TEXT and value:
                return value[-1] if direction < 0 else value[0]
            if kind != _ko_TAG or value.split("=", 1)[0] in ("space", "vspace", "image", "w", "p", "br"):
                return ""
            index += direction
        return ""

    def _ko_pad_em_dash_runs(tokens):
        result = []
        for index, (kind, value) in enumerate(tokens):
            if kind != _ko_TEXT or not _ko_spacing_re.search(r"[—─]{2,}", value):
                result.append((kind, value))
                continue
            start = 0
            for match in _ko_spacing_re.finditer("[—─]{2,}", value):
                a, b = match.span()
                if a > start:
                    result.append((_ko_TEXT, value[start:a]))
                left = value[a-1] if a else _ko_dash_neighbor(tokens, index, -1)
                right = value[b] if b < len(value) else _ko_dash_neighbor(tokens, index, 1)
                if left.isalnum():
                    result.append((_ko_TAG, "space=4"))
                result.append((_ko_TEXT, match.group()))
                if right.isalnum():
                    result.append((_ko_TAG, "space=4"))
                start = b
            if start < len(value):
                result.append((_ko_TEXT, value[start:]))
        return result

    def _ko_prolonged_neighbor(tokens, index, position, direction):
        # A continuous vowel run may be split by color/font/bold tags. Look
        # beyond the entire run, so a Japanese word stays intact on both sides.
        while 0 <= index < len(tokens):
            kind, value = tokens[index]
            if kind == _ko_TEXT:
                while 0 <= position < len(value):
                    char = value[position]
                    if char not in "ーｰ":
                        return char
                    position += direction
            elif kind != _ko_TAG or value.split("=", 1)[0] in ("space", "vspace", "image", "w", "p", "br"):
                return ""
            index += direction
            if 0 <= index < len(tokens):
                position = len(tokens[index][1])-1 if direction < 0 else 0
        return ""

    def _ko_unify_long_dashes(tokens):
        result = []
        for index, (kind, value) in enumerate(tokens):
            if kind != _ko_TEXT:
                result.append((kind, value))
                continue
            value = value.replace("—", "─").replace("―", "─")
            def prolonged(match):
                start, end = match.span()
                left = _ko_prolonged_neighbor(tokens, index, start-1, -1)
                right = _ko_prolonged_neighbor(tokens, index, end, 1)
                # Preserve the spelling of Japanese words and credited names,
                # including when their formatting tags split the vowel mark.
                # Korean elongation marks and punctuation-only runs are rules.
                for char in (left, right):
                    if char and char not in "ーｰ" and char.isalnum() and not (0xac00 <= ord(char) <= 0xd7a3
                            or 0x1100 <= ord(char) <= 0x11ff or 0x3130 <= ord(char) <= 0x318f):
                        return match.group()
                return "─" * len(match.group())
            value = _ko_spacing_re.sub(r"[ーｰ]+", prolonged, value)
            result.append((kind, value))
        return result

    def _ko_uniform_line_symbols(tokens):
        # Only regular Korean line/tilde symbols share this glyph face. Preserve
        # explicit font/style overrides (including heavy special-effect text).
        # Bold tags remain in the stream and keep their authored emphasis.
        result = []
        explicit = []
        for kind, value in tokens:
            if kind == _ko_TAG:
                if value.startswith("font=") or value.startswith("="):
                    explicit.append("font" if value.startswith("font=") else "style")
                elif value == "/font" and explicit and explicit[-1] == "font":
                    explicit.pop()
                elif value.startswith("/=") and explicit and explicit[-1] == "style":
                    explicit.pop()
                result.append((kind, value))
            elif kind == _ko_TEXT and not explicit:
                for part in _ko_spacing_re.split(r"([—─~～〜]+)", value):
                    if not part:
                        continue
                    if _ko_spacing_re.fullmatch(r"[—─~～〜]+", part):
                        result.extend([(_ko_TAG, "font=fonts/ko/SignKoreanUIPunctuation-Regular.ttf"),
                                       (_ko_TEXT, part), (_ko_TAG, "/font")])
                    else:
                        result.append((_ko_TEXT, part))
            else:
                result.append((kind, value))
        return result

    def _ko_join_period_ellipsis(tokens):
        # rc25: a period followed by an ellipsis is one evenly pitched dot run.
        # Only display-time horizontal whitespace inside that run is removed.
        # Source codepoints/counts, outside spaces, breaks, waits and explicit
        # font/style runs remain intact. Bold emphasis naturally inherits.
        result = []
        explicit = []
        for kind, value in tokens:
            if kind == _ko_TAG:
                if value.startswith("font=") or value.startswith("="):
                    explicit.append("font" if value.startswith("font=") else "style")
                elif value == "/font" and explicit and explicit[-1] == "font":
                    explicit.pop()
                elif value.startswith("/=") and explicit and explicit[-1] == "style":
                    explicit.pop()
                result.append((kind, value))
            elif kind == _ko_TEXT and not explicit:
                start = 0
                for match in _ko_spacing_re.finditer(r"\.[ \t\u00a0\u2000-\u200a\u202f\u3000]*(…+)", value):
                    if match.start() > start:
                        result.append((_ko_TEXT, value[start:match.start()]))
                    result.extend([(_ko_TAG, "font=fonts/ko/SignKoreanUIPunctuation-Regular.ttf"),
                                   (_ko_TEXT, "." + match.group(1)), (_ko_TAG, "/font")])
                    start = match.end()
                if start < len(value):
                    result.append((_ko_TEXT, value[start:]))
            else:
                result.append((kind, value))
        return result

    def _ko_halfwidth_punctuation(tokens):
        tokens = _ko_punct_Text._etashi_punctuation_base(tokens)
        if _preferences.language != "japanese":
            return tokens
        plain = "".join(value for kind, value in tokens if kind == _ko_TEXT)
        if not _ko_is_korean_or_symbol_text(plain):
            return tokens
        # rc28: one continuous rule style for all three long-dash variants.
        # Convert visible text only, retaining each character and its count in
        # the source files, and leaving tags/variables/ordinary hyphens intact.
        tokens = _ko_unify_long_dashes(tokens)
        result = []
        feature_depth = 0
        for kind, value in tokens:
            if kind == _ko_TAG:
                if value.startswith("feature:halt="):
                    feature_depth += 1
                elif value == "/feature:halt":
                    feature_depth = max(0, feature_depth - 1)
                result.append((kind, value))
            elif kind == _ko_TEXT and not feature_depth:
                for part in _ko_spacing_re.split(r"([！？「」『』（）]+)", value):
                    if not part:
                        continue
                    if _ko_spacing_re.fullmatch(r"[！？「」『』（）]+", part):
                        result.extend([(_ko_TAG, "feature:halt=1"),
                                       (_ko_TEXT, part), (_ko_TAG, "/feature:halt")])
                    else:
                        result.append((_ko_TEXT, part))
            else:
                result.append((kind, value))
        return _ko_join_period_ellipsis(_ko_uniform_line_symbols(_ko_pad_em_dash_runs(result)))

    _ko_punct_Text.apply_custom_tags = staticmethod(_ko_halfwidth_punctuation)
