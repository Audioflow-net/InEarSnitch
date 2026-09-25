#!/bin/bash
SCAD="/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
OUT_DIR="/Users/ben/.gemini/antigravity/brain/31bf4b28-6899-4300-afe9-4ba5def05658/img"

MODES=("V27" "V29" "V30" "V31" "FLARE" "NUTLESS")
CAMERA="0,0,5,70,0,45,50"

for MODE in "${MODES[@]}"; do
    echo "Rendering $MODE with FULL CGAL..."
    $SCAD -o "$OUT_DIR/render_$MODE.png" \
          --render \
          --colorscheme="Tomorrow Night" \
          --imgsize=800,800 \
          --camera=$CAMERA \
          -D "run_mode=\"$MODE\"" \
          render_catalog.scad
done
echo "Done!"
