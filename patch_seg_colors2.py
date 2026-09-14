import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        def create_seg_btn\(text, pos\):
            btn = QPushButton\(text\)
            btn\.setCheckable\(True\)
            # Base style
            rad = "4px"
            bl = rad if pos in \("left", "only"\) else "0px"
            tl = rad if pos in \("left", "only"\) else "0px"
            br = rad if pos in \("right", "only"\) else "0px"
            tr = rad if pos in \("right", "only"\) else "0px"
            b_right = "0px" if pos == "left" or pos == "middle" else "1px solid #555"
            
            btn\.setStyleSheet\(f\'\'\'
                QPushButton \{\{
                    background-color: #222;
                    color: #AAA;
                    border: 1px solid #555;
                    border-right: \{b_right\};
                    border-top-left-radius: \{tl\};
                    border-bottom-left-radius: \{bl\};
                    border-top-right-radius: \{tr\};
                    border-bottom-right-radius: \{br\};
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 13px;
                \}\}
                QPushButton:checked \{\{
                    background-color: #444;
                    color: white;
                    border-color: #666;
                \}\}
                QPushButton:hover:!checked \{\{
                    background-color: #333;
                \}\}
            \'\'\'\)'''

replacement = r'''        def create_seg_btn(text, pos, checked_bg="#444"):
            btn = QPushButton(text)
            btn.setCheckable(True)
            # Base style
            rad = "4px"
            bl = rad if pos in ("left", "only") else "0px"
            tl = rad if pos in ("left", "only") else "0px"
            br = rad if pos in ("right", "only") else "0px"
            tr = rad if pos in ("right", "only") else "0px"
            b_right = "0px" if pos == "left" or pos == "middle" else "1px solid #555"
            
            btn.setStyleSheet(f\'\'\'
                QPushButton {{
                    background-color: #222;
                    color: #AAA;
                    border: 1px solid #555;
                    border-right: {b_right};
                    border-top-left-radius: {tl};
                    border-bottom-left-radius: {bl};
                    border-top-right-radius: {tr};
                    border-bottom-right-radius: {br};
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:checked {{
                    background-color: {checked_bg};
                    color: white;
                    border-color: #666;
                }}
                QPushButton:hover:!checked {{
                    background-color: #333;
                }}
            \'\'\')'''

code = re.sub(pattern, replacement, code)

# Now update the calls!
code = code.replace(
    'btn_l = create_seg_btn("Left", "left")',
    'btn_l = create_seg_btn("Left", "left", checked_bg="#16a34a")'
)

code = code.replace(
    'btn_r = create_seg_btn("Right", "right")',
    'btn_r = create_seg_btn("Right", "right", checked_bg="#dc2626")'
)

with open("main.py", "w") as f:
    f.write(code)

print("Segmented button colors patched via regex.")
