# rc31: approved 18px dictionary notification, original 459x80 background.
init offset = 235

init python:
    import unicodedata as _ko_notice_unicode

    def ko_dictionary_object_particle(title):
        # Read numbered entries as Korean numerals: ①=일, ②=이, etc.
        plain = _ko_notice_unicode.normalize("NFKC", renpy.filter_text_tags(title, allow=[])).rstrip(" \t\n'\"’”)]}〉》」』")
        last = plain[-1:] or " "
        if "가" <= last <= "힣":
            final = (ord(last) - 0xAC00) % 28 != 0
        elif last.isascii() and last.isdigit():
            final = last in "013678"
        else:
            # Current Latin titles are JK(제이케이) and ID(아이디).
            # Korean letter names L/M/N/R end in a consonant.
            final = last.upper() in ("L", "M", "N", "R")
        return "을" if final else "를"

    def ko_dictionary_notification_message(title):
        return "용어 ‘" + title + "’" + ko_dictionary_object_particle(title) + " 열람할 수 있습니다"

    if not hasattr(PersistentDictionaryHandler, "_ko_original_add"):
        PersistentDictionaryHandler._ko_original_add = PersistentDictionaryHandler.add

    def _ko_dictionary_add(self, id, name_cn=None, notify_text_scale=1.0):
        if _preferences.language != "japanese":
            return self._ko_original_add(id, name_cn, notify_text_scale)
        if id not in self.entry_ids:
            self.entry_ids.append(id)
            self.unread_ids.add(id)
        if name_cn:
            message = ko_dictionary_notification_message(renpy.translate_string(name_cn))
            if notify_text_scale == 1.0:
                renpy.notify(message)
            else:
                scaled_notify(message, notify_text_scale)
            narrator.add_history(kind="dictionary", who=None, what=message)

    PersistentDictionaryHandler.add = _ko_dictionary_add

    def ko_is_dictionary_notification(message):
        return (_preferences.language == "japanese"
            and isinstance(message, str)
            and message.startswith("용어 ‘")
            and message.endswith(("’을 열람할 수 있습니다", "’를 열람할 수 있습니다")))

screen notify(message, text_scale=1.0):
    zorder 100
    style_prefix "notify"
    $ _ko_dictionary_notice = ko_is_dictionary_notification(message)

    frame at notify_appear:
        text "[message!tq]":
            size (18 if _ko_dictionary_notice else int(gui.notify_text_size * text_scale))
            properties ({"xsize": 350, "language": "korean-with-spaces", "line_spacing": 0, "yoffset": 0} if _ko_dictionary_notice else {})

    timer 3.25 action Hide('notify')
