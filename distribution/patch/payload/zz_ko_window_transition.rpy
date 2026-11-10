# rc47: follow native scry routing when selecting a translated NVL window.
# Inspect translated speakers without evaluating dialogue arguments, Python
# bodies or transition expressions. Retain the synchronous end_page scope.
init 300 python:
    import re as _ko_window_re

    def _ko_window_nvl_target(node, limit=20):
        translated = False
        visited = set()
        for unused in range(limit):
            if node is None or id(node) in visited:
                return None
            visited.add(id(node))
            if isinstance(node, renpy.ast.TranslateSay) and node.language is None:
                target = node.lookup()
                if target is node or target is None:
                    return None
                translated = True
                node = target
                # A translated Say consumes the source Say's lookahead slot.
                # Do not let TranslateSay.scry skip it or Say.scry eval args.
            if isinstance(node, renpy.ast.Say):
                name = node.who
                if not translated or not isinstance(name, str) or not _ko_window_re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                    return None
                namespace = getattr(store, 'character', None)
                character = vars(namespace).get(name) if namespace is not None else None
                if character is None:
                    character = vars(store).get(name)
                return character if isinstance(character, NVLCharacter) else None
            if isinstance(node, renpy.ast.Translate):
                if node.language is None:
                    target = node.lookup()
                    if target is node or target is None:
                        return None
                    translated = True
                    node = target
                else:
                    node = node.block[0] if node.block else node.next
                continue
            # Native empty-window selection walks scry._next, including setup
            # Python and With nodes. Their scry methods do not execute them.
            # Native calls/branches/menus stop; static jumps keep their target.
            # Custom statements retain their own registered scry routing.
            future = node.scry()
            if future is None or future.say or future.menu_with_caption:
                return None
            node = future._next
        return None

    _ko_original_empty_window = config.empty_window

    def _ko_make_end_page_scope():
        # Ordinary Python state is deliberately outside Ren'Py rollback state.
        # Every synchronous call removes its entry even on load/rollback/error.
        stack = __import__('builtins').list()

        def enter(who):
            context = renpy.game.context()
            stack.append((context, context.current, who))

        def leave():
            stack.pop()

        def active():
            if not stack:
                return False
            context, node, unused = stack[-1]
            current = renpy.game.context()
            return current is context and current.current == node

        def target():
            if not stack:
                return None
            context, node, who = stack[-1]
            current = renpy.game.context()
            if current is context and current.current == node and isinstance(who, NVLCharacter):
                return who
            return None

        return enter, leave, target, active

    _ko_enter_end_page, _ko_leave_end_page, _ko_end_page_target, _ko_end_page_active = _ko_make_end_page_scope()
    _ko_original_end_page = end_page

    def _ko_window_end_page(*args, **kwargs):
        who = args[0] if args else kwargs.get('who')
        _ko_enter_end_page(who)
        try:
            return _ko_original_end_page(*args, **kwargs)
        finally:
            _ko_leave_end_page()

    end_page = _ko_window_end_page

    def _ko_translated_empty_window():
        target = None
        if (_preferences.language == 'japanese' and store._window_next
                and renpy.get_statement_name() != 'window hide'):
            target = _ko_end_page_target()
            try:
                # An actual ADV/None page call must not inherit a later NVL.
                if not _ko_end_page_active():
                    current = renpy.game.script.lookup(renpy.game.context().current)
                    target = _ko_window_nvl_target(current)
            except Exception:
                pass
        if target is not None:
            return nvl_show_core()
        return _ko_original_empty_window()

    config.empty_window = _ko_translated_empty_window
