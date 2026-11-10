# Korean shared confirmation and alert buttons.
init offset = 100






screen confirm(message, yes_action, no_action):


    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:
        background "gui/confirm/bg.png"
        xysize (833, 494)
        align (0.5, 0.5)
        offset (-10, -5)

        text _("请确认"):
            size 42
            xalign 0.5
            color "#fff"
            ypos 20

        text _(message):
            language ("korean-with-spaces" if _preferences.language == "japanese" else "unicode")
            xmaximum 740
            text_align 0.5
            size (30 if _preferences.language == "japanese" and len(_(message)) > 70 else 35)
            xalign 0.5
            color "#596FA0"
            ypos (115 if _preferences.language == "japanese" and len(_(message)) > 70 else 0.3)

        hbox:
            xalign 0.5
            spacing 28
            ypos 360

            imagebutton:
                id "confirm_yes"
                focus_mask (None if _preferences.language == "japanese" else True)
                action yes_action

                idle ko_config_asset("gui/confirm/yes_idle.png")

                hover ko_config_asset("gui/confirm/yes_hover.png")

                selected_idle ko_config_asset("gui/confirm/yes_selected_idle.png")

                selected_hover ko_config_asset("gui/confirm/yes_selected_hover.png")


                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"

            imagebutton:
                id "confirm_no"
                default_focus True
                focus_mask (None if _preferences.language == "japanese" else True)
                action no_action

                idle ko_config_asset("gui/confirm/no_idle.png")

                hover ko_config_asset("gui/confirm/no_hover.png")

                selected_idle ko_config_asset("gui/confirm/no_selected_idle.png")

                selected_hover ko_config_asset("gui/confirm/no_selected_hover.png")


                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click.mp3"


    key "game_menu" action no_action





screen alert_box(message, message_text_align=0.0):
    modal True
    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"


    frame:
        background "gui/confirm/bg.png"
        xysize (833, 494)
        align (0.5, 0.5)
        offset (-10, -5)


        text _(message):
            language ("korean-with-spaces" if _preferences.language == "japanese" else "unicode")
            size (30 if _preferences.language == "japanese" and len(_(message)) > 70 else 35)
            xmaximum 740
            xalign 0.5
            text_align message_text_align
            color "#596FA0"
            ypos (115 if _preferences.language == "japanese" and len(_(message)) > 70 else 0.3)


        imagebutton:
            id "alert_ok"
            default_focus True
            ypos 360
            xalign 0.5
            idle ko_config_asset("gui/confirm/yes_idle.png")
            hover ko_config_asset("gui/confirm/yes_hover.png")
            selected_idle ko_config_asset("gui/confirm/yes_selected_idle.png")
            selected_hover ko_config_asset("gui/confirm/yes_selected_hover.png")
            action Return()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
