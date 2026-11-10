# Korean secondary UI. Text is rendered at runtime; original image files stay intact.
# Every asset helper returns the original path outside the Japanese language slot.
# Screen bodies retain the original actions, positions, timers and transforms.
init offset = 200

init python:
    def ko_secondary_title(key, original):
        if _preferences.language != "japanese":
            return original
        labels = {
            "save": ("저장", "S A V E"),
            "load": ("불러오기", "L O A D"),
            "history": ("대화 기록", "H I S T O R Y"),
            "dictionary": ("용어사전", "D I C T I O N A R Y"),
            "gallery": ("갤러리", "G A L L E R Y"),
            "thanks": ("제작진", "C R E D I T"),
        }
        label, subtitle = labels[key]
        return Fixed(
            Text(label, font=ko_ui_font, size=46, color="#f5f5f5", pos=(0, 0), layout="nobreak"),
            Text(subtitle, font="fonts/ChillRoundFRegular.otf", size=12, color="#adb8cf", pos=(2, 54), layout="nobreak"),
            xysize=(225, 70))

    def ko_secondary_menu_title():
        if _preferences.language != "japanese":
            return "gui/menu/title.png"
        # Keep the native 75x52 title slot; the small MENU is in the background.
        return Fixed(Text("메뉴", font=ko_ui_font, size=36, color="#f5f5f5",
            xcenter=absolute(37.5), ycenter=23, layout="nobreak"), xysize=(75, 52))

    def ko_secondary_gallery_tab(key, state):
        original = "gui/gallery/tabs/" + key + "_" + state + ".png"
        if _preferences.language != "japanese":
            return original
        children = []
        if state.startswith("selected"):
            # The left edge of the selected tab is a blank strip of its original panel.
            children.append(Transform(original, crop=(0, 0, 8, 42), xysize=(201, 42)))
        children.append(Text("일러스트" if key == "cg" else "영상", font=ko_ui_font,
            size=30, color="#ffffff" if "hover" in state else "#e5e8f3",
            outlines=[(2, "#ffffff50", 0, 0)] if "hover" in state else [],
            align=(0.5, 0.5), layout="nobreak"))
        return Fixed(*children, xysize=(201, 42))

    def ko_secondary_new_badge():
        # User preference: keep the complete original NEW badge, glow and ornaments.
        return "gui/save/new.png"

    def ko_secondary_page_background(state):
        original = "gui/save/btn_page_" + state + ".png"
        if _preferences.language == "japanese" and state == "idle":
            # Original idle artwork is one pixel left of the hover/selected circle.
            return Transform(original, xoffset=1)
        return original

    def ko_secondary_fake_button(key, state):
        original = "perform/fakemenu/fake_" + key + "_" + state + ".png"
        if _preferences.language != "japanese":
            return original
        labels = {"start": "여정 시작", "continue": "여정 계속", "load": "기억 되짚기",
            "config": "설정", "extra": "추가 콘텐츠", "exit": "게임 종료"}
        left = key in ("start", "continue", "load")
        locked = state == "insensitive"
        children = []
        if locked:
            # Only the original padlock is retained; no source-language glyphs remain.
            lock_x, lock_w = (0, 72) if left else (235, 65)
            children.append(Transform(original, crop=(lock_x, 0, lock_w, 90), pos=(lock_x, 0)))
        else:
            # Preserve the star and the English sublabel, including their hover glow.
            star_x, star_w = (0, 68) if left else (230, 70)
            children.append(Transform(original, crop=(star_x, 0, star_w, 80), pos=(star_x, 0)))
            children.append(Transform(original, crop=(0, 80, 300, 46), pos=(0, 80)))
        children.append(Text(labels[key], font=ko_ui_font, size=38 if locked else 42,
            color="#787d89" if locked else "#ffffff",
            outlines=[(2, "#ffffff50", 0, 0)] if state == "hover" else [],
            xcenter=183 if left else 117, ycenter=49, layout="nobreak"))
        return Fixed(*children, xysize=(300, 126))

    def ko_secondary_fake_alert(key):
        original = "perform/fakemenu/fake_" + key + "_alert.png"
        if _preferences.language != "japanese":
            return original
        label = "마녀의 힘으로 이 항목은 선택할 수 없습니다." if key == "title" else "마녀의 힘으로 이 기능은 비활성화되어 있습니다."
        # Source glyphs occupy y=17..37. Blank top/bottom strips retain the panel gradient.
        return Fixed(
            Transform(original, crop=(0, 0, 1038, 14), pos=(0, 0)),
            Transform(original, crop=(0, 45, 1038, 10), xysize=(1038, 41), pos=(0, 14)),
            Text(label, font=ko_ui_font, size=23, color="#ffffff", align=(0.5, 0.5), layout="nobreak"),
            xysize=(1038, 55))

# Source: scripts/screens/save.rpy
screen file_slots(title):
    $ page_name = FilePageName(auto='a', quick='q')
    add "gui/save/bg.png"
    add ko_secondary_title(title, f"gui/save/{title}.png"):
        pos (46, 14)

    use common_return_base(pos=(1769, 30), size='l')
    use controller_menu_hint("files")

    fixed:
        grid gui.file_slot_cols gui.file_slot_rows:
            xalign 0.5
            yalign 0.5

            spacing gui.slot_spacing

            for i in range(gui.file_slot_cols * gui.file_slot_rows):

                $ slot = i + 1

                button:
                    id ("slot_%d" % slot)
                    default_focus (slot == 1)
                    if title == "load":
                        action If(FileLoadable(slot), Confirm(layout.LOADING_NEW, FileLoad(slot, confirm=None), confirm_selected=True), NullAction())
                    else:
                        action FileSave(slot)

                    background "gui/save/slot_idle.png"
                    hover_background "gui/save/slot_hover.png"
                    activate_sound "sound/click.mp3"
                    hover_sound "sound/hover.mp3"
                    xysize (507, 349)
                    align (0.5, 0.5)

                    focus_mask True

                    add AlphaMask(Crop((0, 24, 415, 185), Frame(FileScreenshot(slot), xysize=(415, 234))),
                        "gui/save/slot_mask.png"):
                        pos (54, 48)
                        xysize (415, 185)

                    if FileNewest(slot):
                        add ko_secondary_new_badge():
                            xysize (98, 46)
                            pos (370, 50)

                    text FileTime(slot, format=_("{#file_time}%Y.%m.%d %H:%M"), empty=_("空存档位")):
                        style "slot_time_text"
                        font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")

                    if FileLoadable(slot):
                        $ chapter_title = FileJson(slot, "chapter_title")

                        if chapter_title:
                            text _(chapter_title):
                                style "slot_name_text"
                                font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")

                    key "save_delete" action FileDelete(slot)



        hbox:
            align (0.5, 0.5)
            spacing 1590

            imagebutton:
                id "file_prev"
                focus_mask True
                auto "gui/save/btn_left_%s.png"
                action FilePagePrevious(max=5, wrap=True, auto=(title == "load"))
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover.mp3"
                keysym ["save_page_prev"]

            imagebutton:
                id "file_next"
                focus_mask True
                auto "gui/save/btn_right_%s.png"
                action FilePageNext(max=5, wrap=True, auto=(title == "load"))
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover.mp3"
                keysym ["save_page_next"]

        vbox:
            style_prefix "page"

            xalign 0.5
            yalign 1.0
            yoffset (-98 if _pad_state.instance is not None else -60)

            hbox:
                xalign 0.5

                spacing 30

                if config.has_autosave and title == "load":
                    textbutton _("自动") action FilePage("auto"):
                        id "file_page_a"
                        text_size (20 if _preferences.language == "japanese" else 24)
                        text_font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                        background ko_secondary_page_background("idle")
                        hover_background ko_secondary_page_background("hover")
                        selected_background ko_secondary_page_background("selected")
                        # Native text alpha, independent of the circle/hover halo.
                        text_xoffset 0
                        text_yoffset (-1 if _preferences.language == "japanese" else 0)
                        focus_mask True
                        activate_sound "sound/click.mp3"
                        hover_sound "sound/hover.mp3"

                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick"):
                        id "file_page_q"
                        background ko_secondary_page_background("idle")
                        hover_background ko_secondary_page_background("hover")
                        selected_background ko_secondary_page_background("selected")
                        text_xoffset 0
                        text_yoffset (-2 if _preferences.language == "japanese" else 0)
                        focus_mask True
                        activate_sound "sound/click.mp3"
                        hover_sound "sound/hover.mp3"


                for page in range(1, 6):
                    textbutton "[page]" action FilePage(page):
                        id ("file_page_%d" % page)
                        background ko_secondary_page_background("idle")
                        hover_background ko_secondary_page_background("hover")
                        selected_background ko_secondary_page_background("selected")
                        text_xoffset (1 if _preferences.language == "japanese" and page == 1 else 0)
                        text_yoffset (1 if _preferences.language == "japanese" and page == 1 else 0)
                        focus_mask True
                        activate_sound "sound/click.mp3"
                        hover_sound "sound/hover.mp3"


screen history():
    tag menu



    key 'mouseup_3' action Return()
    key 'K_ESCAPE' action Return()

    add "gui/history/bg.png"
    add ko_secondary_title("history", "gui/history/title.png"):
        pos (34, 35)


    predict False

    frame:
        background Solid("#0ff0")
        pos (310, 115)
        xysize (1406, 884)

        has viewport

        id "vp"
        yinitial 1.0

        mousewheel True
        draggable True
        xalign 0.5

        vbox:

            spacing 72

            for h in _history_list:

                fixed:
                    xsize 1310
                    yfit True
                    yminimum 180

                    hbox:
                        spacing 15
                        ypos 5
                        if h.what != _last_say_what and (renpy.get_identifier_checkpoints(h.rollback_identifier) is not None):
                            button:
                                id ("history_jump_" + str(h.rollback_identifier))
                                focus_mask True
                                action Confirm(layout.JUMP,
                                            [With(dissolve), RollbackToIdentifier(h.rollback_identifier)])
                                background "gui/history/jump_idle.png"
                                hover_background "gui/history/jump_hover.png"
                                xysize (41, 41)

                        $ replay_files = getattr(h, "page_voice_files", None)
                        if replay_files or h.voice.filename:
                            button:
                                focus_mask True
                                action ReplayCharacterVoice(replay_files or h.voice.filename, h.voice.tag)
                                background "gui/history/voice_idle.png"
                                hover_background "gui/history/voice_hover.png"
                                xysize (41, 41)

                    vbox:
                        xpos 170
                        xsize 1140

                        if h.who:
                            python:
                                name = h.who
                                if '|' in name:
                                    name = name.split('|')[0]
                                history_namebox_width = signi_speaker_namebox_width(_(name), "", _preferences.language,
    _preferences.font_size, _preferences.font_transform, history=True)

                            frame:
                                background Frame("gui/say/namebox.png", 24, 0, 0, 0)
                                xysize (history_namebox_width, 49)

                                has text ko_speaker_name(_(name))
                                substitute False
                                color "#fff"
                                xanchor 0.0
                                yalign 0.5
                                size (36 if _preferences.language == "japanese" else 30)
                                xpos 10
                                xsize history_namebox_width - 20
                                if "color" in h.who_args:
                                    color h.who_args["color"]

                            null height 21
                        else:
                            null height 20

                        $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                        text what style "history_text":
                            substitute False
                            xsize 1140
                            size 35
                            color "#7489b7"

    vbar value YScrollValue("vp"):
        pos (1741, 115)
        xysize (26, 889)
        top_bar "gui/history/vertical_idle_bar.png"
        bottom_bar "gui/history/vertical_idle_bar.png"
        thumb "gui/history/vertical_idle_thumb.png"
        hover_thumb "gui/history/vertical_hover_thumb.png"
        thumb_offset 10

    use common_return_base(pos=(1825, 10), size='s')
    use controller_menu_hint("scroll")


screen dictionary(entry_id=None):
    tag menu
    modal True
    zorder 100




    key 'mouseup_3' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())
    key 'K_ESCAPE' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())
    key 'game_menu' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())

    default content_scroll = ui.adjustment()

    add "gui/dictionary/bg.png"

    add ko_secondary_title("dictionary", "gui/dictionary/title.png"):
        pos (32, 15)



    use common_return_base(pos=(1769, 30), size='l', action=If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return()))


    $ repair_dictionary_map()
    $ _dict_ids = [candidate for candidate in persistent.dictionary_handler.entry_ids if candidate in dictionary_map]
    default selected_entry_id = entry_id if entry_id is not None else (_dict_ids[-1] if _dict_ids else None)
    $ _dict_len = len(_dict_ids)
    $ _row_h = 68
    $ _vp_h = 738
    $ _initial_scroll = 0.0
    if selected_entry_id not in dictionary_map:
        $ selected_entry_id = None
    if selected_entry_id in _dict_ids:
        $ _idx = _dict_ids.index(selected_entry_id)
        $ _max_scroll = max(1, _dict_len * _row_h - _vp_h)

        $ _target_y = max(0, _idx * _row_h - _vp_h // 2 + _row_h // 2)
        $ _initial_scroll = min(1.0, _target_y / float(_max_scroll))

    if selected_entry_id:
        on "show" action Function(persistent.dictionary_handler.read, id=selected_entry_id)
        on "replace" action Function(persistent.dictionary_handler.read, id=selected_entry_id)

    frame:
        background Solid("#0ff0")
        pos (190, 201)
        xysize (475, 738)

        has vpgrid

        id "dictionary_vp"
        cols 1
        yinitial _initial_scroll
        spacing 0

        mousewheel True
        xalign 0.5

        $ dict_len = _dict_len
        for index in range(dict_len):
            $ entry_id = _dict_ids[index]
            button:
                action [SetScreenVariable('selected_entry_id', entry_id),
                    Function(content_scroll.change, 0),
                    Function(persistent.dictionary_handler.read, id=entry_id)]

                selected selected_entry_id == entry_id

                background Solid("#fff0")
                hover_background Transform("gui/dictionary/selected_idle.png", alpha=0.24)
                selected_idle_background "gui/dictionary/selected_idle.png"
                selected_hover_background "gui/dictionary/selected_hover.png"
                xysize (478, 68)
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover.mp3"
                text _(dictionary_map[entry_id].title):
                    color "#687792"
                    hover_color "#304b7a"
                    selected_color "#fff"
                    size 35
                    align (0.0, 0.5)
                    xoffset 20

                if persistent.dictionary_handler.is_unread(entry_id):
                    text "NEW":
                        color "#f10e0e"
                        size 15

    vbar value YScrollValue("dictionary_vp"):
        pos (669, 212)
        xysize (26, 729)
        top_bar "gui/dictionary/bar.png"
        bottom_bar "gui/dictionary/bar.png"
        thumb "gui/dictionary/thumb.png"
        hover_thumb "gui/dictionary/hover_thumb.png"
        thumb_offset 10

    if selected_entry_id:
        $ selected_dict_entry = dictionary_map[selected_entry_id]

        frame:
            background Solid("#fff0")
            pos (898, 152)
            xysize (905, 81)

            text _(selected_dict_entry.title):
                align (0.0, 0.5)
                color "#fff"
                size 45

        frame:
            background Solid("#fff0")
            pos (898, 265)
            xysize (845, 701)

            has viewport
            id "dictionary_content_vp"
            yadjustment content_scroll
            mousewheel True
            draggable True

            text _(selected_dict_entry.content):
                color "#5b74ab"
                size 35


        vbar value YScrollValue("dictionary_content_vp"):
            pos (1760, 271)
            xysize (26, 689)
            top_bar "gui/dictionary/bar.png"
            bottom_bar "gui/dictionary/bar.png"
            thumb "gui/dictionary/thumb.png"
            hover_thumb "gui/dictionary/hover_thumb.png"
            thumb_offset 10
            unscrollable "hide"
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc

screen thanks_list():
    tag menu

    modal True
    zorder 100




    key 'mouseup_3' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())
    key 'K_ESCAPE' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())
    key 'game_menu' action If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return())

    add "gui/dictionary/bg.png"

    add ko_secondary_title("thanks", "gui/thanks/title.png"):
        pos (32, 15)






    use common_return_base(pos=(1769, 30), size='l', action=If(main_menu, true=ShowMenu("main_menu_extra", _transition=title_menu_transition), false=Return()))

    frame:
        background Solid("#0000")
        pos (860, 258)
        xysize (875, 701)

        has viewport

        id "thanks_vp"
        mousewheel True
        yinitial 0.0

        vbox:
            spacing 30
            for ts in ts_list:
                $ rows = (len(ts.items) + ts.config.columns - 1) // ts.config.columns
                frame:
                    background Solid("#fff0")
                    has vbox
                    spacing 8
                    hbox:
                        spacing 30
                        add "gui/thanks/cat.png":
                            pos (5, 5)

                        text _(ts.config.name):
                            size 35
                            color "#5b74ab"
                            font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                            adjust_spacing False

                    grid ts.config.columns rows:
                        xspacing 15
                        yspacing 15

                        for name in ts.items:
                            frame:
                                background None
                                xsize ts.config.xysize[0]
                                text name:
                                    size ts.config.font_size
                                    color "#adb8cf"
                                    font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                                    adjust_spacing False

    vbar value YScrollValue("thanks_vp"):
        pos (1770, 247)
        xysize (26, 729)
        top_bar Frame("gui/dictionary/bar.png")
        bottom_bar Frame("gui/dictionary/bar.png")
        thumb "gui/dictionary/thumb.png"
        hover_thumb "gui/dictionary/hover_thumb.png"
        thumb_offset 10

    frame:
        background Solid("#fff0")
        pos (880, 155)
        xysize (905, 81)

        text _("众筹感谢名单"):
            yoffset -3
            align (0.0, 0.5)
            color "#fff"
            size 45
            font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
            adjust_spacing False
    frame:
        background None
        pos (220, 210)
        xysize (526, 780)
        has viewport

        id "staff2"
        mousewheel True
        yinitial 0.0
        ymaximum 780

        vbox:
            spacing 25

            for sg in staff_groups:
                hbox:
                    spacing 12
                    if sg.title:
                        add "gui/thanks/crown.png":
                            ypos 8
                            zoom 1.2
                        vbox:

                            xsize 390
                            spacing 5
                            text _(sg.title):
                                size 35
                                color "#5b74ab"
                                font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                                adjust_spacing False
                            for member in sg.members:
                                text _(member):
                                    size 26
                                    color "#8a9bb8"
                                    font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                                    line_leading 12
                                    adjust_spacing False
                            if getattr(sg, "portraits", ()):
                                hbox:
                                    spacing 18
                                    for guest_name, guest_photo in sg.portraits:
                                        vbox:
                                            xsize 180
                                            spacing 10
                                            frame:
                                                padding (3, 3)
                                                background Solid("#adb8cf")
                                                add guest_photo:
                                                    xysize (174, 174)
                                            text _(guest_name):
                                                xalign 0.5
                                                textalign 0.5
                                                size 26
                                                color "#8a9bb8"
                                                font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                                                adjust_spacing False
                    else:
                        null width 35
                        vbox:
                            xsize 390
                            spacing 5
                            for member in sg.members:
                                text _(member):
                                    size 26
                                    color "#5b74ab"
                                    font (ko_ui_font if _preferences.language == "japanese" else "fonts/ChillRoundFRegular.otf")
                                    line_leading 12
                                    adjust_spacing False

    vbar value YScrollValue("staff2"):
        pos (670, 235)
        xysize (26, 729)
        top_bar "gui/dictionary/bar.png"
        bottom_bar "gui/dictionary/bar.png"
        thumb "gui/dictionary/thumb2.png"
        hover_thumb "gui/dictionary/hover_thumb2.png"
        thumb_offset 10
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc

screen gallery():
    tag menu
    key 'mouseup_3' action If(main_menu, ShowMenu("main_menu_extra", _transition=title_menu_transition), Return())
    key 'K_ESCAPE' action If(main_menu, ShowMenu("main_menu_extra", _transition=title_menu_transition), Return())
    key 'game_menu' action If(main_menu, ShowMenu("main_menu_extra", _transition=title_menu_transition), Return())

    default index = 0
    default section = "cg"
    $ page_len = gallery_page_manager.get_page_len()
    $ index = max(0, min(index, page_len - 1))
    $ cgs = gallery_page_manager.get_items(index)
    $ collection = gallery.get_fraction(None)

    add "gui/save/bg.png"
    add ko_secondary_title("gallery", "gui/gallery/title.png") pos (30, 14)
    use common_return_base(pos=(1769, 30), size='l', action=If(main_menu, ShowMenu("main_menu_extra", _transition=title_menu_transition), Return()))
    $ film_collection = "%d / %d" % (sum(_gallery_film_unlocked(film["key"]) for film in _gallery_films), len(_gallery_films))
    for divider_x in (748, 953, 1158):
        add Solid("#92a2c8", xysize=(2, 30)) pos (divider_x, 35)
    hbox:
        xcenter 954
        ypos 28
        spacing 4
        for tab_key, tab_title in (("cg", _("插画{#gallery}")), ("films", _("影片{#gallery}"))):
            imagebutton:
                id ("gallery_tab_" + tab_key)
                focus_mask (None if _preferences.language == "japanese" else True)
                idle ko_secondary_gallery_tab(tab_key, "idle")
                hover ko_secondary_gallery_tab(tab_key, "hover")
                selected_idle ko_secondary_gallery_tab(tab_key, "selected_idle")
                selected_hover ko_secondary_gallery_tab(tab_key, "selected_hover")
                alt tab_title
                action SetScreenVariable("section", tab_key)
                selected (section == tab_key)
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover2.mp3"

    text (_("已收集 [collection]") if section == "cg" else _("已解锁 [film_collection]")):
        style "gallery_caption"
        xpos 1710
        xanchor 1.0
        ypos 147
        size 22

    if section == "films":
        use gallery_films
    else:
        grid 3 2:
            xalign 0.5
            ypos 210
            xspacing 48
            yspacing 36
            for cg in cgs:
                $ group = _gallery_group_map[cg]
                $ cover = _gallery_cover(group)
                $ caption = _gallery_group_title(group) if cover else _("未解锁")
                fixed:
                    xysize (466, 316)
                    button:
                        id ("gallery_" + cg.replace(" ", "_"))
                        style "empty"
                        xysize (466, 279)
                        idle_foreground gallery.idle_border
                        hover_foreground gallery.hover_border
                        action (gallery.Action(cg) if cover else NullAction())
                        activate_sound ("sound/click.mp3" if cover else None)
                        hover_sound "sound/hover.mp3"
                        alt caption
                        if cover:
                            if "thumbnail_crop" in group:
                                add Transform(_gallery_entries[cover]["file"], crop=tuple(group["thumbnail_crop"]), xysize=(437, 246), pos=(10, 10))
                            else:
                                add Transform("gui/gallery/thumbs/" + cover + ".png", xysize=(437, 246), pos=(10, 10))
                        else:
                            add gallery.locked_button
                    if len(group["items"]) > 1:
                        hbox:
                            xpos 446
                            xanchor 1.0
                            ypos 268
                            for entry in group["items"]:
                                add GalleryDot(_gallery_entry_unlocked(entry["id"]))
            for empty in range(6 - len(cgs)):
                null width 466 height 316

        if page_len > 1:
            imagebutton:
                id "gallery_prev"
                pos (105, 508)
                auto "gui/save/btn_left_%s.png"
                action SetScreenVariable("index", (index - 1) % page_len)
                keysym "save_page_prev"
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover.mp3"
            imagebutton:
                id "gallery_next"
                pos (1750, 508)
                auto "gui/save/btn_right_%s.png"
                action SetScreenVariable("index", (index + 1) % page_len)
                keysym "save_page_next"
                activate_sound "sound/click.mp3"
                hover_sound "sound/hover.mp3"
            hbox:
                style_prefix "page"
                xalign 0.5
                ypos 930
                spacing 40
                for page in range(page_len):
                    textbutton "[page + 1]":
                        id ("gallery_page_" + str(page))
                        action SetScreenVariable("index", page)
                        selected (page == index)
    if _pad_state.instance is not None:
        hbox:
            id "controller_hint_row"
            xalign 0.5
            ypos 1008
            spacing 36
            use gallery_navigation_item(("dpad", "LS"), _("选择"))
            use gallery_navigation_item(("A",), _("确认"))
            use gallery_navigation_item(("B",), _("返回"))
            if section == "cg":
                use gallery_navigation_item(("LB", "RB"), _("翻页{#gallery}"))


screen fake_main_menu():
    tag menu



    timer 0.01 action Stop("music", fadeout=0.0)


    fixed:
        at fakemenu_fadein


        add "fake_menu_bg_dynamic"


        add "perform/fakemenu/fake_menu_purple.png"

        add "perform/fakemenu/fake_decoration.png":
            at mainbg_mask(0.9)

        add "perform/fakemenu/fake_title.png":
            at mainbg_title(0.9)
            xpos 960 ypos 360 xanchor 0.5 yanchor 0.5



        frame:
            background None
            align (0.5, 0.0)
            yoffset 670
            has grid 2 3
            xalign 0.5


            imagebutton:
                id "fm_start"
                focus_mask None
                idle ko_secondary_fake_button("start", "insensitive")
                hover ko_secondary_fake_button("start", "insensitive")
                action Show("fakemenu_alert")
                at main_btn_transform2(0.5)
                xoffset -638


            imagebutton:
                id "fm_extra"
                focus_mask None
                idle ko_secondary_fake_button("extra", "insensitive")
                hover ko_secondary_fake_button("extra", "insensitive")
                action Show("fakemenu_alert")
                at main_btn_transform(0.5)
                xoffset 638



            imagebutton:
                id "fm_continue"
                focus_mask None
                idle ko_secondary_fake_button("continue", "idle")
                hover ko_secondary_fake_button("continue", "hover")
                action Show("fake_confirm", message="结局已然圆满，你确定要继续吗？", yes_action=[Hide("fake_confirm"), SetVariable("fakemenu_bg_state", "exiting"), Show("fake_menu_farewell")], no_action=Hide("fake_confirm"))
                at main_btn_transform2(0.9)
                xoffset -560
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"


            imagebutton:
                id "fm_config"
                focus_mask None
                idle ko_secondary_fake_button("config", "insensitive")
                hover ko_secondary_fake_button("config", "insensitive")
                action Show("fakemenu_alert")
                at main_btn_transform(0.9)
                xoffset 560


            imagebutton:
                id "fm_load"
                focus_mask None
                idle ko_secondary_fake_button("load", "insensitive")
                hover ko_secondary_fake_button("load", "insensitive")
                action Show("fakemenu_alert")
                at main_btn_transform2(1.3)
                xoffset -402


            imagebutton:
                id "fm_exit"
                focus_mask None
                idle ko_secondary_fake_button("exit", "idle")
                hover ko_secondary_fake_button("exit", "hover")
                action Quit(confirm=False)
                at main_btn_transform(1.3)
                xoffset 402
                hover_sound "sound/hover2.mp3"
                activate_sound "sound/click2.mp3"






screen fake_menu_farewell():
    modal True
    zorder 100




    fixed:
        at fake_farewell_bg_pair_zoom
        add "perform/fakemenu/fake_menu_bg.png"
        add "perform/fakemenu/fake_menu_purple.png" at fake_purple_exit
        add "perform/fakemenu/fake_end_bg.png" at fake_farewell_layerC_fadein_dim


    add "perform/fakemenu/fake_decoration.png":
        at fake_decoration_exit(0.4)


    add "perform/fakemenu/fake_title.png":
        xpos 960 ypos 360 xanchor 0.5 yanchor 0.5
        at mainbg_title_exit(0.4)



    frame:
        background None
        align (0.5, 0.0)
        yoffset 670
        has grid 2 3
        xalign 0.5


        add ko_secondary_fake_button("start", "insensitive"):
            xoffset -638
            at main_btn_exit_transform2(0.8)

        add ko_secondary_fake_button("extra", "insensitive"):
            xoffset 638
            at main_btn_exit_transform(0.8)

        add ko_secondary_fake_button("continue", "idle"):
            xoffset -560
            at main_btn_exit_transform2(0.4)

        add ko_secondary_fake_button("config", "insensitive"):
            xoffset 560
            at main_btn_exit_transform(0.4)

        add ko_secondary_fake_button("load", "insensitive"):
            xoffset -402
            at main_btn_exit_transform2(0.0)

        add ko_secondary_fake_button("exit", "idle"):
            xoffset 402
            at main_btn_exit_transform(0.0)


    timer 4.0 action Start("plotend")
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc

screen fakemenu_alert():
    modal False
    fixed:
        xysize (1038, 55)
        at fakemenu_alert_fade
        xalign 0.5
        yalign 0.72
        add ko_secondary_fake_alert("title")
    timer 1.0 action Hide("fakemenu_alert")




screen plotend_alert():
    modal False
    fixed:
        xysize (1038, 55)
        at fakemenu_alert_fade
        xalign 0.5
        yalign 0.5
        add ko_secondary_fake_alert("plotend")
    timer 1.0 action Hide("plotend_alert")







# Source: scripts/screens/creator_game_menu.rpy; only the title displayable differs.
screen creator_game_menu():
    tag menu

    add "gui/menu/bg.png"
    add ko_secondary_menu_title():
        pos (1736, 35)
    use common_return_base(pos=(1825, 10), size='s')

    default buttons = [
        "title",
        "preferences",
        "dictionary",
        "history",
        "load",
        "save",
    ]

    for index, btn in enumerate(buttons):
        button:
            id ("menu_" + btn)
            focus_mask True
            default_focus (btn == "save")
            at menu_button_t(index)
            background f"gui/menu/{btn}_idle.png"
            hover_background f"gui/menu/{btn}_hover.png"
            activate_sound "sound/click.mp3"
            hover_sound "sound/hover.mp3"
            xysize (329, 67)

            text _(btn):
                size 30
                color "#526486"
                hover_color "#cbcdd3"
                align (0.0, 0.5)
                offset (63.5, -5)

            if btn == "title":
                action [
                    SetVariable("persistent.main_bg_played", False),
                    SigniMainMenu()
                ]
            else:
                action ShowMenu(btn)
