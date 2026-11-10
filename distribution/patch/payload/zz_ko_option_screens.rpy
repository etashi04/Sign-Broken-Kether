# Korean option screens. Original actions and widget IDs preserved.
init offset = 100

screen preferences():
    tag menu

    default config_type = "general"

    add "gui/config/shared/bg.png"
    add ko_config_title():
        pos (30, 14)

    use common_return_base(pos=(1769, 30), size='l')
    use controller_menu_hint("settings")

    hbox:






        xcenter 954
        ypos 28
        spacing 4

        imagebutton:
            id "config_tab_general"
            default_focus True
            focus_mask (None if _preferences.language == "japanese" else True)
            idle ko_config_asset("gui/config/radio/general_idle.png")
            hover ko_config_asset("gui/config/radio/general_hover.png")
            selected_idle ko_config_asset("gui/config/radio/general_selected_idle.png")
            selected_hover ko_config_asset("gui/config/radio/general_selected_hover.png")

            action [SetScreenVariable('config_type', 'general')]

            activate_sound "sound/click.mp3"
            hover_sound "sound/hover2.mp3"

        imagebutton:
            id "config_tab_audio"
            focus_mask (None if _preferences.language == "japanese" else True)
            idle ko_config_asset("gui/config/radio/audio_idle.png")
            hover ko_config_asset("gui/config/radio/audio_hover.png")
            selected_idle ko_config_asset("gui/config/radio/audio_selected_idle.png")
            selected_hover ko_config_asset("gui/config/radio/audio_selected_hover.png")

            action SetScreenVariable('config_type', 'audio')

            activate_sound "sound/click.mp3"
            hover_sound "sound/hover2.mp3"

        imagebutton:
            id "config_tab_guide"
            focus_mask (None if _preferences.language == "japanese" else True)
            idle ko_config_asset("gui/config/radio/guide_idle.png")
            hover ko_config_asset("gui/config/radio/guide_hover.png")
            selected_idle ko_config_asset("gui/config/radio/guide_selected_idle.png")
            selected_hover ko_config_asset("gui/config/radio/guide_selected_hover.png")

            action [SetScreenVariable('config_type', 'guide')]

            activate_sound "sound/click.mp3"
            hover_sound "sound/hover2.mp3"


        imagebutton:
            id "config_tab_gamepad"
            focus_mask (None if _preferences.language == "japanese" else True)
            idle ko_config_asset("gui/config/radio/gamepad_idle.png")
            hover ko_config_asset("gui/config/radio/gamepad_hover.png")
            selected_idle ko_config_asset("gui/config/radio/gamepad_selected_idle.png")
            selected_hover ko_config_asset("gui/config/radio/gamepad_selected_hover.png")

            action [SetScreenVariable('config_type', 'gamepad')]

            activate_sound "sound/click.mp3"
            hover_sound "sound/hover2.mp3"
    if config_type not in ("guide", "gamepad"):
        hbox:
            align (0.0, 1.0)
            offset (120, -40)
            spacing 1130
            default reset_action = get_voice_reset_actions()

            imagebutton:
                id "config_reset"
                focus_mask (None if _preferences.language == "japanese" else True)
                idle ko_config_asset("gui/config/shared/reset_idle.png")
                hover ko_config_asset("gui/config/shared/reset_hover.png")
                selected_idle ko_config_asset("gui/config/shared/reset_selected_idle.png")
                selected_hover ko_config_asset("gui/config/shared/reset_selected_hover.png")
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"

                action Confirm(_("是否恢复默认设置？"), reset_action, confirm_selected=True)

            imagebutton:
                id "config_title"
                focus_mask (None if _preferences.language == "japanese" else True)
                if main_menu:
                    action ShowMenu("main_menu", _transition=title_menu_transition)
                else:
                    action [
                        SetVariable("persistent.main_bg_played", False),
                        SigniMainMenu()
                    ]
                idle ko_config_asset("gui/config/shared/title_idle.png")
                hover ko_config_asset("gui/config/shared/title_hover.png")
                selected_idle ko_config_asset("gui/config/shared/title_selected_idle.png")
                selected_hover ko_config_asset("gui/config/shared/title_selected_hover.png")
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"

    frame:
        background None
        pos (116, 180)
        use expression "config_%s" % config_type


screen config_general():
    hbox:
        style "config_hbox"
        spacing 275
        use config_general_left()
        use config_general_right()

screen config_general_left():
    default text_preview = PreviewSlowText("文字预览文字预览", size=26, color="#596fa0", align=(0.5, 0.5))

    vbox:
        spacing 45
        style "config_left_vbox"

        vbox:
            style "config_title_bar_set_vbox"
            use config_title("文字显示速度")

            bar:
                id "config_text_speed"
                value Preference("text speed")
                style "config_bar"
                released Function(text_preview.update_cps)

        vbox:
            style "config_title_bar_set_vbox"
            use config_title("自动播放速度")

            bar:
                id "config_auto_speed"
                value Preference("auto-forward time")
                style "config_bar"
                bar_invert True

        vbox:
            style "config_title_bar_set_vbox"
            use config_title("对话框不透明度")

            bar:
                id "config_textbox_alpha"
                value VariableValue(variable="persistent.textbox_alpha", range=1.0)
                style "config_bar"

        vbox:
            style "config_title_bar_set_vbox"
            use config_title("文字描边颜色")
            hbox:
                spacing 15

                imagebutton:
                    focus_mask True
                    auto "gui/config/shared/check_%s.png"
                    yalign 0.5
                    xysize (34, 34)
                    action [SetVariable("persistent.text_outline_color", None), SetVariable("persistent.enable_text_outline", False)]
                    selected persistent.text_outline_color is None
                text "无描边":
                    size (29 if _preferences.language == "japanese" else 35)
                    color "#58719f"
                    yalign 0.5

                imagebutton:
                    focus_mask True
                    auto "gui/config/shared/check_%s.png"
                    yalign 0.5
                    xysize (34, 34)
                    action [SetVariable("persistent.text_outline_color", "#FFFFFF80"), SetVariable("persistent.enable_text_outline", True)]
                    selected persistent.text_outline_color == "#FFFFFF80"
                text "半透明白":
                    size (29 if _preferences.language == "japanese" else 35)
                    color "#58719f"
                    yalign 0.5

                imagebutton:
                    focus_mask True
                    auto "gui/config/shared/check_%s.png"
                    yalign 0.5
                    xysize (34, 34)
                    action [SetVariable("persistent.text_outline_color", "#FFFFFF"), SetVariable("persistent.enable_text_outline", True)]
                    selected persistent.text_outline_color == "#FFFFFF"
                text "白色":
                    size (29 if _preferences.language == "japanese" else 35)
                    color "#58719f"
                    yalign 0.5

                imagebutton:
                    focus_mask True
                    auto "gui/config/shared/check_%s.png"
                    yalign 0.5
                    xysize (34, 34)
                    action [SetVariable("persistent.text_outline_color", "#D9E8F5FF"), SetVariable("persistent.enable_text_outline", True)]
                    selected persistent.text_outline_color == "#D9E8F5FF"
                text "冰蓝色":
                    size (29 if _preferences.language == "japanese" else 35)
                    color "#58719f"
                    yalign 0.5



        vbox:
            style "config_title_bar_set_vbox"
            use config_title("文本预览")

            frame:
                background "gui/config/general/test_bg.png"
                xysize (656, 150)
                padding (0, 0)

                add "gui/config/general/test_textbox.png":

                    at transform:
                        alpha persistent.textbox_alpha
                add text_preview:
                    align (0.5, 0.5)


screen config_general_right():
    frame:
        background None
        vbox:
            style "config_title_bar_set_vbox"
            spacing 40
            use config_title("显示模式")

            hbox:
                style "config_btn_hbox"

                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/fullscreen_idle.png")
                    hover ko_config_asset("gui/config/general/fullscreen_hover.png")
                    selected_idle ko_config_asset("gui/config/general/fullscreen_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/fullscreen_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    action Preference("display", "fullscreen")

                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/windows_idle.png")
                    hover ko_config_asset("gui/config/general/windows_hover.png")
                    selected_idle ko_config_asset("gui/config/general/windows_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/windows_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    selected not preferences.fullscreen
                    action Preference("display", "window")

        vbox:
            ypos 250
            style "config_title_bar_set_vbox"
            spacing 40
            use config_title("语言选择")

            grid 2 2:
                spacing 50
                xsize 700
                use config_general_lang(None, "简体中文")
                use config_general_lang("cht", "繁體中文")
                use config_general_lang("en", "English")
                use config_general_lang("japanese", "한국어")

        vbox:
            style "config_title_bar_set_vbox"
            ypos 560
            spacing 40
            frame:
                background "gui/config/shared/subheading.png"
                xysize (450, 32)
                text _("跳过未读文本"):
                    style "config_title_text"

            hbox:
                style "config_btn_hbox"
                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/skip_yes_idle.png")
                    hover ko_config_asset("gui/config/general/skip_yes_hover.png")
                    selected_idle ko_config_asset("gui/config/general/skip_yes_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/skip_yes_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    action Preference("skip", "all")

                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/skip_no_idle.png")
                    hover ko_config_asset("gui/config/general/skip_no_hover.png")
                    selected_idle ko_config_asset("gui/config/general/skip_no_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/skip_no_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    action Preference("skip", "seen")


screen config_general_lang(lang, name):
    hbox:
        spacing 10
        imagebutton:
            focus_mask True
            auto "gui/config/shared/check_%s.png"

            yalign 0.5
            xalign 0.0
            xysize (34, 34)

            action Language(lang)

        text name:
            size 30
            align (0.5, 0.5)
            font ko_ui_font
            if lang in [None, "japanese", "en"]:
                color "#58719f"
            else:
                color "#4c4c4c"
                strikethrough True



screen config_audio():
    hbox:
        style "config_hbox"
        use config_audio_left()
        use config_audio_right()

screen config_audio_left():
    vbox:
        spacing 75
        style "config_left_vbox"
        use config_audio_bar_set("主音量", "main")
        use config_audio_bar_set("BGM音量", "music")
        use config_audio_bar_set("音效音量", "sfx")
        vbox:
            style "config_title_bar_set_vbox"
            frame:
                background "gui/config/shared/subheading.png"
                xysize (450, 32)
                text "下一句文本时不中断语音":
                    style "config_title_text"


            hbox:
                style "config_btn_hbox"
                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/yes_idle.png")
                    hover ko_config_asset("gui/config/general/yes_hover.png")
                    selected_idle ko_config_asset("gui/config/general/yes_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/yes_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    action SetVariable("preferences.voice_sustain", True)

                imagebutton:
                    focus_mask (None if _preferences.language == "japanese" else True)
                    idle ko_config_asset("gui/config/general/no_idle.png")
                    hover ko_config_asset("gui/config/general/no_hover.png")
                    selected_idle ko_config_asset("gui/config/general/no_selected_idle.png")
                    selected_hover ko_config_asset("gui/config/general/no_selected_hover.png")
                    hover_sound "sound/hover2.mp3"
                    activate_sound "sound/click2.mp3"
                    action SetVariable("preferences.voice_sustain", False)


screen config_audio_right():
    vbox:
        use config_audio_bar_set("语音音量", "voice")
        use config_audio_character_voice()


screen config_audio_character_voice():
    vbox:
        ypos 80
        text _("角色语音单独设定"):
            style "config_title_text"
            align (0.3, 0.0)

        hbox:
            xsize 785
            xpos -33
            ypos 30
            spacing 80
            add f"gui/config/audio/char/{character_radio}.png":
                xoffset 15
            use config_audio_character_grid()

screen config_audio_character_grid():
    frame:
        background None
        padding (0, 0)
        yoffset -5
        xsize 726

        has vbox

        vpgrid:
            id "vp"
            cols 2
            yinitial 0.0
            yspacing 3
            xspacing 30

            for c in character_list:
                hbox:
                    imagebutton:
                        focus_mask True
                        auto "gui/config/shared/check_%s.png"

                        yalign 0.5
                        xalign 0.0
                        xysize (34, 34)

                        action [Stop("voice"), ToggleVoiceMute(c, invert=True)]

                    button:
                        focus_mask None
                        action [SetVariable("character_radio", c),
                            Stop("voice"),
                            PlayCharacterVoice(c, f"audio/tmp/{c}/{c}_100001.ogg")]

                        background "gui/config/audio/name_idle.png"
                        hover_background "gui/config/audio/name_hover.png"
                        selected_idle_background "gui/config/audio/name_selected_idle.png"
                        selected_hover_background "gui/config/audio/name_selected_hover.png"
                        xysize (181, 55)

                        selected c == character_radio

                        text _(c):
                            size 35
                            align (0.5, 0.5)
                            color "#58719f"
                            selected_color "#fff"
        hbox:
            spacing 20
            offset (-10, 50)
            bar:
                id "config_character_volume"
                value SetCharacterVolume(character_radio)
                style "config_bar"
                xysize (333, 34)

            use config_audio_bar_text(GetCharacterVolume(character_radio) * 100)

            imagebutton:
                focus_mask True
                action PlayCharacterVoice(character_radio, f"audio/tmp/{character_radio}/{character_radio}_100001.ogg")
                yoffset -2
                auto "gui/config/audio/play_%s.png"



screen config_gamepad():
    tag menu
    fixed:
        pos (-116, -180)
        xysize (config.screen_width, config.screen_height)

        if _preferences.language == "japanese":
            text "컨트롤러 조작":
                font ko_ui_font
                size 38
                color "#5871a5"
                pos (208, 190)
        else:
            add Transform("gui/config/shared/help_gamepad.png", crop=(208, 140, 520, 80), zoom=0.75):
                pos (208, 190)

        add "gui/controller/guide_pad.svg":
            pos (590, 370)
        add "gui/controller/guide_leaders.svg"

        use controller_guide_callout(("LT",), _("历史文本"), 200, 368)
        use controller_guide_callout(("LB", "X"), _("自动播放{#controller_guide}"), 200, 476)
        use controller_guide_callout(("Back",), _("隐藏界面{#controller_guide}"), 200, 684)
        use controller_guide_callout(("dpad", "LS"), _("菜单导航"), 200, 788)

        use controller_guide_callout(("RT",), _("快捷菜单"), 1424, 368)
        use controller_guide_callout(("RB", "Y"), _("开关跳过"), 1424, 476)
        use controller_guide_callout(("B", "Start"), _("呼出 / 隐藏菜单"), 1424, 580)
        use controller_guide_callout(("A",), _("确认 / 下一句文本"), 1424, 684)
        use controller_guide_callout(("R3",), _("切换显示模式"), 1424, 788)

        for key, x, y in (("LT", 791, 417), ("RT", 1129, 417), ("LB", 791, 456), ("RB", 1129, 456), ("R3", 1051, 687), ("X", 1122, 580), ("Y", 1173, 531), ("B", 1224, 580), ("A", 1173, 629)):
            text ({"LB": "L1", "RB": "R1", "LT": "L2", "RT": "R2"}.get(key, key) if is_steam_deck() else key):
                style "controller_guide_pad_label"
                size (18 if key in ("LT", "RT", "LB", "RB") else 21)
                xcenter x
                ycenter y

        text _("R3：按下右摇杆"):
            style "controller_guide_caption"
            xalign 0.5
            ypos 879

        if is_steam_deck():
            vbox:
                xalign 0.5
                ypos 919
                spacing 4
                text _("Deck：L2 / R2 为扳机，L1 / R1 为肩键；菜单内 L1 / R1 切换分类或翻页。"):
                    style "controller_guide_note"
                    size 20
                text _("推荐布局：左触控板按下导航，右触控板移动 / 点击；L4 返回，R4 确认。"):
                    style "controller_guide_note"
                    size 20
        else:
            text _("图中为剧情操作；菜单内 LB / RB 用于切换分类或翻页。"):
                style "controller_guide_note"
                ypos 940

screen controller_guide_callout(keys, description, x, y):
    $ left_side = x < config.screen_width / 2
    fixed:
        pos (x, y - 58)
        xysize (300 if left_side else 360, 82)
        text description:
            style "controller_guide_description"
            xsize (300 if left_side else 360)
            xalign (1.0 if left_side else 0.0)
            text_align (1.0 if left_side else 0.0)
        hbox:
            xalign (1.0 if left_side else 0.0)
            ypos 40
            spacing 8
            for key in keys:
                if key in ("dpad", "LS"):
                    use controller_hint_keycap(key)
                elif key == "R3":
                    fixed:
                        xysize (36, 36)
                        add "gui/controller/guide_stickcap.svg"
                        text key:
                            style "controller_guide_key_label"
                            size 18
                            align (0.5, 0.5)
                            yoffset -1
                else:
                    fixed:
                        xysize (48, 36)
                        add Frame("gui/controller/guide_keycap.svg", 4, 4)
                        if key in ("Back", "Start"):
                            add ("gui/controller/view.svg" if key == "Back" else "gui/controller/menu.svg"):
                                align (0.5, 0.5)
                                yoffset -1
                        else:
                            text ({"LB": "L1", "RB": "R1", "LT": "L2", "RT": "R2"}.get(key, key) if is_steam_deck() else key):
                                style "controller_guide_key_label"
                                align (0.5, 0.5)
                                yoffset -1
