# OP/ED timed Korean captions. Chapter titles are baked into replacement videos.
init 195 python:
    import json as _ko_video_json
    import re as _ko_video_re
    with renpy.file("ko_video_subtitles.json") as _ko_video_file:
        _ko_video_data = _ko_video_json.load(_ko_video_file)
    if not hasattr(renpy.display.video.Movie, "_ko_unmodified_render"):
        renpy.display.video.Movie._ko_unmodified_render = renpy.display.video.Movie.render
    _ko_video_original_render = renpy.display.video.Movie._ko_unmodified_render
    _ko_video_caption_cache = {}

    def ko_video_key(path):
        if not isinstance(path, str):
            return None
        path = _ko_video_re.sub(r"<[^>]*>", "", path).replace("\\", "/")
        if path.startswith("tl/japanese/"):
            path = path[len("tl/japanese/"):]
        if path.startswith("videos/"):
            path = "audio/" + path
        return path

    def ko_video_cues(path, seconds):
        record = _ko_video_data.get(ko_video_key(path), {})
        return record, [c for c in record.get("cues", ()) if c["start"] <= seconds < c["end"]]

    def ko_video_alpha(cue, seconds):
        fade_in = cue.get("fade_in", 0.45)
        fade_out = cue.get("fade_out", 0.45)
        a = max(0.0, min(1.0, (seconds-cue["start"])/fade_in, (cue["end"]-seconds)/fade_out))
        return a*a*(3.0-2.0*a)

    def ko_video_caption_layer(path, seconds):
        key = ko_video_key(path)
        # Never add a live mask or title on top of the baked chapter videos.
        if key not in ("audio/videos/op.webm", "movie/ED.webm"):
            return None
        record, cues = ko_video_cues(path, seconds)
        if not cues:
            return None
        layers = []
        for cue in cues:
            if key == "movie/ED.webm":
                closing = cue.get("kind") == "closing"
                caption = Text(cue["text"], font=ko_ui_font, size=40, italic=True,
                    color="#272936" if closing else "#fff", xpos=cue.get("xpos", 80), xanchor=cue.get("xanchor", 0.0), ypos=cue.get("ypos", 96),
                    xmaximum=1760 if closing else 900, text_align=cue.get("text_align", 0.0),
                    outlines=[] if closing else [(0, "#182332cc", 2, 3), (1, "#36425280", 0, 0)], line_spacing=3)
                layers.append(Transform(caption, alpha=ko_video_alpha(cue, seconds)))
            else:
                layers.append(Text(cue["text"], font=ko_ui_font, size=56, color="#fff",
                    xpos=960, xanchor=0.5, ypos=972, yanchor=1.0, xmaximum=1856,
                    text_align=0.5, outlines=[(2, "#101927e0", 0, 0)], line_spacing=3))
        return Fixed(*layers, xysize=(1920,1080))

    def ko_video_composite(base, playing, seconds, st, at, channel="qa"):
        if ko_video_key(playing) not in ("audio/videos/op.webm", "movie/ED.webm"):
            return base
        w,h = base.get_size()
        if not w or not h:
            return base
        cache_key = (ko_video_key(playing), int(seconds*30), w, h)
        cached = _ko_video_caption_cache.get(channel)
        if cached is None or cached[0] != cache_key:
            layer = ko_video_caption_layer(playing, seconds)
            if layer is not None and (w,h) != (1920,1080):
                layer = Transform(layer, xysize=(w,h))
            cached = (cache_key, layer)
            _ko_video_caption_cache[channel] = cached
        if cached[1] is None:
            return base
        result = renpy.Render(w,h)
        result.blit(base,(0,0))
        result.blit(renpy.render(cached[1],w,h,st,at),(0,0))
        return result

    def _ko_video_render(self, width, height, st, at):
        base = _ko_video_original_render(self, width, height, st, at)
        if _preferences.language != "japanese":
            return base
        playing = renpy.music.get_playing(channel=self.channel)
        if ko_video_key(playing) not in ("audio/videos/op.webm", "movie/ED.webm"):
            return base
        seconds = renpy.music.get_pos(channel=self.channel)
        if seconds is None:
            return base
        return ko_video_composite(base, playing, seconds, st, at, self.channel)

    renpy.display.video.Movie.render = _ko_video_render
