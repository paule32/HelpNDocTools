import sys
import math

from dataclasses     import dataclass
from PyQt5.QtCore    import (
    Qt, QTimer, QPointF
)
from PyQt5.QtGui     import (
    QPainter, QPen, QColor, QLinearGradient, QRadialGradient, QBrush,
    QPainterPath, QPolygonF
)
from PyQt5.QtWidgets import QApplication, QWidget

@dataclass
class Vec4:
    x: float
    y: float
    z: float
    w: float

@dataclass
class Vec3:
    x: float
    y: float
    z: float

def rotate4d(v: Vec4, a: int, b: int, angle: float) -> Vec4:
    s, c = math.sin(angle), math.cos(angle)
    comp = [v.x, v.y, v.z, v.w]
    va, vb = comp[a], comp[b]
    comp[a] = va * c - vb * s
    comp[b] = va * s + vb * c
    return Vec4(*comp)

def project_4d_to_3d(v: Vec4, w_dist: float = 3.2) -> Vec3:
    denom = (w_dist - v.w)
    if abs(denom) < 1e-4:
        denom = 1e-4 if denom >= 0 else -1e-4
    f = w_dist / denom
    return Vec3(v.x * f, v.y * f, v.z * f)

def project_3d_to_2d(v: Vec3, z_dist: float = 5.0):
    denom = (z_dist - v.z)
    if abs(denom) < 1e-4:
        denom = 1e-4 if denom >= 0 else -1e-4
    f = z_dist / denom
    return v.x * f, v.y * f

def draw_edge_gradient(
    p: QPainter, x1, y1, x2, y2, c1: QColor, c2: QColor,
    width: float, opacity: float):
    grad = QLinearGradient(x1, y1, x2, y2)
    grad.setColorAt(0.0, c1)
    grad.setColorAt(1.0, c2)
    pen = QPen(QBrush(grad), width)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setOpacity(opacity)
    p.setPen(pen)
    p.drawLine(int(x1), int(y1), int(x2), int(y2))

class Teaser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("4D Teaser – Innerer Würfel mit Oberfläche (PyQt5/QPainter)")
        self.resize(1100, 650)

        # 16 vertices: all combinations of ±1 in x,y,z,w
        self.verts = []
        for x in (-1, 1):
            for y in (-1, 1):
                for z in (-1, 1):
                    for w in (-1, 1):
                        self.verts.append(Vec4(x, y, z, w))

        # edges: vertices differing by exactly one coordinate
        self.edges = []
        for i, a in enumerate(self.verts):
            for j in range(i + 1, len(self.verts)):
                b = self.verts[j]
                diff = (a.x != b.x) + (a.y != b.y) + (a.z != b.z) + (a.w != b.w)
                if diff == 1:
                    self.edges.append((i, j))

        self.t = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def tick(self):
        self.t += 0.016
        self.update()

    def classify_edge(self, i: int, j: int) -> str:
        wi = self.verts[i].w
        wj = self.verts[j].w
        if wi == wj == -1:
            return "wneg"   # inner cube (w=-1)
        if wi == wj == +1:
            return "wpos"   # outer cube (w=+1)
        return "conn"

    # ---- BACKGROUND TEXTURE ----
    def paint_color_texture(self, p: QPainter, w: int, h: int):
        shift = 0.5 + 0.5 * math.sin(self.t * 0.35)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.00, QColor(8, 10, 18))
        grad.setColorAt(0.35 + 0.10 * shift, QColor(18, 120, 170))
        grad.setColorAt(0.70 - 0.10 * shift, QColor(140, 40, 185))
        grad.setColorAt(1.00, QColor(4, 5, 10))
        p.fillRect(0, 0, w, h, grad)

        p.setCompositionMode(QPainter.CompositionMode_Screen)
        p.setOpacity(0.35)
        for k in range(4):
            cx = w * (0.2 + 0.2 * k) + math.sin(self.t * (0.6 + k * 0.13)) * w * 0.08
            cy = h * (0.35 + 0.12 * k) + math.cos(self.t * (0.55 + k * 0.11)) * h * 0.07
            radius = min(w, h) * (0.25 + 0.04 * math.sin(self.t * (0.8 + k * 0.2)))

            rg = QRadialGradient(QPointF(cx, cy), radius)
            rg.setColorAt(0.0, QColor(80, 220, 255, 200))
            rg.setColorAt(0.5, QColor(190, 70, 255, 120))
            rg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(0, 0, w, h, rg)

        p.setCompositionMode(QPainter.CompositionMode_Overlay)
        p.setOpacity(0.16)
        pen = QPen(QColor(255, 255, 255, 140))
        pen.setWidthF(1.2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)

        for i in range(14):
            y = h * (i / 14.0)
            amp = 18 + 8 * math.sin(self.t * 0.9)
            freq = 0.012 + i * 0.00035
            phase = self.t * (0.9 + i * 0.03)

            path = QPainterPath()
            path.moveTo(0, y)
            step = 16
            for x in range(0, w + step, step):
                yy = y + math.sin(x * freq + phase) * amp
                path.lineTo(x, yy)
            p.drawPath(path)

        p.setOpacity(1.0)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)

    # ---- FACE FILL FOR INNER CUBE (w=-1) ----
    def inner_cube_face_indices(self):
        # Faces of the 3D cube defined by x=±1, y=±1, z=±1, restricted to w=-1
        faces = []
        for axis in ("x", "y", "z"):
            for sign in (-1, 1):
                idxs = []
                for i, v in enumerate(self.verts):
                    if v.w != -1:
                        continue
                    if getattr(v, axis) == sign:
                        idxs.append(i)
                # should be 4 vertices per face
                if len(idxs) == 4:
                    faces.append((axis, sign, idxs))
        return faces

    def order_face_vertices_ccw(self, idxs, pts2):
        # Sort by angle around centroid in screen space (stable for convex quads)
        cx = sum(pts2[i][0] for i in idxs) / 4.0
        cy = sum(pts2[i][1] for i in idxs) / 4.0

        def ang(i):
            x, y = pts2[i]
            return math.atan2(y - cy, x - cx)

        return sorted(idxs, key=ang)

    def paint_inner_faces(self, p: QPainter, pts2, pts3):
        face_defs = self.inner_cube_face_indices()

        # sort faces by average z (far -> near)
        faces = []
        for axis, sign, idxs in face_defs:
            avg_z = sum(pts3[i].z for i in idxs) / 4.0
            faces.append((avg_z, axis, sign, idxs))
        faces.sort(key=lambda t: t[0])

        # IMPORTANT: draw solids in normal mode so they don't vanish
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Make it clearly visible
        base_op = 0.38 + 0.10 * (0.5 + 0.5 * math.sin(self.t * 1.1))  # ~0.38..0.48

        # Optional subtle edge to separate faces
        outline = QPen(QColor(255, 255, 255, 55))
        outline.setWidthF(1.0)
        outline.setCapStyle(Qt.RoundCap)
        outline.setJoinStyle(Qt.RoundJoin)

        for _, axis, sign, idxs in faces:
            ordered = self.order_face_vertices_ccw(idxs, pts2)
            poly = QPolygonF([QPointF(pts2[i][0], pts2[i][1]) for i in ordered])

            # Build a direction for the gradient that "moves" with the face.
            # We'll use the two farthest points in screen space as gradient endpoints.
            pts = [(pts2[i][0], pts2[i][1]) for i in ordered]
            # pick endpoints by max distance (simple & effective)
            best = (0, 1, -1.0)
            for a in range(4):
                for b in range(a + 1, 4):
                    dx = pts[a][0] - pts[b][0]
                    dy = pts[a][1] - pts[b][1]
                    d2 = dx*dx + dy*dy
                    if d2 > best[2]:
                        best = (a, b, d2)
            (xA, yA) = pts[best[0]]
            (xB, yB) = pts[best[1]]

            # Stronger per-face color palette (you can tweak these)
            if axis == "x":
                c0 = QColor(0, 230, 255, 220)     # cyan
                c1 = QColor(160, 80, 255, 180)   # purple
            elif axis == "y":
                c0 = QColor(255, 90, 230, 210)   # magenta
                c1 = QColor(0, 200, 255, 170)    # cyan-blue
            else:  # z
                c0 = QColor(80, 220, 255, 210)
                c1 = QColor(255, 140, 255, 170)

            # flip depending on sign so opposite faces look different
            if sign == -1:
                c0, c1 = c1, c0

            # Add a little animated highlight shift along the gradient
            t = 0.5 + 0.5 * math.sin(self.t * 1.7 + (0 if sign == 1 else 1.2))
            g = QLinearGradient(xA, yA, xB, yB)
            g.setColorAt(0.0, c0)
            g.setColorAt(0.45, QColor(
                int(c0.red()   * (1 - t) + c1.red()   * t),
                int(c0.green() * (1 - t) + c1.green() * t),
                int(c0.blue()  * (1 - t) + c1.blue()  * t),
                230
            ))
            g.setColorAt(1.0, c1)

            p.setOpacity(base_op)
            p.setPen(outline)           # outline helps read the surface
            p.setBrush(QBrush(g))
            p.drawPolygon(poly)

        p.setOpacity(1.0)

    # ---- TESSERACT DRAW ----
    def paint_tesseract(self, p: QPainter, w: int, h: int):
        aspect = w / max(1, h)

        a = self.t * 0.9
        b = self.t * 0.7
        c = self.t * 0.6

        rotated4 = []
        for v in self.verts:
            r = v
            r = rotate4d(r, 0, 3, a)                 # x-w
            r = rotate4d(r, 1, 3, b)                 # y-w
            r = rotate4d(r, 2, 3, c)                 # z-w
            r = rotate4d(r, 0, 1, self.t * 0.35)     # x-y
            rotated4.append(r)

        # Project to 3D then 2D (keep both for depth sorting)
        pts3 = []
        pts2 = []
        for r in rotated4:
            p3 = project_4d_to_3d(r, w_dist=3.2)
            x2, y2 = project_3d_to_2d(p3, z_dist=5.0)

            x2 *= 0.55 / max(1e-6, aspect)
            y2 *= 0.55

            sx = w * 0.5 + x2 * w * 0.45
            sy = h * 0.5 + y2 * h * 0.45

            pts3.append(p3)
            pts2.append((sx, sy))

        pulse = 0.55 + 0.25 * math.sin(self.t * 1.6)

        # 1) draw inner cube surfaces FIRST (so lines sit on top)
        self.paint_inner_faces(p, pts2, pts3)

        # 2) Glow layer (colored per cube)
        p.setCompositionMode(QPainter.CompositionMode_Screen)
        for i, j in self.edges:
            x1, y1 = pts2[i]
            x2, y2 = pts2[j]
            kind = self.classify_edge(i, j)

            if kind == "wneg":
                c1 = QColor(0, 230, 255, 220)
                c2 = QColor(0, 140, 255, 170)
                width = 5.2
                op = 0.22 * pulse
            elif kind == "wpos":
                c1 = QColor(255, 80, 230, 220)
                c2 = QColor(150, 90, 255, 170)
                width = 5.2
                op = 0.22 * pulse
            else:
                c1 = QColor(230, 240, 255, 140)
                c2 = QColor(120, 200, 255, 120)
                width = 4.2
                op = 0.12 * pulse

            draw_edge_gradient(p, x1, y1, x2, y2, c1, c2, width, opacity=op)

        # 3) Core lines
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        for i, j in self.edges:
            x1, y1 = pts2[i]
            x2, y2 = pts2[j]
            kind = self.classify_edge(i, j)

            if kind == "wneg":
                c1 = QColor(180, 255, 255, 255)
                c2 = QColor(0, 210, 255, 255)
                width = 2.3
                op = 0.95
            elif kind == "wpos":
                c1 = QColor(255, 190, 255, 255)
                c2 = QColor(210, 120, 255, 255)
                width = 2.3
                op = 0.95
            else:
                c1 = QColor(245, 248, 255, 210)
                c2 = QColor(245, 248, 255, 210)
                width = 1.6
                op = 0.72

            draw_edge_gradient(p, x1, y1, x2, y2, c1, c2, width, opacity=op)

        p.setOpacity(1.0)

    def paintEvent(self, _):
        w, h = self.width(), self.height()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        self.paint_color_texture(p, w, h)
        self.paint_tesseract(p, w, h)

def main():
    app = QApplication(sys.argv)
    w = Teaser()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
