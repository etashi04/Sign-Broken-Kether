# ETASHI unofficial Korean localization, Japanese language slot.
# Select Korean on the first patched launch; retain later manual choices.
init 240 python:
    config.language = None if persistent.etashi_ko_default_v1 else "japanese"

    # The original splash screen calls this after Ren'Py's initial language
    # selection. Its OS-language detection otherwise resets ko_KR to Chinese.
    def set_language_automatically():
        if not persistent.etashi_ko_default_v1:
            renpy.change_language("japanese")
            persistent.etashi_ko_default_v1 = True
            renpy.save_persistent()
