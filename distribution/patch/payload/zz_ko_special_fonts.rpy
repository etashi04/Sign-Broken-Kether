# rc24: five final-choice thoughts used a Japanese font without Hangul.
# Preserve the original size42, position, outlines, and entrance/exit timing.
init offset = 220

translate japanese style choice_thought:
    font ko_ui_font

# Native generic choice screens are dormant in this build's main story, but
# their Korean-label probe exposed the same missing-glyph risk.
translate japanese style choice_button_text:
    font ko_ui_font

translate japanese style nvl_button_text:
    font ko_ui_font

# rc51: cinematic captions use the same Korean word boundaries as dialogue.
# Width, size, alignment, line spacing, timing and other languages stay native.
translate japanese style below_subtitle:
    language "korean-with-spaces"

translate japanese style right_subtitle:
    language "korean-with-spaces"

translate japanese style center_subtitle:
    language "korean-with-spaces"

translate japanese style center_subtitle_nvl:
    language "korean-with-spaces"

translate japanese style choice_thought:
    language "korean-with-spaces"

