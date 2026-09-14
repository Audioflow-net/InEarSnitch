import re

with open("metrology_lab.py", "r") as f:
    content = f.read()

# Ersetze die Standard shaft height
old_shaft = """            y_base = cy + 15*sc
            shaft_h = 20*sc
            y_shaft_top = y_base - 5*sc - shaft_h"""

new_shaft = """            y_base = cy + 15*sc
            shaft_h = self.get_val("cone_length_mm", 20.0) * sc
            y_shaft_top = y_base - 5*sc - shaft_h"""

content = content.replace(old_shaft, new_shaft)

# Ersetze das Cone Zeichnen
old_cone = """            # 2. Main Shaft or Cone
            if cone > 0:
                top_w = out_d * 0.3 # Visual representation of a cone tip
                poly = QPolygonF([
                    QPointF(cx - out_d/2, y_base - 5*sc),
                    QPointF(cx + out_d/2, y_base - 5*sc),
                    QPointF(cx + top_w/2, y_shaft_top),
                    QPointF(cx - top_w/2, y_shaft_top)
                ])
                qp.drawPolygon(poly)
                self.draw_dim(qp, cx + out_d/2 + 15, y_shaft_top + shaft_h/2, cx + out_d/2 + 25, y_shaft_top + shaft_h/2, "cone_angle_deg")
            else:
                qp.drawRect(int(cx - out_d/2), int(y_shaft_top), int(out_d), int(shaft_h))"""

new_cone = """            # 2. Main Shaft or Cone
            has_tip = "tip_outer_mm" in self.data
            if cone > 0 or has_tip:
                top_w = (self.get_val("tip_outer_mm", 4.0) * sc) if has_tip else (out_d * 0.3)
                poly = QPolygonF([
                    QPointF(cx - out_d/2, y_base - 5*sc),
                    QPointF(cx + out_d/2, y_base - 5*sc),
                    QPointF(cx + top_w/2, y_shaft_top),
                    QPointF(cx - top_w/2, y_shaft_top)
                ])
                qp.drawPolygon(poly)
                if has_tip:
                    self.draw_dim(qp, cx - top_w/2, y_shaft_top - 15, cx + top_w/2, y_shaft_top - 15, "tip_outer_mm")
                    self.draw_dim(qp, cx + out_d/2 + 25, y_shaft_top + shaft_h/2, cx + out_d/2 + 25, y_shaft_top + shaft_h/2, "cone_length_mm")
                else:
                    self.draw_dim(qp, cx + out_d/2 + 15, y_shaft_top + shaft_h/2, cx + out_d/2 + 25, y_shaft_top + shaft_h/2, "cone_angle_deg")
            else:
                qp.drawRect(int(cx - out_d/2), int(y_shaft_top), int(out_d), int(shaft_h))"""

content = content.replace(old_cone, new_cone)

with open("metrology_lab.py", "w") as f:
    f.write(content)

print("done")
