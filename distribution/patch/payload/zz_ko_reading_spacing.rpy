# rc38: move the typewriter texture seam above the next ruby ink; geometry stays unchanged.
# rc37: ruby keeps the normal body baseline and line spacing, including line one.
# rc21: modest reading-space adjustment for Korean display only.
# Styles are restored by Ren'Py when the language changes. No preference/save
# values, source dialogue, tags, font sizes or fixed scene coordinates are edited.
init offset = 210

# rc31: keep Korean words together using the engine's native line-break rules.
# Explicit newlines, tags, text content and other language slots are unchanged.
translate japanese style say_dialogue:
    ruby_line_leading 0
    language "korean-with-spaces"
    line_spacing 16

translate japanese style nvl_dialogue:
    ruby_line_leading 0
    line_spacing 16

translate japanese style nvl_thought:
    ruby_line_leading 0
    line_spacing 16

translate japanese style history_text:
    ruby_line_leading 0
    language "korean-with-spaces"

init python:
    _ko_nvl_entry_text_y_base = nvl_entry_text_y

    def _ko_nvl_entry_text_y(entry, index):
        original = _ko_nvl_entry_text_y_base(entry, index)
        # Named/fixed-height entries, the first paragraph, explicit per-scene
        # spacing and specially staged layouts keep their original placement.
        if (_preferences.language == "japanese"
                and _nvl_fp_layout in ("default", "portrait_left", "portrait_right", "nvl_wide_reading")
                and index > 0 and not gui.nvl_height and entry.who is None
                and _nvl_paragraph_gap is None):
            return max(0, original - 4)
        return original

    nvl_entry_text_y = _ko_nvl_entry_text_y

# Correct the typewriter texture seam only when this layout contains ruby.
# Keep small text and intentionally tight non-ruby scenes on the native seam.
# Run after the Latin/corner-quote hooks and preserve that existing call chain.
init 250 python:
    from renpy.text.text import Layout as _ko_ruby_seam_Layout
    _ko_ruby_seam_pixels = -11

    if not hasattr(_ko_ruby_seam_Layout, "_etashi_ruby_seam_init"):
        _ko_ruby_seam_Layout._etashi_ruby_seam_init = staticmethod(_ko_ruby_seam_Layout.__init__)
        _ko_ruby_seam_Layout._etashi_ruby_seam_paragraph = staticmethod(_ko_ruby_seam_Layout.glyphs_paragraph)

    def _ko_ruby_seam_layout_init(self, text, *args, **kwargs):
        self._etashi_ruby_seam_enabled = (
            _preferences.language == "japanese"
            and text.style.ruby_line_leading == 0
            and text.style.line_overlap_split == 0)
        return _ko_ruby_seam_Layout._etashi_ruby_seam_init(self, text, *args, **kwargs)

    def _ko_ruby_seam_glyphs_paragraph(self, *args, **kwargs):
        result = _ko_ruby_seam_Layout._etashi_ruby_seam_paragraph(self, *args, **kwargs)
        # Native segmentation sets has_ruby before glyph placement. Adjust only
        # the clipping seam, before either software blits or GPU meshes exist.
        if getattr(self, "_etashi_ruby_seam_enabled", False) and self.has_ruby:
            self.line_overlap_split = self.scale_int(_ko_ruby_seam_pixels)
        return result

    _ko_ruby_seam_Layout.__init__ = _ko_ruby_seam_layout_init
    _ko_ruby_seam_Layout.glyphs_paragraph = _ko_ruby_seam_glyphs_paragraph
