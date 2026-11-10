# rc21: user-approved Korean quick-menu tooltip proposal.
init offset = 210

init python:
    import re as _ko_tooltip_re

    def ko_quick_tooltip_label(key):
        label = renpy.translation.translate_string(key)
        return _ko_tooltip_re.sub(r"\{/?size(?:=[^}]*)?\}", "", label)

    def ko_quick_tooltip_width(key):
        return 132 if key == "快速读档" else 100

screen quick_menu_buttons():
    zorder 100

    if quick_menu and quick_menu_window_ready() and not (renpy.is_skipping() and config.allow_skipping):

        vbox:
            pos quick_menu_pos
            if not quick_menu_status['is_locked']:
                at quick_menu_t
            style_prefix "quick"

            hbox:
                spacing 18
                if quick_menu_status["is_locked"]:
                    use quick_menu_btn("locked", "解锁", SetDict(quick_menu_status, "is_locked", False))
                else:
                    use quick_menu_btn("unlocked", "锁定", SetDict(quick_menu_status, "is_locked", True))
                use quick_menu_btn("hide", "隐藏界面", HideInterface())

            null height 35

            grid 2 4:
                xspacing 18
                yspacing 5
                use quick_menu_btn("qsave", "快速存档", QuickSave(message="已进行快速存档"))
                use quick_menu_btn("auto", "自动播放", Preference("auto-forward", "toggle"))
                use quick_menu_btn("qload", "快速读档", QuickLoad())
                use quick_menu_btn("skip", "快进")
                use quick_menu_btn("save", "存档")
                use quick_menu_btn("history", "历史记录")
                use quick_menu_btn("load", "读档")
                use quick_menu_btn("preferences", "系统设置")

        $ tooltip = GetTooltip()
        if tooltip and isinstance(tooltip, str):
            nearrect:
                focus "tooltip"
                prefer_top True

                if _preferences.language == "japanese":
                    frame:
                        id "ko_quick_tooltip"
                        at tooltip_pop
                        background Frame("gui/quick_menu/cube.png", 16, 0, 16, 0)
                        xysize (ko_quick_tooltip_width(tooltip), 31)
                        padding (0, 0)
                        align (0.5, 0.5)
                        yoffset 5

                        text ko_quick_tooltip_label(tooltip):
                            id "ko_quick_tooltip_text"
                            align (0.5, 0.5)
                            yoffset 0
                            size 16
                            color "#fff"
                            layout "nobreak"
                else:
                    frame:
                        at tooltip_pop
                        background "gui/quick_menu/cube.png"
                        xysize (100, 31)
                        align (0.5, 0.5)
                        yoffset 5

                        text _(tooltip):
                            align (0.5, 0.5)
                            yoffset 0
                            size 20
                            color "#fff"

