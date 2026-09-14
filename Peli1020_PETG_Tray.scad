// Peli 1020 - PETG Storage Tray & Transport Lock (Podest Edition)

$fn = 60;
eps = 0.05;

// -- Global Parameters (Matched to V30 Master) --
rim_x = 136.14;
rim_y = 91.69;
depth = 23.62;
center_shift = 1.65;

// -- Tray Design --
wall = 2.0;
z_bot = 23.62;
z_top = 41.5;

// Z-Levels for the Flat Floor & Podest
z_ubelly = 29.5; // 0.5mm Safety clearance for Tips (Z=29.0)         // Ceiling of main underbelly (touches tips perfectly)
z_floor = 31.5;  // Raised to maintain 2mm floor thickness          // Main storage floor (10.5mm deep storage!)

// Mic Head (Coupler) is exactly at Z=32.62. 
// We want to press it down by exactly 1.0mm.
z_podest_ubelly = 31.62; // 32.62 - 1.0mm (Ceiling presses into the Mic Head)
z_podest = 33.62;        // Floor of the Podest (2mm wall thickness)

h_total = z_top - z_bot;
h_floor = z_floor - z_bot;
h_ubelly = z_ubelly - z_bot;

// Dimensions at bottom
tray_x_bot = rim_x - 3.0;
tray_y_bot = rim_y - 3.0;
tray_r_bot = 9.3 - 1.5;

// Draft calculations (15 degrees to clear lid hinge)
draft_total = h_total * tan(15);
draft_floor = h_floor * tan(15);
draft_ubelly = h_ubelly * tan(15);

module rounded_rect(l, w, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(h=h, r=r);
        translate([l-r, r, 0]) cylinder(h=h, r=r);
        translate([l-r, w-r, 0]) cylinder(h=h, r=r);
        translate([r, w-r, 0]) cylinder(h=h, r=r);
    }
}

module coupler_tube(is_inner) {
    // V173: Kopf und Schaft getrennt modelliert, um den Stauraum zu maximieren!
    // Der dicke Kopf (d=25) braucht Platz, aber der dünne Schaft (d=14) liegt tief unten
    // und erzeugt nun keine unnötige Beule mehr im Boden des Trays.
    
    z = 19.12; // Perfect Z-center for the 1mm press-fit
    
    // The Head
    head_d = is_inner ? 25.0 : 29.0;
    head_x = is_inner ? 87.65 : 85.65;
    head_l = is_inner ? 28.5 : 32.5;
    
    // The Stem
    stem_d = is_inner ? 14.0 : 18.0;
    stem_x = 8.0;
    stem_l = head_x - stem_x + eps;
    
    translate([0, 67.65, z]) rotate([0, 90, 0]) {
        // Head
        translate([0, 0, head_x]) cylinder(h=head_l, d=head_d);
        // Stem
        translate([0, 0, stem_x]) cylinder(h=stem_l, d=stem_d);
    }
}

// ==========================================
// CIEM CLEANING STATION - SOFT NOTCHES
// ==========================================
module soft_notch(x_pos) {
    w = 8.0; 
    r = w / 2;
    // Die Rinne in der TPU-Matte endet bei Z=3.0 über dem Boden. 
    // z_floor = 31.5 -> Boden der Rinne liegt bei 34.5.
    z_center = 34.5 + r; 
    
    translate([x_pos, 0, 0]) hull() {
        // Innerer Trichter (weit aufgeweitet für weichen Kabel-Einlauf)
        translate([0, 10, z_center + 2]) sphere(r=r + 2, $fn=30);
        translate([0, 10, z_top + 10]) sphere(r=r + 2, $fn=30);
        
        // Engste Stelle direkt in der PETG-Wand (Y=3.5)
        translate([0, 3.5, z_center]) sphere(r=r, $fn=30);
        translate([0, 3.5, z_top + 10]) sphere(r=r, $fn=30);
        
        // Äußerer Trichter (weit aufgeweitet für weichen Kabel-Auslauf)
        translate([0, -2, z_center + 2]) sphere(r=r + 2, $fn=30);
        translate([0, -2, z_top + 10]) sphere(r=r + 2, $fn=30);
    }
}

module petg_tray() {
    union() {
        difference() {
            // 1. MAIN OUTER SHELL
            hull() {
                translate([1.5, 1.5, z_bot])
                    rounded_rect(tray_x_bot, tray_y_bot, eps, tray_r_bot);
                translate([1.5 + draft_total, 1.5 + draft_total, z_top])
                    rounded_rect(tray_x_bot - 2*draft_total, tray_y_bot - 2*draft_total, eps, tray_r_bot - draft_total);
            }
            
            // 2. STORAGE CAVITY (Top side)
            difference() {
                // Main flat bucket (Down to Z=31.0)
                hull() {
                    translate([1.5 + draft_floor + wall, 1.5 + draft_floor + wall, z_floor])
                        rounded_rect(tray_x_bot - 2*draft_floor - 2*wall, tray_y_bot - 2*draft_floor - 2*wall, eps, tray_r_bot - draft_floor - wall);
                    translate([1.5 + draft_total + wall, 1.5 + draft_total + wall, z_top + eps])
                        rounded_rect(tray_x_bot - 2*draft_total - 2*wall, tray_y_bot - 2*draft_total - 2*wall, eps, tray_r_bot - draft_total - wall);
                }
                
                // Keep the Outer Tube solid by subtracting it from the cavity!
                coupler_tube(is_inner=false);
            }
            
            // 3. UNDERBELLY CAVITY (Bottom side)
            union() {
                // Main Underbelly (Up to Z=29.0)
                hull() {
                    translate([1.5 + wall, 1.5 + wall, z_bot - eps])
                        rounded_rect(tray_x_bot - 2*wall, tray_y_bot - 2*wall, eps, tray_r_bot - wall);
                    translate([1.5 + draft_ubelly + wall, 1.5 + draft_ubelly + wall, z_ubelly])
                        rounded_rect(tray_x_bot - 2*draft_ubelly - 2*wall, tray_y_bot - 2*draft_ubelly - 2*wall, eps, tray_r_bot - draft_ubelly - wall);
                }
                
                // Exact 3D imprint of the Mic Head!
                // Forms a perfect arched ceiling that cups the microphone.
                coupler_tube(is_inner=true);
            }
            
            // 4. TOWER CUTOUT
            translate([109.65, 41.65, z_bot - eps])
                cylinder(h=50, d=23.0);
                
            // 5. CABLE ROUTING NOTCHES (Butterweiche Kabelausgänge)
            soft_notch(26);
            soft_notch(59);
        }
        
        // 6. PARTITION WALL (Trennbereich für CIEMs)
        // Separiert die 75x80 CIEM-Wanne physisch von der rechten Mikrofon-Seite.
        intersection() {
            translate([81.0, 0, z_floor]) cube([2.0, 100, 10]);
            // Intersect with the main outer shell to perfectly match the drafted walls
            hull() {
                translate([1.5, 1.5, z_bot])
                    rounded_rect(tray_x_bot, tray_y_bot, eps, tray_r_bot);
                translate([1.5 + draft_total, 1.5 + draft_total, z_top])
                    rounded_rect(tray_x_bot - 2*draft_total, tray_y_bot - 2*draft_total, eps, tray_r_bot - draft_total);
            }
        }
    }
}

// V184: Massiver TPU Boden mit extrem starken Klemm-Wänden & 2-Teile PETG System
module tpu_tray_mat() {
    mat_thickness = 1.5;  
    wall_thickness = 1.2; 
    wall_h = 8.5;         
    
    // Die perfekte, kontinuierliche 2D-Wand (ohne Lücken!)
    module tpu_wall_2d() {
        
        // 1. Grundform einer einzelnen Kammer (inkl. Überlappungs-Nase)
        module pod_shape(is_left) {
            hull() {
                translate([0, 50]) circle(d=34, $fn=60);
                translate([0, 30]) circle(d=34, $fn=60);
                translate([0, 10]) circle(d=16, $fn=60);
                
                if (is_left) {
                    translate([10, 40]) circle(d=22, $fn=60);
                } else {
                    translate([-10, 40]) circle(d=22, $fn=60);
                }
            }
        }
        
        // 2. Einzelne Kammer aushöhlen (absolut crash-frei für CGAL!)
        module hollow_pod(is_left) {
            difference() {
                pod_shape(is_left);
                offset(r = -wall_thickness) pod_shape(is_left);
            }
        }
        
        // 3. Ausgehöhlte Kammern vereinen und die Leaf-Spring Glättung einfügen!
        // offset(0.5) verschmilzt die Wände sanft miteinander.
        offset(r=0.5) offset(r=-0.5) {
            union() {
                translate([28, 0]) hollow_pod(true);
                translate([59, 0]) hollow_pod(false);
                
                // DAS GEHEIMNIS DER BLATTFEDER (Leaf Spring):
                // Anstatt komplizierter Offset-Ketten, die CGAL zum Absturz bringen,
                // füllen wir die scharfen V-Kerben im Inneren der Überkreuzung 
                // einfach direkt mit runden TPU-Tropfen auf! 
                // Dies eliminiert die Sollbruchstelle und erzeugt eine weiche U-Kurve.
                translate([43.5, 47]) circle(d=6, $fn=30);
                translate([43.5, 33]) circle(d=6, $fn=30);
            }
        }
    }
    
    // 1. DER MASSIVE BODEN (Keine Lücken mehr im Boden!)
    intersection() {
        translate([1.5 + draft_floor + wall, 1.5 + draft_floor + wall, 0])
            rounded_rect(tray_x_bot - 2*draft_floor - 2*wall, tray_y_bot - 2*draft_floor - 2*wall, mat_thickness, tray_r_bot - draft_floor - wall);
        cube([80.0, 100.0, mat_thickness + eps]);
    }
    
    // 2. DIE WAND
    difference() {
        translate([0, 0, mat_thickness - eps]) 
            linear_extrude(height = wall_h + eps) 
                tpu_wall_2d();
        
        // Trichter links öffnen (Kabelausgang)
        translate([28, 0, 0]) translate([-7, -5, -eps]) cube([14, 25, 20]);
        // Trichter rechts öffnen
        translate([59, 0, 0]) translate([-7, -5, -eps]) cube([14, 25, 20]);
        
        // 3. SOLLBRUCHSTELLE (Tear-Away Schnitt für lose Innenwände)
        // Wie von dir genial vorgeschlagen: Wir schneiden einen 0.4mm Spalt 
        // exakt zwischen dem Boden und der eingewölbten Innenwand!
        // Der Drucker druckt diese Schicht in die Luft, sie droopt minimal an,
        // und nach dem Druck kannst du die Wand einfach mit dem Finger abreißen. 
        // Ab dann ist die gesamte zentrale Blattfeder komplett LOSE und federt frei!
        translate([43.5, 40, mat_thickness + 0.2]) 
            cube([28, 45, 0.4], center=true);
    }
}

// ==========================================
// SNAP-FIT 2-TEILE SYSTEM (V187)
// ==========================================

// Ein exakter Block, der genau der geschrägten Innenwand der Storage Cavity entspricht.
// Wir nutzen ihn, um den Boden aus dem Rahmen zu schneiden und die Platte zu formen!
module dropin_cutout_block(tol=0) {
    // BUGFIX: Um "CGAL Coplanar Face" Rendering-Fehler (unsichtbare Platte) zu verhindern,
    // lassen wir den Block 1mm tiefer anfangen (28.5 statt 29.5).
    // Da das PETG-Tray unten eh schon bis 29.5 hohl ist, schneiden wir nur in leere Luft,
    // aber wir zwingen OpenSCAD zu sauberer Geometrie-Mathematik!
    z_start = 28.5;
    h_start = z_start - z_bot;
    d_start = h_start * tan(15);
    
    h_50 = 50.0 - z_bot;
    d_50 = h_50 * tan(15);
    
    hull() {
        translate([1.5 + d_start + wall + tol, 1.5 + d_start + wall + tol, z_start])
            rounded_rect(tray_x_bot - 2*d_start - 2*wall - 2*tol, tray_y_bot - 2*d_start - 2*wall - 2*tol, eps, tray_r_bot - d_start - wall);
            
        translate([1.5 + d_50 + wall + tol, 1.5 + d_50 + wall + tol, 50])
            rounded_rect(tray_x_bot - 2*d_50 - 2*wall - 2*tol, tray_y_bot - 2*d_50 - 2*wall - 2*tol, eps, tray_r_bot - d_50 - wall);
    }
}

module petg_outer_frame() {
    difference() {
        petg_tray();
        // BUGFIX: tol=-0.1 macht den Block minimal breiter.
        // Das garantiert, dass er beim Abziehen sauber IN die Wand schneidet
        // und OpenSCAD keine "Invalid 2-Manifold" Kanten stehen lässt!
        dropin_cutout_block(tol=-0.1);
    }
    
    // Snap-Fit Punkte: Wir müssen die 15 Grad Schräge (Draft) exakt berechnen!
    bump_z = 32.2;
    h_bump = bump_z - z_bot;
    draft_bump = h_bump * tan(15); // ca. 2.30mm Offset durch die Schräge
    
    inner_left_x  = 1.5 + draft_bump + wall;
    inner_right_x = 1.5 + tray_x_bot - draft_bump - wall;
    inner_back_y  = 1.5 + tray_y_bot - draft_bump - wall;
    
    module snap_bump() {
        sphere(d=1.2, $fn=20); // 1.2mm d, ragt exakt 0.6mm in den Rahmen (perfekter Snap)
    }
    color("Gold") {
        translate([inner_left_x, 30, bump_z]) snap_bump();
        translate([inner_left_x, 60, bump_z]) snap_bump();
        translate([inner_right_x, 30, bump_z]) snap_bump();
        translate([inner_right_x, 60, bump_z]) snap_bump();
        translate([40, inner_back_y, bump_z]) snap_bump();
        translate([90, inner_back_y, bump_z]) snap_bump();
    }
}

// BUGFIX V189: Platte nativ bauen (ohne intersection!), da CGAL sonst abstürzt!
module petg_dropin_plate() {
    tol = 0.15; // Toleranz für sauberes Einklicken
    
    difference() {
        union() {
            // 1. Die flache 2mm Bodenplatte exakt an den 15 Grad Wänden hochziehen
            h_295 = 29.5 - z_bot;
            d_295 = h_295 * tan(15);
            h_315 = 31.5 - z_bot;
            d_315 = h_315 * tan(15);
            
            hull() {
                translate([1.5 + d_295 + wall + tol, 1.5 + d_295 + wall + tol, 29.5])
                    rounded_rect(tray_x_bot - 2*d_295 - 2*wall - 2*tol, tray_y_bot - 2*d_295 - 2*wall - 2*tol, eps, tray_r_bot - d_295 - wall);
                translate([1.5 + d_315 + wall + tol, 1.5 + d_315 + wall + tol, 31.5])
                    rounded_rect(tray_x_bot - 2*d_315 - 2*wall - 2*tol, tray_y_bot - 2*d_315 - 2*wall - 2*tol, eps, tray_r_bot - d_315 - wall);
            }
            
            // 2. Die Trennwand
            translate([81.0, 1.5 + d_315 + wall + tol, 31.5]) 
                cube([2.0, tray_y_bot - 2*d_315 - 2*wall - 2*tol, 10.0]);
                
            // 3. Mic Coupler Tube (Outer)
            coupler_tube(is_inner=false);
        }
        
        // Mic Coupler aushöhlen (damit das Mikrofon perfekt hineinpasst!)
        coupler_tube(is_inner=true);
        
        // Unterseite radikal abschneiden, damit die Platte zu 100% plan bei Z=29.5 beginnt
        translate([-50, -50, 0]) cube([300, 300, 29.5]);
    }
}

// ==========================================
// RENDER STEUERUNG (V185)
// ==========================================
render_mode = "exploded"; 

if (render_mode == "exploded") {
    // Zeigt alle Teile auseinandergebaut!
    color("DimGray") petg_outer_frame();
    translate([0, 0, 30]) color("Silver") petg_dropin_plate();
    translate([0, 0, 60]) color("DeepSkyBlue") tpu_tray_mat();
} else if (render_mode == "assembly") {
    color("DimGray") petg_outer_frame();
    color("Silver") petg_dropin_plate();
    color("DeepSkyBlue") translate([0, 0, z_floor]) tpu_tray_mat();
} else if (render_mode == "print_frame") {
    // Schiebt den Rahmen auf Z=0 (Druckbett)
    translate([0, 0, -z_bot]) color("DimGray") petg_outer_frame();
} else if (render_mode == "print_plate") {
    // Liegt flach auf dem Boden für den Druck
    translate([0, 0, -29.5]) color("Silver") petg_dropin_plate();
} else if (render_mode == "print_mat") {
    color("DeepSkyBlue") tpu_tray_mat();
}
