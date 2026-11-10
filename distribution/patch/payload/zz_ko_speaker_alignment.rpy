# rc36: retain 36px; center the ADV name ink with a -1px baseline correction.
# Preserve the independent NVL label's original placement.
init 230 python:
    _ko_speaker_base_yoffset = style.say_label.yoffset
    _ko_speaker_nvl_base_yoffset = style.nvl_label.yoffset

translate japanese style say_label:
    size 36
    yoffset (_ko_speaker_base_yoffset - 1)

translate japanese style nvl_label:
    size 36
    yoffset _ko_speaker_nvl_base_yoffset

# Display-only normalization also handles historical names stored with size tags.
# Name characters, colors, explicit font faces, nicknames and saved text stay intact.
init offset = 240

init python:
    import functools as _ko_speaker_functools

    def ko_speaker_name(text):
        text = renpy.translate_string(text)
        if _preferences.language == "japanese":
            return renpy.filter_text_tags(text, deny=["size"])
        return text

    _ko_original_speaker_namebox_width = signi_speaker_namebox_width

    @_ko_speaker_functools.lru_cache(maxsize=512)
    def signi_speaker_namebox_width(name, nick_name, language, font_size=1.0, font_transform=None, history=False):
        if language != "japanese":
            return _ko_original_speaker_namebox_width(name, nick_name, language, font_size, font_transform, history)
        label = Text(ko_speaker_name(name), style="say_label", size=36, substitute=False)
        width = renpy.render(label, 4096, 1080, 0, 0).get_size()[0]
        if nick_name and not history:
            nickname = Text("[" + nick_name + "]", style="nick_name_label", substitute=False)
            width = max(width, renpy.render(nickname, 4096, 1080, 0, 0).get_size()[0])
        padding = 20 if history else 60
        return max(326, int((width + padding + 9) // 10) * 10)

screen say(who, what):
    zorder 0

    window:
        add "gui/say/textbox.png":
            xalign 0.5

            at transform:
                alpha persistent.textbox_alpha
        id "window"

        if who is not None:
            python:
                if '|' in who:
                    name, nick_name = who.split('|')
                else:
                    name, nick_name = who, ""
                namebox_width = signi_speaker_namebox_width(_(name), _(nick_name), _preferences.language,
    _preferences.font_size, _preferences.font_transform)

            window:
                id "namebox"
                style "namebox"
                background Frame('gui/say/namebox.png', 24, 0, 0, 0)
                xysize (namebox_width, 49)
                yoffset 13

                if nick_name:
                    text _("[[[nick_name!t]]"):
                        style "nick_name_label"
                text ko_speaker_name(_(name)) id "who":
                    size (36 if _preferences.language == "japanese" else 40)

        if persistent.text_outline_color:
            text what id "what" outlines [(1, persistent.text_outline_color, 0, 0)]
        else:
            text what id "what"




        if not renpy.variant("small"):
            add SideImage():
                xalign 0.0
                yalign 1.0
                xoffset 120
                yoffset 2


