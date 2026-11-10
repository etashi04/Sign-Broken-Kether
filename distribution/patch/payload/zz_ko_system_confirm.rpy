init offset = 210
init python:
    def ko_system_fake_confirm_button(key, state):
        if _preferences.language != "japanese":
            return "perform/fakemenu/fake_" + key + "_" + state + ".png"
        return Transform(ko_config_asset("gui/confirm/" + key + "_" + state + ".png"), xysize=(351, 89))

screen fake_confirm(message, yes_action, no_action):
    modal True
    zorder 200


    add "gui/overlay/confirm.png"


    fixed:
        xysize (1001, 509)
        align (0.5, 0.5)

        add "perform/fakemenu/fake_comfirm_bg.png"


        text _("梦幻泡影"):
            xalign 0.5
            ypos 28
            color "#ffffff"
            size 36


        text _(message):
            xsize (740 if _preferences.language == "japanese" else 900)
            xalign 0.5
            ypos 180
            text_align 0.5
            color "#687792"
            size (32 if _preferences.language == "japanese" else 38)
            language ("korean-with-spaces" if _preferences.language == "japanese" else "unicode")


        hbox:
            xalign 0.5
            ypos 365
            spacing 50

            imagebutton:
                focus_mask None
                idle ko_system_fake_confirm_button("yes", "idle")
                hover ko_system_fake_confirm_button("yes", "hover")
                action yes_action
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"

            imagebutton:
                focus_mask None
                idle ko_system_fake_confirm_button("no", "idle")
                hover ko_system_fake_confirm_button("no", "hover")
                action no_action
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"













