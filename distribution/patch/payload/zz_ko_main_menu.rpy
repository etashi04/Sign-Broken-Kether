# Korean native-text menu labels; actions, positions and animations retained.
init offset = 100

screen real_main_menu():

    default _title_animate = not persistent.main_bg_played
    use main_menu_base(animate=_title_animate):
        imagebutton:
            id "mm_start"
            default_focus True
            focus_mask None
            action Start()
            at main_btn_transform2(0.5, _title_animate)
            xoffset -638
            idle ko_main_menu_asset("gui/main_menu/start_idle.png")
            hover ko_main_menu_asset("gui/main_menu/start_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_continue"
            focus_mask None
            action SigniContinue()
            at main_btn_transform(0.5, _title_animate)
            xoffset 638
            idle ko_main_menu_asset("gui/main_menu/continue_idle.png")
            hover ko_main_menu_asset("gui/main_menu/continue_hover.png")
            insensitive ko_main_menu_asset("gui/main_menu/continue_insensitive.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_load"
            focus_mask None
            action ShowMenu("load")
            at main_btn_transform2(0.9, _title_animate)
            xoffset -567
            idle ko_main_menu_asset("gui/main_menu/load_idle.png")
            hover ko_main_menu_asset("gui/main_menu/load_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_preferences"
            focus_mask None
            action ShowMenu("preferences")
            at main_btn_transform(0.9, _title_animate)
            xoffset 567
            idle ko_main_menu_asset("gui/main_menu/config_idle.png")
            hover ko_main_menu_asset("gui/main_menu/config_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_extra"
            focus_mask None
            action ShowMenu("main_menu_extra", _transition=title_menu_transition)
            at main_btn_transform2(1.3, _title_animate)
            xoffset -402
            idle ko_main_menu_asset("gui/main_menu/extra_idle.png")
            hover ko_main_menu_asset("gui/main_menu/extra_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_exit"
            focus_mask None
            action Confirm("您确定要退出吗？",yes=Quit(confirm=False),no=None)
            xoffset 402
            at main_btn_transform(1.3, _title_animate)
            idle ko_main_menu_asset("gui/main_menu/exit_idle.png")
            hover ko_main_menu_asset("gui/main_menu/exit_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

screen main_menu_extra():
    tag menu


    key 'mouseup_3' action ShowMenu("main_menu", _transition=title_menu_transition)
    key 'K_ESCAPE' action ShowMenu("main_menu", _transition=title_menu_transition)

    add "gui/main_menu/bg.png"

    use main_menu_base():
        imagebutton:
            id "mm_staff"
            focus_mask None
            default_focus True
            action ShowMenu("thanks_list")
            at main_btn_transform2(0.5, False)
            xoffset -638
            idle ko_main_menu_asset("gui/main_menu/staff_idle.png")
            hover ko_main_menu_asset("gui/main_menu/staff_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_gallery"
            focus_mask None
            action ShowMenu("gallery")
            at main_btn_transform(0.5, False)
            xoffset 638
            idle ko_main_menu_asset("gui/main_menu/gallery_idle.png")
            hover ko_main_menu_asset("gui/main_menu/gallery_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_dictionary"
            focus_mask None
            action ShowMenu("dictionary")
            at main_btn_transform2(0.9, False)
            xoffset -567
            idle ko_main_menu_asset("gui/main_menu/dictionary_idle.png")
            hover ko_main_menu_asset("gui/main_menu/dictionary_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_prequel"
            focus_mask None
            action Start("plotexternal")
            sensitive persistent.prequel_unlocked
            at main_btn_transform(0.9, False)
            xoffset 567
            idle ko_main_menu_asset("gui/main_menu/prequel_idle.png")
            hover ko_main_menu_asset("gui/main_menu/prequel_hover.png")
            insensitive ko_main_menu_asset("gui/main_menu/prequel_insensitive.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"

        imagebutton:
            id "mm_back"
            focus_mask None
            action ShowMenu("main_menu", _transition=title_menu_transition)
            at main_btn_transform2(1.3, False)
            xoffset -402
            idle ko_main_menu_asset("gui/main_menu/back_idle.png")
            hover ko_main_menu_asset("gui/main_menu/back_hover.png")
            hover_sound "sound/hover2.mp3"
            activate_sound "sound/click2.mp3"


