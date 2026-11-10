# Korean why-page unit; preserve Japanese 30 characters per row and cutoff timing.
init 190 python:
    _ko_original_p9_why_page = p9_why_page
    def p9_why_page(unit):
        if unit in ("왜？", "왜?"):
            return "\n".join(["왜？" * 15] * 8)
        return _ko_original_p9_why_page(unit)
