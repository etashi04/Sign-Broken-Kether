# Copy-only Korean patch: reconstruct localized resources from the owned game.
init -999 python:
    def _etashi_prepare_manual_resources():
        import importlib.util
        import os
        import renpy.pygame
        path = os.path.join(config.gamedir, "ko_patch_resources", "runtime.py")
        spec = importlib.util.spec_from_file_location("_sign_ko_manual_resources", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.prepare(config.basedir, renpy.pygame)

    if _etashi_prepare_manual_resources():
        renpy.loader.common_files[:] = []
        renpy.loader.game_files[:] = []
        renpy.loader.loadable_cache.clear()
        renpy.loader.scandirfiles()
    del _etashi_prepare_manual_resources
