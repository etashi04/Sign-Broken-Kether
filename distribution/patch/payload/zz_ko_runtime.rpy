# Korean localization support. No original assets or scripts are replaced on disk.
init -5 python:
    ko_ui_font = FontGroup().add("fonts/ko/GowunDodum-Regular.ttf", 0xAC00, 0xD7A3).add("fonts/ko/GowunDodum-Regular.ttf", 0x1100, 0x11FF).add("fonts/ko/GowunDodum-Regular.ttf", 0x3130, 0x318F).add("fonts/ChillRoundFRegular.otf", None, None)

    # rc22: use native Korean-face punctuation with matched !/? advances.
    # Source Han dialogue keeps its existing halt treatment; only this UI group
    # changes. Original font files and stored text are preserved.
    for _ko_cp in map(ord, "！？「」『』（）"):
        ko_ui_font.add("fonts/ko/SignKoreanUIPunctuation-Regular.ttf", _ko_cp, _ko_cp)

    # rc24: regular punctuation uses the same face as Korean UI letters.
    # Explicit bold/font tags still take precedence in native text layout.
    for _ko_cp in map(ord, ".,·:;…‥。，、：；"):
        ko_ui_font.add("fonts/ko/GowunDodum-Regular.ttf", _ko_cp, _ko_cp)

    # Only characters absent from the original UI face use fallback fonts.
    # Preserve credited names and intentional block/glitch characters verbatim.
    for _ko_cp in (0x2588, 0x3405, 0x66D1, 0x7071, 0x71D1, 0x782F):
        ko_ui_font.add("fonts/SourceHanSerifSC-Regular.otf", _ko_cp, _ko_cp)
    for _ko_cp in (0x02C4, 0x0348, 0x208D, 0x208E, 0x25DE, 0x2714, 0x2718):
        ko_ui_font.add("DejaVuSans.ttf", _ko_cp, _ko_cp)
    ko_ui_font.add("fonts/ko/NotoSerifTibetan.ttf", 0x0F1D, 0x0F1D)

init 101 python:
    _ko_asset_labels = {
        "general/fullscreen": ("전체 화면", 338, 88, 33),
        "general/windows": ("창 모드", 338, 88, 33),
        "general/skip_yes": ("스킵", 338, 88, 33),
        "general/skip_no": ("스킵 안 함", 338, 88, 33),
        "general/yes": ("켜기", 338, 88, 33),
        "general/no": ("끄기", 338, 88, 33),
        "radio/general": ("기본 설정", 201, 42, 29),
        "radio/audio": ("소리 설정", 201, 42, 29),
        "radio/guide": ("키보드 · 마우스", 201, 42, 27),
        "radio/gamepad": ("컨트롤러", 201, 42, 29),
        "shared/reset": ("기본 설정 복원", 265, 65, 28),
        "shared/title": ("타이틀 화면으로", 265, 65, 28),
        "confirm/yes": ("확인", 338, 88, 33),
        "confirm/no": ("취소", 338, 88, 33),
    }

    def ko_config_asset(path):
        if _preferences.language != "japanese":
            if not renpy.loadable(path):
                path = path.replace("_selected_hover", "_hover").replace("_selected_idle", "_idle")
            return path
        tail = path[len("gui/config/"):-4] if path.startswith("gui/config/") else path[len("gui/"):-4]
        for state in ("selected_hover", "selected_idle", "hover", "idle"):
            if tail.endswith("_" + state):
                key = tail[:-len(state)-1]
                break
        if key not in _ko_asset_labels:
            return path
        label, width, height, size = _ko_asset_labels[key]
        selected = state.startswith("selected")
        background = Frame("gui/config/audio/name_" + state + ".png", 8, 8)
        color = "#ffffff" if selected else "#58719f"
        if key.startswith("radio/"):
            color = "#ffffff" if selected else "#edf3ff"
            background = Solid("#dae5ff35" if selected else "#00000000")
        # The source button has padding; native text keeps every label crisp at any scale.
        return Fixed(Transform(background, xysize=(width-8, height-10), align=(0.5,0.5)),
            Text(label, font=ko_ui_font, size=size, color=color, text_align=0.5, align=(0.5,0.5), layout="nobreak"),
            xysize=(width,height))

    def ko_config_title():
        if _preferences.language != "japanese":
            return "gui/config/shared/title.png"
        return VBox(Text("설정", font=ko_ui_font, size=49, color="#ffffff"),
            Text("S E T T I N G", font="fonts/ChillRoundFRegular.otf", size=12, color="#ffffff"), spacing=-7)

    def ko_main_menu_asset(path):
        if _preferences.language != "japanese":
            return path
        key, state = path[len("gui/main_menu/"):-4].rsplit("_", 1)
        labels = {"start":"게임 시작", "continue":"이어하기", "load":"불러오기", "config":"설정",
            "extra":"추가 콘텐츠", "exit":"게임 종료", "staff":"제작진", "gallery":"갤러리",
            "dictionary":"용어사전", "prequel":"전일담", "back":"돌아가기"}
        if key not in labels:
            return path
        left = key in ("start", "load", "extra", "staff", "dictionary", "back")
        color = "#92a9c8" if state == "insensitive" else "#ffffff"
        children = []
        if state == "hover":
            children.append(Transform(path, crop=(2,2,8,8), xysize=(292,116), pos=(2,5)))
        # Keep the original star ornament and English sublabel as native crops.
        star_x = 0 if left else 220
        children.append(Transform(path, crop=(star_x,0,80,80), pos=(star_x,0)))
        children.append(Transform(path, crop=(0,80,300,46), pos=(0,80)))
        children.append(Text(labels[key], font=ko_ui_font, size=42 if key=="extra" else 45,
            color=color, xcenter=180 if left else 120, ycenter=48, layout="nobreak"))
        return Fixed(*children, xysize=(300,126))

translate japanese python:
    gui.text_font = ko_ui_font
    gui.name_text_font = ko_ui_font
    gui.interface_text_font = ko_ui_font
    for _ko_style in renpy.style.styles.values():
        if _ko_style.font == "fonts/ChillRoundFRegular.otf":
            _ko_style.font = ko_ui_font
    style.default.font = ko_ui_font
    style.gui_text.font = ko_ui_font
    style.button_text.font = ko_ui_font
    style.config_title_text.font = ko_ui_font
    style.controller_hint_text.font = ko_ui_font
    style.say_dialogue.font = ko_ui_font
    style.say_label.font = ko_ui_font
    style.history_text.font = ko_ui_font
    style.nvl_dialogue.font = ko_ui_font
    style.nvl_thought.font = ko_ui_font
    style.nvl_label.font = ko_ui_font
    style.center_subtitle_nvl.font = ko_ui_font

translate japanese style controller_guide_description:
    font ko_ui_font
translate japanese style controller_guide_caption:
    font ko_ui_font
translate japanese style controller_guide_note:
    font ko_ui_font
translate japanese style config_title_text:
    font ko_ui_font
    yoffset -42

screen config_guide():
    tag menu
    if _preferences.language == "japanese":
        fixed:
            pos (-116, -180)
            xysize (1920,1080)
            text "키보드 · 마우스 조작":
                font ko_ui_font
                color "#5871a5"
                size 38
                pos (208,190)
            for column, items in enumerate((
                (("왼쪽 클릭 / 휠 아래 / Enter", "다음 대사"),
                 ("Esc / 오른쪽 클릭", "메뉴 열기 / 닫기"),
                 ("Ctrl 길게 누르기", "대사 스킵"),
                 ("휠 위로", "대화 기록"),
                 ("Tab", "설정 열기")),
                (("가운데 클릭 / Space", "화면 숨기기"),
                 ("F / Alt + Enter", "화면 모드 전환"),
                 ("F12", "스크린샷"),
                 ("Alt + F4", "게임 종료"),
                 ("A", "자동 진행")))):
                for row, (keys, meaning) in enumerate(items):
                    hbox:
                        pos (205 + column * 815, 300 + row * 107)
                        spacing 25
                        frame:
                            background Frame("gui/config/audio/name_idle.png",8,8)
                            xysize (375,68)
                            text keys:
                                font ko_ui_font
                                color "#435b87"
                                size 26
                                align (0.5,0.5)
                        text meaning:
                            font ko_ui_font
                            color "#5871a5"
                            size 29
                            yalign 0.5
            text "마우스 커서를 화면 오른쪽 아래로 옮기면 퀵 메뉴가 나타납니다.":
                font ko_ui_font
                color "#5871a5"
                size 30
                pos (208,925)
    else:
        add "gui/config/shared/help.png":
            pos (-116,-180)
            xysize (config.screen_width,config.screen_height)
