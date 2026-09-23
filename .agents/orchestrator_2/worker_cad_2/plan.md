# Worker CAD 2 Plan — Iteration 2 Mechanical Refinement
1. Fix press_v2_wedge.scad:
   - Genuine internal tapered collet sleeve pocket (~7.0° taper) that actively compresses mold halves laterally
   - Remove/fix uncentered cube blowout so sleeve is a single clean manifold body
   - Enlarge pad recess to 3.2mm for 3.0mm tamper lid and eliminate 4.26mm collision with wedge
   - Reorient wedge in mode="print_plate" so it rests flat on Z=0
2. Fix press_v2_cam.scad:
   - Re-engineer vertical stack height: pin at proper Z, plunger thickness + cam lobe profile match travel
   - Tangential rolling cam profile without plunger collision (0.0mm intersection)
   - Proper lever rotation: upright at open (0°), closing to 92° horizontal detent
   - Constrain lateral pin play and ensure pivot pin rests flat on bed in print plate mode
3. Fix press_v2_bayonet.scad:
   - Fix collar outer diameter (e.g. 58mm) vs bore (53.5mm) so skirt has robust manifold walls
   - Lower 14° conical collet so it directly engages and clamps the mold block shoulders
   - Re-align lugs and ramps so collar thrust shoulder drives floating plate firmly onto tamper lid
   - Add 45° printability chamfers under base lugs
4. Enhance verify_press_v2.py:
   - Add CGAL manifoldness checks (assert single manifold volume, no Volumes > 1)
   - Add intersection collision checks (confirm 0.0mm intersection volume between mating parts)
5. Update CHANGELOG.md Work Paper with V36 refinement details.
