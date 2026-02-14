import cv2
import numpy as np
import time

# ── Style ─────────────────────────────────────────────────────────────────────
PANEL_BG    = np.array([0.07, 0.07, 0.07], dtype=np.float64)
PANEL_ALPHA = 0.75
TEXT        = (0.88, 0.88, 0.88)
DIM         = (0.42, 0.42, 0.42)
ACCENT      = (0.25, 0.82, 0.25)
HANDLE      = (1.0,  1.0,  1.0)
TRACK       = (0.30, 0.30, 0.30)
ACTIVE_BG   = np.array([0.15, 0.15, 0.15], dtype=np.float64)

FONT = cv2.FONT_HERSHEY_SIMPLEX
FS   = 0.38
FT   = 1

# ── Layout constants ───────────────────────────────────────────────────────────
PANEL_W  = 160
PAD      = 10
ROW_H    = 35
ITEM_H   = 30
SEARCH_H = 22


# ── Helpers ────────────────────────────────────────────────────────────────────
def _blend(canvas, x1, y1, x2, y2, color, alpha):
    """Blend a solid rectangle onto a float64 canvas in-place."""
    h, w = canvas.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return
    roi = canvas[y1:y2, x1:x2]
    roi[:] = roi * (1.0 - alpha) + color * alpha


def _text(canvas, s, x, y, color=TEXT, scale=FS, thickness=FT):
    cv2.putText(canvas, s, (int(x), int(y)), FONT, scale, color, thickness, cv2.LINE_AA)


def _text_w(s, scale=FS, thickness=FT):
    return cv2.getTextSize(s, FONT, scale, thickness)[0][0]


# ── Slider ─────────────────────────────────────────────────────────────────────
class Slider:
    TRACK_OFF = 20   # track y below slider.ly (leaves room for label above)
    HANDLE_R  = 5

    def __init__(self, label, lo, hi, default, is_int=False):
        self.label    = label
        self.lo       = float(lo)
        self.hi       = float(hi)
        self.value    = float(default)
        self.is_int   = is_int
        self.dragging = False
        self.lx = self.ly = self.w = 0   # set by layout

    @property
    def int_value(self):
        return int(round(self.value))

    def _hx(self):
        if self.hi == self.lo:
            return self.lx
        t = (self.value - self.lo) / (self.hi - self.lo)
        return int(self.lx + t * self.w)

    def draw(self, canvas):
        val_str = str(self.int_value) if self.is_int else f"{self.value:.2f}"
        _text(canvas, f"{self.label}: {val_str}", self.lx, self.ly + 12)
        ty = self.ly + self.TRACK_OFF
        rx = self.lx + self.w
        cv2.line(canvas, (self.lx, ty), (rx, ty), TRACK, 1)
        hx = self._hx()
        cv2.line(canvas, (self.lx, ty), (hx, ty), ACCENT, 2)
        cv2.circle(canvas, (hx, ty), self.HANDLE_R, HANDLE, -1, cv2.LINE_AA)

    def hit(self, mx, my):
        ty = self.ly + self.TRACK_OFF
        return (self.lx - 4 <= mx <= self.lx + self.w + 4) and abs(my - ty) <= self.HANDLE_R + 5

    def update(self, mx):
        t = max(0.0, min(1.0, (mx - self.lx) / max(self.w, 1)))
        self.value = self.lo + t * (self.hi - self.lo)
        if self.is_int:
            self.value = float(int(round(self.value)))


# ── SearchBar ──────────────────────────────────────────────────────────────────
class SearchBar:
    def __init__(self):
        self.text   = ""
        self.active = False
        self.lx = self.ly = self.w = 0

    def draw(self, canvas):
        _blend(canvas, self.lx, self.ly, self.lx + self.w, self.ly + SEARCH_H, ACTIVE_BG, 0.9)
        border = ACCENT if self.active else TRACK
        cv2.rectangle(canvas, (self.lx, self.ly), (self.lx + self.w - 1, self.ly + SEARCH_H - 1), border, 1)
        disp = self.text
        if self.active and int(time.time() * 2) % 2 == 0:
            disp += "|"
        color = TEXT if self.text else DIM
        _text(canvas, disp or "search...", self.lx + 4, self.ly + 15, color)

    def hit(self, mx, my):
        return self.lx <= mx <= self.lx + self.w and self.ly <= my <= self.ly + SEARCH_H

    def handle_key(self, key):
        if key == 8:           # backspace
            self.text = self.text[:-1]
        elif 32 <= key < 127:  # printable ASCII
            self.text += chr(key)


# ── UIOverlay ──────────────────────────────────────────────────────────────────
class UIOverlay:
    HINTS = [
        ("[h]",     "toggle UI"),
        ("[space]", "pause"),
        ("[c]",     "clear"),
        ("[q]",     "quit"),
    ]

    def __init__(self, canvas_w, canvas_h, drawing_classes,
                 new_drawing_chance=0.1, fade_rate=0.97, max_drawings=0):
        self.visible = True
        self.cw      = canvas_w
        self.ch      = canvas_h
        self.drawing_classes = drawing_classes

        # Global sliders
        self.chance_sl = Slider("Chance %",    0,  100, int(new_drawing_chance * 100), is_int=True)
        self.fade_sl   = Slider("Fade (x100)", 90, 100, int(fade_rate * 100),          is_int=True)
        self.max_sl    = Slider("Max Drawings", 0,  50,  max_drawings,                  is_int=True)
        self._global   = [self.chance_sl, self.fade_sl, self.max_sl]

        # Per-drawing weight sliders (default weight 5, all enabled)
        self._weights = {
            cls.__name__: Slider(cls.__name__, 0, 10, 5, is_int=True)
            for cls in drawing_classes
        }

        self.search       = SearchBar()
        self.scroll       = 0
        self._drag_slider = None

        self._do_layout()

    # ── Properties read by ArtGenerator ──────────────────────────────────────
    @property
    def new_drawing_chance(self):
        return self.chance_sl.int_value / 100.0

    @property
    def fade_rate(self):
        return self.fade_sl.int_value / 100.0

    @property
    def max_drawings(self):
        return self.max_sl.int_value

    def get_weights(self):
        return [self._weights[cls.__name__].int_value for cls in self.drawing_classes]

    # ── Layout ────────────────────────────────────────────────────────────────
    def _do_layout(self):
        sw = PANEL_W - 2 * PAD

        # Left panel: title at y=PAD+12, then sliders
        ly = PAD + 20
        for s in self._global:
            s.lx, s.ly, s.w = PAD, ly, sw
            ly += ROW_H

        # Right panel
        rx = self.cw - PANEL_W + PAD
        ry = PAD + 20
        self.search.lx, self.search.ly, self.search.w = rx, ry, sw
        self._list_top = ry + SEARCH_H + 4
        self._rx = rx
        self._rw = sw

    # ── Filtered drawing list ─────────────────────────────────────────────────
    def _items(self):
        q = self.search.text.lower()
        items = list(self._weights.items())
        if q:
            items = [(n, s) for n, s in items if q in n.lower()]
        return items

    def _visible_count(self):
        return max(0, (self.ch - self._list_top) // ITEM_H)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, canvas):
        if not self.visible:
            return

        # ---- Left panel ----
        _blend(canvas, 0, 0, PANEL_W, self.ch, PANEL_BG, PANEL_ALPHA)
        _text(canvas, "Controls", PAD, PAD + 12, ACCENT, FS + 0.04, FT)

        for s in self._global:
            s.draw(canvas)

        hy = self._global[-1].ly + ROW_H + 2
        for key, desc in self.HINTS:
            kw = _text_w(key)
            _text(canvas, key,  PAD,           hy, ACCENT)
            _text(canvas, desc, PAD + kw + 5,  hy, TEXT)
            hy += 17

        # ---- Right panel ----
        _blend(canvas, self.cw - PANEL_W, 0, self.cw, self.ch, PANEL_BG, PANEL_ALPHA)
        _text(canvas, "Drawing Weights", self._rx, PAD + 12, ACCENT, FS + 0.04, FT)

        self.search.draw(canvas)

        items = self._items()
        vc    = self._visible_count()
        self.scroll = max(0, min(self.scroll, max(0, len(items) - vc)))

        for i, (name, sl) in enumerate(items[self.scroll: self.scroll + vc]):
            sl.lx = self._rx
            sl.ly = self._list_top + i * ITEM_H
            sl.w  = self._rw
            sl.draw(canvas)

        if len(items) > vc:
            lo = self.scroll + 1
            hi = min(self.scroll + vc, len(items))
            _text(canvas, f"{lo}-{hi} / {len(items)}", self._rx, self.ch - PAD, DIM)

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_mouse(self, event, x, y, flags, param):
        if not self.visible:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            # Search bar
            if self.search.hit(x, y):
                self.search.active = True
                return
            self.search.active = False

            # Global sliders
            for s in self._global:
                if s.hit(x, y):
                    s.update(x)
                    s.dragging        = True
                    self._drag_slider = s
                    return

            # Visible weight sliders
            items = self._items()
            vc    = self._visible_count()
            for _, sl in items[self.scroll: self.scroll + vc]:
                if sl.hit(x, y):
                    sl.update(x)
                    sl.dragging       = True
                    self._drag_slider = sl
                    return

        elif event == cv2.EVENT_MOUSEMOVE:
            if self._drag_slider:
                self._drag_slider.update(x)

        elif event == cv2.EVENT_LBUTTONUP:
            if self._drag_slider:
                self._drag_slider.dragging = False
                self._drag_slider = None

        elif event == cv2.EVENT_MOUSEWHEEL:
            if x >= self.cw - PANEL_W:   # only scroll when over right panel
                self.scroll += (-1 if flags > 0 else 1)

    def handle_key(self, key):
        """Returns True if the key was consumed by the UI."""
        if key == 27:   # Escape — deactivate search
            self.search.active = False
            return True
        if self.search.active:
            self.search.handle_key(key)
            return True
        return False
