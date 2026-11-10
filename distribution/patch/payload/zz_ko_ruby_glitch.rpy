# User-approved B: two obscured names only. Layout, timings, and source tags stay intact.
init 260 python:
    import math as _ko_rg_math
    import random as _ko_rg_random
    from renpy.text.text import Text as _ko_rg_Text, Layout as _ko_rg_Layout

    _ko_rg_word = "신ㅁㅗㄱ ㅇ카ㅅㅑ"
    _ko_rg_cases = (
        "{rb}이곳{/rb}{rt}{font=SourceHanSerifSC-Heavy.otf}{size=12}신ㅁㅗㄱ ㅇ카ㅅㅑ{/size}{/font}{/rt}에는 똑같은 규격의 유리관이 백 개 넘게 늘어서 있었다.",
        "짙은 쇠 냄새가 장치를 뚫고 {rb}██{/rb}{rt}{font=SourceHanSerifSC-Heavy.otf}{size=12}신ㅁㅗㄱ ㅇ카ㅅㅑ{/size}{/font}{/rt} 전체에 퍼졌다.",
    )

    def _ko_rg_match(text):
        if _preferences.language != "japanese" or text.style.vertical:
            return False
        values = getattr(text, "text", ())
        if isinstance(values, str):
            values = (values,)
        values = tuple(value for value in values if isinstance(value, str) and _ko_rg_word in value)
        if not values:
            return False
        # History strips font and size tags before constructing Text. Keep that
        # exact full-sentence signature too, so its approved ruby is included.
        signatures = _ko_rg_cases + tuple(renpy.filter_text_tags(case,
            allow=gui.history_allow_tags) for case in _ko_rg_cases)
        # Engine {fast}/CTC wrappers are allowed, but the entire approved source
        # sentence must still be present. Other ruby and other languages pass through.
        return any(case in value for value in values for case in signatures)

    if not hasattr(_ko_rg_Layout, "_etashi_rg_init"):
        _ko_rg_Layout._etashi_rg_init = staticmethod(_ko_rg_Layout.__init__)
        _ko_rg_Layout._etashi_rg_paragraph = staticmethod(_ko_rg_Layout.glyphs_paragraph)
        _ko_rg_Text._etashi_rg_render = staticmethod(_ko_rg_Text.render)

    def _ko_rg_layout_init(self, text, *args, **kwargs):
        self._etashi_rg_enabled = _ko_rg_match(text)
        self._etashi_rg_segments = []
        return _ko_rg_Layout._etashi_rg_init(self, text, *args, **kwargs)

    def _ko_rg_paragraph(self, *args, **kwargs):
        result = _ko_rg_Layout._etashi_rg_paragraph(self, *args, **kwargs)
        if getattr(self, "_etashi_rg_enabled", False):
            for ts, glyphs in result[0]:
                if getattr(ts, 'ruby_top', False) and ''.join(chr(g.character) for g in glyphs if g.character) == _ko_rg_word:
                    self._etashi_rg_segments.append((ts, glyphs))
        return result

    def _ko_rg_rectangles(layout):
        boxes = []
        for ts, glyphs in getattr(layout, "_etashi_rg_segments", ()):
            bounds = ts.bounds(glyphs, (100000, 100000, -100000, -100000), layout)
            if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
                continue
            left, top = layout.unscale_pair(bounds[0] + layout.xoffset, bounds[1] + layout.yoffset)
            right, bottom = layout.unscale_pair(bounds[2] + layout.xoffset, bounds[3] + layout.yoffset)
            boxes.append((_ko_rg_math.floor(left)-1, _ko_rg_math.floor(top)-1,
                _ko_rg_math.ceil(right)+1, _ko_rg_math.ceil(bottom)+2))
        return boxes

    def _ko_rg_render(self, width, height, st, at):
        original = _ko_rg_Text._etashi_rg_render(self, width, height, st, at)
        if not _ko_rg_match(self):
            return original
        layout = self.get_layout()
        boxes = _ko_rg_rectangles(layout) if layout else []
        if not boxes:
            return original
        w, h = original.get_size()
        pad_x = max(64, -min(b[0] for b in boxes)+16, max(b[2] for b in boxes)-w+16)
        pad_y = max(32, -min(b[1] for b in boxes)+4, max(b[3] for b in boxes)-h+4)
        pad_x, pad_y = int(pad_x), int(pad_y)
        pw, ph = w + pad_x*2, h + pad_y*2
        padded = renpy.Render(pw, ph)
        padded.blit(original, (pad_x, pad_y))
        # Materialize the padding before cropping so negative ruby overhang is
        # captured instead of being clipped to the original Text rectangle.
        flat = renpy.Render(pw, ph)
        flat.blit(padded, (0, 0))
        flat.operation = renpy.display.render.FLATTEN
        flat.mesh = True
        flat.add_shader("renpy.texture")
        flat.add_property("drawable_resolution", True)
        flat.add_property("mipmap", False)
        # Keep body glyphs on their original render path; only the ruby ink is
        # sampled from the flattened texture (avoids a second body color pass).
        working = padded
        for index, (left, top, right, bottom) in enumerate(boxes):
            x, y = left+pad_x, top+pad_y
            rw, rh = right-left, bottom-top
            composed = renpy.Render(pw, ph)
            for px, py, sw, sh in ((0,0,pw,y), (0,y,x,rh),
                    (x+rw,y,pw-x-rw,rh), (0,y+rh,pw,ph-y-rh)):
                if sw > 0 and sh > 0:
                    composed.blit(working.subsurface((px,py,sw,sh)), (px,py))
            portion = flat.subsurface((x,y,rw,rh))
            distorted = renpy.Render(rw,rh)
            # Same strip sizes, 10% probability and +/-10px as native GlitchText.
            # A private deterministic visual RNG never consumes the story RNG.
            rng = _ko_rg_random.Random(41000 + index*997 + int(max(st,0)*20))
            yy = 0
            while yy < rh:
                occurs = rng.random()*100 < 10
                band = min(rng.randint(1,10), rh-yy)
                dx = rng.randint(-10,10)
                distorted.subpixel_blit(portion.subsurface((0,yy,rw,band)), (dx if occurs else 0,yy))
                yy += band
            composed.blit(distorted, (x,y))
            working = composed
        out = renpy.Render(w,h)
        out.blit(working, (-pad_x,-pad_y))
        renpy.redraw(self,0.05)
        return out

    _ko_rg_Layout.__init__ = _ko_rg_layout_init
    _ko_rg_Layout.glyphs_paragraph = _ko_rg_paragraph
    _ko_rg_Text.render = _ko_rg_render
