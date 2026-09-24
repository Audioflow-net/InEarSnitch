// Peli Case 1020 TPU Insert - V31
// Push-to-Eject Seesaw Mechanism for IEC711 Coupler
// Push-to-Eject Seesaw Mechanism for IEC711 Coupler
// 3-HORIZONTAL-BAND LAYOUT (Max Cable, 6 Tips, No IEM Pocket)

$fn = 60;
eps = 0.05;

// ==========================================
// RENDER STEUERUNG (DRUCK & ANSICHT)
// ==========================================
// Stelle auf "true", um die einzelnen Teile zu rendern
show_tpu_main = false;
show_petg_chassis = true;
show_tpu_sleeve = true;
show_dummy_mic = false;
show_cross_section = false;
show_test_print = false; // TEST-DRUCK FÜR DIE LASCHE

// --- 1. Design Parameters ---
// Peli 1020 Internal Dimensions (Drafted)
// MASSIVE BREAKTHROUGH: 132.84 x 88.39 are the BOTTOM floor dimensions!
base_x = 132.84;
base_y = 88.39;
depth = 23.62;

// Der Draft-Winkel ist 4 Grad (laut PDF).
// Versatz pro Seite = tan(4) * 23.62 = 1.65 mm. 
// Gesamter Längenzuwachs oben = 3.3 mm!
rim_x = base_x + 3.30; // 136.14
rim_y = base_y + 3.30; // 91.69

base_dx = (rim_x - base_x) / 2; // 1.65

// Corner Radii (PDF sagt Outer Radius = 12.3)
// Da der Flansch 3.0mm breit ist, ist der innere Rim-Radius 12.3 - 3.0 = 9.3mm.
fillet_r = 9.3;
base_r = fillet_r - base_dx; // 7.65

// Flange (Retention Collar) and Sealing Lip
flange_w = 3.0; // Auf 3mm reduziert (Nutzer-Schnitt-Test) // 136.14 + 6 = 142.14 (Exakt das Außenmaß aus dem PDF!)
flange_t = 1.5; 
lip_h = 2.0;    
lip_w = 1.5;    
lip_offset = 1.0; // Mittig auf dem 3.0mm Flansch positioniert

// Internal components center shift
center_shift = 1.65;

// Coupler Assembly (Angepasst auf reale Maße von User!)
head_od = 24.0;
head_len = 27.0;
stem_od = 14.0;
stem_len = 78.0; // 105 - 27
adapter_tip_od = 14.0;
adapter_tip_len = 18.0;
total_len = stem_len + head_len + adapter_tip_len; // 123.0 mm

// Bottom Band: Tip Holders (6x in a row)
tip_bore_d = 20.5;
tip_bore_depth = 8.0;
tip_y = 15.0; // Leicht nach unten gerückt für mehr Sicherheitsabstand zur Wanne
tip_xs = [15.65, 36.65, 57.65, 78.65, 99.65, 120.65];

// Middle Band: Cable Trench
cable_well_depth = 20.0;

// --- 2. Base Shape Module ---
module rounded_rect(l, w, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(h=h, r=r);
        translate([l-r, r, 0]) cylinder(h=h, r=r);
        translate([l-r, w-r, 0]) cylinder(h=h, r=r);
        translate([r, w-r, 0]) cylinder(h=h, r=r);
    }
}

module peli_body() {
    union() {
        // 1. MAIN BODY (Drafted shape inside the case)
        hull() {
            translate([base_dx, base_dx, 0])
                rounded_rect(base_x, base_y, eps, base_r);
            translate([0, 0, depth])
                rounded_rect(rim_x, rim_y, eps, fillet_r);
        }
        
        // 2. FLANSCH UND EINHAK-LIPPE (U-Channel über den Kistenrand)
        // Nach exaktem PDF-Querschnitt: Der Flansch geht flach nach außen und hat
        // an der äußersten Kante eine nach UNTEN zeigende Lippe, die über den Plastikrand greift.
        translate([-flange_w, -flange_w, depth]) {
            // Flacher Flansch (oben, 1.5mm dick)
            rounded_rect(rim_x + 2*flange_w, rim_y + 2*flange_w, flange_t, fillet_r + flange_w);
            
            // EINZEL-LIPPE (Nach Nutzer-Schnitt-Test)
            // 3.0mm Flanschbreite. Eine einzelne, robuste 1.0mm dicke Lippe am ganz äußeren Rand.
            translate([0, 0, -3.0]) {
                difference() {
                    rounded_rect(rim_x + 2*flange_w, rim_y + 2*flange_w, 3.0, fillet_r + flange_w);
                    translate([1.0, 1.0, -eps])
                        rounded_rect(rim_x + 2*flange_w - 2.0, rim_y + 2*flange_w - 2.0, 3.0 + 2*eps, fillet_r + flange_w - 1.0);
                }
            }
        }
        

    }
}

// --- 3. Internal Cutouts Module ---
// Hilfs-Modul für support-freien 3D-Druck (45 Grad Schräge)
module wedge_tab(w, o) {
    // WEDGE TAB MIT RUNDEN SEITEN (Finger-Safe!)
    // r = 2.0 mm Kantenradius an den Seiten der Balkone
    r = 2.0;
    translate([-w/2 + r, 0, 0])
    hull() {
        // Wand-Anker (Zylinder sorgen für weiche, abgerundete Seitenkanten)
        translate([0, -eps, -o - 1.0]) cylinder(h=o + 1.0, r=r, $fn=30);
        translate([w - 2*r, -eps, -o - 1.0]) cylinder(h=o + 1.0, r=r, $fn=30);
        
        // Spitze des Balkons
        translate([0, o - r, -1.0]) cylinder(h=1.0, r=r, $fn=30);
        translate([w - 2*r, o - r, -1.0]) cylinder(h=1.0, r=r, $fn=30);
    }
}

// Hilfs-Modul für weiche 3D-Boden-Rundungen (Bathtub-Fillet)
module straight_pocket(l, w, h, r, roof_chamfer=0) {
    if (roof_chamfer > 0) {
        union() {
            hull() {
                translate([r, r, 0]) cylinder(h=h-roof_chamfer, r=r, $fn=30);
                translate([l-r, r, 0]) cylinder(h=h-roof_chamfer, r=r, $fn=30);
                translate([l-r, w-r, 0]) cylinder(h=h-roof_chamfer, r=r, $fn=30);
                translate([r, w-r, 0]) cylinder(h=h-roof_chamfer, r=r, $fn=30);
            }
            hull() {
                translate([r, r, h-roof_chamfer]) cylinder(h=eps, r=r, $fn=30);
                translate([l-r, r, h-roof_chamfer]) cylinder(h=eps, r=r, $fn=30);
                translate([l-r, w-r, h-roof_chamfer]) cylinder(h=eps, r=r, $fn=30);
                translate([r, w-r, h-roof_chamfer]) cylinder(h=eps, r=r, $fn=30);
                
                translate([r, r, h]) cylinder(h=eps, r=r-roof_chamfer, $fn=30);
                translate([l-r, r, h]) cylinder(h=eps, r=r-roof_chamfer, $fn=30);
                translate([l-r, w-r, h]) cylinder(h=eps, r=r-roof_chamfer, $fn=30);
                translate([r, w-r, h]) cylinder(h=eps, r=r-roof_chamfer, $fn=30);
            }
        }
    } else {
        hull() {
            translate([r, r, 0]) cylinder(h=h, r=r, $fn=30);
            translate([l-r, r, 0]) cylinder(h=h, r=r, $fn=30);
            translate([l-r, w-r, 0]) cylinder(h=h, r=r, $fn=30);
            translate([r, w-r, 0]) cylinder(h=h, r=r, $fn=30);
        }
    }
}

module rounded_pocket(l, w, h, r, br, chamfer=2.0) {
    // Inklusive 2.0mm Fase (Chamfer) an der Oberkante, damit KEINE harten 90-Grad Ecken bleiben!
    hull() {
        // Boden-Kugeln
        translate([r, r, br]) sphere(r=br, $fn=30);
        translate([l-r, r, br]) sphere(r=br, $fn=30);
        translate([l-r, w-r, br]) sphere(r=br, $fn=30);
        translate([r, w-r, br]) sphere(r=br, $fn=30);
        
        // Senkrechte Wände bis zum Start der Fase
        translate([r, r, br]) cylinder(h=h-br-chamfer, r=r, $fn=30);
        translate([l-r, r, br]) cylinder(h=h-br-chamfer, r=r, $fn=30);
        translate([l-r, w-r, br]) cylinder(h=h-br-chamfer, r=r, $fn=30);
        translate([r, w-r, br]) cylinder(h=h-br-chamfer, r=r, $fn=30);
    }
    
    // Die weiche Fase (Chamfer) an der Oberfläche
    hull() {
        translate([r, r, h-chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([l-r, r, h-chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([l-r, w-r, h-chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([r, w-r, h-chamfer]) cylinder(h=eps, r=r, $fn=30);
        
        // Oben 2mm breiter -> erzeugt einen 45-Grad Trichter als softe Kante
        translate([r, r, h]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([l-r, r, h]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([l-r, w-r, h]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([r, w-r, h]) cylinder(h=eps, r=r+chamfer, $fn=30);
    }
}

module ramp_pocket(l, w, h_top, z_deep, z_shallow, r, br, chamfer=2.0) {
    // Ein Pocket, dessen Boden von z_deep (links) auf z_shallow (rechts) ansteigt (Rampe).
    hull() {
        // Bottom-Left (Deep)
        translate([r, r, z_deep + br]) sphere(r=br, $fn=30);
        translate([r, w-r, z_deep + br]) sphere(r=br, $fn=30);
        
        // Bottom-Right (Shallow)
        translate([l-r, r, z_shallow + br]) sphere(r=br, $fn=30);
        translate([l-r, w-r, z_shallow + br]) sphere(r=br, $fn=30);
        
        // Vertical walls up to start of chamfer
        translate([r, r, z_deep + br]) cylinder(h=h_top - chamfer - (z_deep + br), r=r, $fn=30);
        translate([r, w-r, z_deep + br]) cylinder(h=h_top - chamfer - (z_deep + br), r=r, $fn=30);
        
        // Right side cylinders (shorter because floor is higher)
        translate([l-r, r, z_shallow + br]) cylinder(h=h_top - chamfer - (z_shallow + br), r=r, $fn=30);
        translate([l-r, w-r, z_shallow + br]) cylinder(h=h_top - chamfer - (z_shallow + br), r=r, $fn=30);
    }
    
    // The Top Chamfer
    hull() {
        // Inner rim (at h_top - chamfer)
        translate([r, r, h_top - chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([l-r, r, h_top - chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([r, w-r, h_top - chamfer]) cylinder(h=eps, r=r, $fn=30);
        translate([l-r, w-r, h_top - chamfer]) cylinder(h=eps, r=r, $fn=30);
        
        // Outer rim (at h_top)
        translate([r, r, h_top]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([l-r, r, h_top]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([r, w-r, h_top]) cylinder(h=eps, r=r+chamfer, $fn=30);
        translate([l-r, w-r, h_top]) cylinder(h=eps, r=r+chamfer, $fn=30);
    }
}



// Hilfsmodule für flexible, abgerundete Halte-Lippen (Pill-Shape)
// V163: Konkave Rundung (Viertelkreis) unter der Lippe für maximalen Platz und Support-freien Druck!
module pill_x_left(x, y, z, length, cr, p, h) {
    translate([x, y, z])
        hull() {
            cube([eps, length, h]);
            translate([p - cr, cr, 0]) cylinder(h=h, r=cr, $fn=20);
            translate([p - cr, length - cr, 0]) cylinder(h=h, r=cr, $fn=20);
        }
}
module pill_x_right(x, y, z, length, cr, p, h) {
    translate([x, y, z])
        hull() {
            translate([-eps, 0, 0]) cube([eps, length, h]);
            translate([-(p - cr), cr, 0]) cylinder(h=h, r=cr, $fn=20);
            translate([-(p - cr), length - cr, 0]) cylinder(h=h, r=cr, $fn=20);
        }
}
module retaining_lip_x(x, y, z, on_left, length, protrusion, thickness) {
    cr = min(3.0, length/2);
    support_h = protrusion;
    steps = 8;
    
    // Die flache Lippe oben
    if (on_left) pill_x_left(x, y, z - thickness, length, cr, protrusion, thickness);
    else pill_x_right(x, y, z - thickness, length, cr, protrusion, thickness);
        
    // Die konkave Stütze darunter
    for (i = [0 : steps - 1]) {
        t1 = i / steps;
        t2 = (i + 1) / steps;
        p1 = protrusion * (1 - sqrt(1 - t1*t1));
        p2 = protrusion * (1 - sqrt(1 - t2*t2));
        z1 = (z - thickness) - support_h * (1 - t1);
        z2 = (z - thickness) - support_h * (1 - t2);
        
        hull() {
            if (on_left) {
                pill_x_left(x, y, z1, length, cr, p1, eps);
                pill_x_left(x, y, z2, length, cr, p2, eps);
            } else {
                pill_x_right(x, y, z1, length, cr, p1, eps);
                pill_x_right(x, y, z2, length, cr, p2, eps);
            }
        }
    }
}

module pill_y_front(x, y, z, length, cr, p, h) {
    translate([x, y, z])
        hull() {
            cube([length, eps, h]);
            translate([cr, p - cr, 0]) cylinder(h=h, r=cr, $fn=20);
            translate([length - cr, p - cr, 0]) cylinder(h=h, r=cr, $fn=20);
        }
}
module pill_y_back(x, y, z, length, cr, p, h) {
    translate([x, y, z])
        hull() {
            translate([0, -eps, 0]) cube([length, eps, h]);
            translate([cr, -(p - cr), 0]) cylinder(h=h, r=cr, $fn=20);
            translate([length - cr, -(p - cr), 0]) cylinder(h=h, r=cr, $fn=20);
        }
}
module retaining_lip_y(x, y, z, on_front, length, protrusion, thickness) {
    cr = min(3.0, length/2);
    support_h = protrusion;
    steps = 8;
    
    if (on_front) pill_y_front(x, y, z - thickness, length, cr, protrusion, thickness);
    else pill_y_back(x, y, z - thickness, length, cr, protrusion, thickness);
        
    for (i = [0 : steps - 1]) {
        t1 = i / steps;
        t2 = (i + 1) / steps;
        p1 = protrusion * (1 - sqrt(1 - t1*t1));
        p2 = protrusion * (1 - sqrt(1 - t2*t2));
        z1 = (z - thickness) - support_h * (1 - t1);
        z2 = (z - thickness) - support_h * (1 - t2);
        
        hull() {
            if (on_front) {
                pill_y_front(x, y, z1, length, cr, p1, eps);
                pill_y_front(x, y, z2, length, cr, p2, eps);
            } else {
                pill_y_back(x, y, z1, length, cr, p1, eps);
                pill_y_back(x, y, z2, length, cr, p2, eps);
            }
        }
    }
}


// ==========================================
// DEIN INDIVIDUELLES LOGO (Option "Base-Through")
// ==========================================
module custom_logo_2d() {
    // Das zentrierte und skalierte Spy-Logo!
    translate([-11.05, -7.28]) 
        scale([0.0645, 0.0645]) 
            import("Final_Logo_Spy_Cleaned.svg");
}

module waves_block() {
    // Ein solider Block, der exakt die feinen Soundwellen umschließt
    translate([6.6, -0.5])
        square([6.2, 7.5], center=true);
}

module logo_tower_2d() {
    // Ein massiver ovaler Turm (20x15mm), der das filigrane Logo trägt
    hull() {
        translate([-2.5, 0]) circle(r=7.5);
        translate([2.5, 0]) circle(r=7.5);
    }
}


module cutouts() {
    // 1. THE HARMONIOUS L-SHAPE CABLE TRENCH
    difference() {
        union() {
            // Vertikaler Kanal - STRAIGHT WALLS
            // Breite auf 17.0 -> Rechte Wand ist bündig mit X=26.65
            // Länge auf 44.6 -> Obere Kante endet exakt bei Y=73.25!
            translate([9.65, 28.65, depth + flange_t - cable_well_depth])
                straight_pocket(17.0, 44.6, cable_well_depth + eps, 7.5);
                
            // SQUARED OFF TOP-RIGHT CORNER
            translate([19.15, 60.15, depth + flange_t - cable_well_depth])
                cube([7.5, 13.1, cable_well_depth + eps]);
                
            // ZWISCHENWAND TIP ROUNDING
            translate([26.65 + 4.705, 52.65 + 4.705, depth + flange_t - cable_well_depth])
                difference() {
                    translate([-4.705 - eps, -4.705 - eps, -eps])
                        cube([4.705 + eps, 9.41 + 2*eps, cable_well_depth + 2*eps]);
                    translate([0, 0, -2*eps])
                        cylinder(h=cable_well_depth + 4*eps, r=4.705, $fn=60);
                }
                
            // Horizontales Hauptfach - STRAIGHT WALLS
            translate([9.65, 28.65, depth + flange_t - cable_well_depth])
                straight_pocket(86.0, 24.0, cable_well_depth + eps, 7.5);
                
        }
        
        // Zwischenwand ergibt sich aus negativem Raum!
        
        // ==========================================
        // CABLE RETENTION: WAAGERECHTE HALTE-LIPPEN (ZUNGEN)
        // Hauchdünne (1.2mm), extrem flexible TPU-Lippen ganz oben am Rand.
        // Perfekt abgerundet (Pillen-Form), sodass keine Kabel aufschlitzen.
        // ==========================================
        union() {
            // A) Vertikaler Kanal (Breite X=17.0)
            retaining_lip_x(9.65, 38.0, depth + flange_t + eps, true, 12.0, 6.0, 1.2);
            
            // NEU: Kabelhalter exakt hinten am Ende des Schafts (wie gewünscht gekrikelt)
            // Die Lippe ist bei Y=64, also greift sie exakt das Kabel, wenn es aus dem Mic-Schaft kommt!
            retaining_lip_x(9.65, 64.0, depth + flange_t + eps, true, 12.0, 8.0, 1.2);
           
            
            // B) Horizontales Hauptfach (Breite Y=24.0)
            retaining_lip_y(35.0, 28.65, depth + flange_t + eps, true, 12.0, 8.0, 1.2);
            // Diese Klappe war bei X=53, aber da die Zwischenwand dort jetzt gelöscht ist, 
            // hing sie in der Luft. Ich habe sie auf X=70 verschoben, wo die Wand wieder massiv ist.
            retaining_lip_y(70.0, 52.65, depth + flange_t + eps, false, 12.0, 8.0, 1.2);
            retaining_lip_y(85.0, 28.65, depth + flange_t + eps, true, 12.0, 8.0, 1.2);
        }
    }

    // 2. HORIZONTAL MIC STORAGE (NEGATIVE MOLD)
    // EXAKT WIEDERHERGESTELLT - DIE MASSE SIND HEILIG
    chan_y = 66.0;
    z_center = depth + flange_t - 5; 
    
    // 2. MAIN COUPLER CHASSIS (MIC SHAFT)
    // Retour: Wieder ein simpler, gerader Schaft ohne integrierte Rampe.
    // Die restlichen Zylinder des Mikrofons (ganz normal)
    translate([22.65, chan_y + 1.65, z_center])
        rotate([0, 90, 0]) {
            cylinder(h=65.0, d=14.0 + 1.0);
            translate([0, 0, 65.0]) cylinder(h=28.5, d=24.0 + 1.0);
            translate([0, 0, 93.5]) cylinder(h=18, d=14.0 + 1.0);
        }

    // 3. FINGER-KRATER & KABELGRABEN-MERGE (Unified Basin)
    // 3. FINGER-KRATER & KABELGRABEN-MERGE (Unified Basin)
    // 3. FINGER-KRATER & KABELGRABEN-MERGE (Unified Basin)
    // 3. FINGER-KRATER & KABELGRABEN-MERGE (Unified Basin)
    // Die Zwischenwand ist komplett entfernt! Das Mikrofonfach fließt stufenlos in den Kabelgraben.
    translate([0, 0, 5.0]) {
        linear_extrude(height=40.0) {
            // Wir nutzen ein exaktes Polygon, weil hull() keine inneren Kurven (konkav für das Solid) kann!
            polygon(points = concat(
                // Oben Rechts: Die Rückseite vom Mic bleibt komplett gerade wie vorher (Y=73.5)
                [ [62.65, 73.5] ],
                
                // DIE PERFEKTE RUNDUNG (Gekrikelt):
                // Wir berechnen hier mit Sinus/Cosinus einen makellosen 8.5mm Radius Bogen.
                // Er ist oben bei [62.65, 58.5] absolut bündig mit dem 25mm Schaft-Kanal 
                // und unten bei [54.15, 50.0] absolut bündig mit dem leeren Kabelgraben.
                [ for(a = [0 : -5 : -90]) [54.15 + 8.5 * cos(a), 58.5 + 8.5 * sin(a)] ],
                
                // Unten Links & Rechts: 
                // Zieht den Krater tief in den Kabelgraben (Y=50.0), um Ghost-Walls zu verhindern,
                // und hält die rechte Wand zu 100% schnurgerade.
                [ [22.65, 50.0], [22.65, 73.5] ]
            ));
        }
    }

    // 4. BOTTOM BAND: TIP HOLDERS
    for(x = tip_xs) {
        translate([x, tip_y, depth + flange_t - tip_bore_depth]) {
            difference() {
                cylinder(h=tip_bore_depth + eps, d=tip_bore_d, $fn=60);
                union() {
                    translate([0, 0, -eps]) cylinder(h=tip_bore_depth - 1.0, d=6.0, $fn=30);
                    translate([0, 0, tip_bore_depth - 1.0 - eps]) cylinder(h=1.0 + 3*eps, d1=6.0, d2=4.5, $fn=30);
                }
            }
        }
    }
    
            // 5. DAS INTEGRIERTE LOGO (Top Left)
    // A) Der massive Turm-Ausschnitt (von Z=2.0 bis Z=21.12)
    translate([20.0, 80.8, 2.0 - eps])
        linear_extrude(height=19.12 + eps)
            offset(r=0.2) logo_tower_2d(); // 0.2mm Toleranz
            
        // B) Die filigranen Logo-Löcher (Hat, Face, Ear)
    translate([20.0, 80.8, 21.12 - eps])
        linear_extrude(height=depth + flange_t - 21.12 + 2*eps)
            offset(r=0.2) custom_logo_2d();
            
    // C) Der Ausschnitt im TPU für den massiven Wellen-Block!
    translate([20.0, 80.8, 21.12 - eps])
        linear_extrude(height=depth + flange_t - 21.12 + 2*eps)
            offset(r=0.2) waves_block();
}

// ==========================================
// 6. PETG FULL CHASSIS (Rigid Skeleton)
// ==========================================
module petg_chassis(tol=0) {
    difference() {
        union() {
            // Haupt-Bodenplatte (Nutzer-Korrektur)
            // Da die Peli-Kiste am Boden einen extrem dicken Fillet (Rundung zur Seitenwand) hat,
            // lassen wir an jeder Seite exakt 3.0 mm Luft (insgesamt 6.0 mm schmaler).
            // So schlägt die harte 2.0mm Platte nicht gegen die Kisten-Rundung und liegt 100% flach auf.
            translate([base_dx + 3.0, base_dx + 3.0, 0])
                rounded_rect(base_x - 6.0, base_y - 6.0, 2.0, base_r - 3.0);
                
            // NEU: Support-Fuß für den Logo-Turm, damit er nicht in der Luft hängt!
            // Da der Turm Y=88.3 erreicht, die Bodenplatte aber bei 87.0 aufhört.
            translate([20.0, 80.8, 0])
                linear_extrude(height=2.0)
                    logo_tower_2d();
                
            
                        // 3. DIE LOGO-STELZEN & TURM (Top Left Corner)
            // A) Der massive Basis-Turm (Z=2.0 bis Z=21.12)
            translate([20.0, 80.8, 2.0 - eps])
                linear_extrude(height=19.12 + eps)
                    logo_tower_2d();
                    
                        // B) Die filigranen Logo-Details (Hut, Gesicht, Ohr, Wellen)
            translate([20.0, 80.8, 21.12 - eps])
                linear_extrude(height=depth + flange_t - 21.12 + eps)
                    custom_logo_2d();
                    
            // C) NEU: Der massive Block unter den Wellen (verhindert Abbrechen!)
            // Geht nur bis Z=24.12, sodass die Wellen oben 1mm erhaben herausstechen!
            translate([20.0, 80.8, 21.12 - eps])
                linear_extrude(height=3.0)
                    waves_block();
            
            // Main PETG Tube (OD: 22mm)
            // GEKÜRZT AUF 41.5mm! (Absolute Decke der Peli-Kiste ist bei 42.42mm).
            translate([109.65, 41.65, 0]) 
                cylinder(h=41.5, d=22.0);
                
            // Das neue TPU-Spar-Gestell (massiv PETG, mit 45° Dächern)
            petg_support_blocks(tol);
        }
        
        // Tube Cutouts
        translate([109.65, 41.65, 0]) {
            // Upper Socket for TPU Sleeve (18mm diameter)
            // USER REQUEST: Zwischenebene 2mm höher! (Von Z=24 auf Z=26)
            translate([0, 0, 26]) 
                cylinder(h=20 + eps, d=18.0);
                
            // Snap-In Locking Groove for TPU Sleeve (Bleibt bei Z=34)
            translate([0, 0, 34])
                cylinder(h=2.0, d=19.0);
                
            // Lower Hole for Strain Relief (Hangs freely in the air)
            // Wurde auf 26mm verlängert, damit es bis zur neuen Zwischenebene reicht!
            translate([0, 0, -eps]) 
                cylinder(h=26 + 2*eps, d=12.0);
                
            // 5mm Cable Slit facing LEFT (-X) towards the Cable Trench
            // USER REQUEST: Komplett durch die Base-Platte (Z=-eps) für maximalen Platz und weniger Knick!
            translate([-15, -2.5, -eps]) 
                cube([15, 5.0, 44 + 2*eps]);
        }
    }
}

module tpu_chassis_cutout(tol=0.2) {
    // Schneidet nur den inneren Bereich für das PETG-Skelett aus,
    // lässt aber einen 2.0mm dicken TPU-Rand an der Unterseite stehen!
    // tol=0.2 gibt dem Snap-Fit etwas Spielraum zum Einrasten
    translate([base_dx + 2.0 - tol, base_dx + 2.0 - tol, -eps])
        rounded_rect(base_x - 4.0 + 2*tol, base_y - 4.0 + 2*tol, 2.0 + 2*eps, base_r - 2.0 + tol);
        
    // Einhak-Nut (Groove) im TPU, in die die PETG-Lippe einrastet
    // Z=1.0 bis Z=2.0. Geht 0.8mm tief ins TPU.
    translate([base_dx + 1.2 - tol, base_dx + 1.2 - tol, 1.0])
        rounded_rect(base_x - 2.4 + 2*tol, base_y - 2.4 + 2*tol, 1.0 + eps, base_r - 1.2 + tol);
        
    // Cutout for the PETG Tube and the Cable Slit in the TPU Base
    translate([109.65, 41.65, 0]) {
        // Hole for the Tube
        translate([0, 0, -eps]) 
            cylinder(h=50, d=22.0);
            
        // Slit extended into the TPU to connect to the Cable Trench
        // Straight-Walled
        translate([-25.0, -2.5, depth + flange_t - cable_well_depth]) 
            straight_pocket(25.0, 5.0, cable_well_depth + eps, 2.5);
            
        // Top Chamfer (2mm) für das große runde Tower-Loch!
        translate([0, 0, depth + flange_t - 2.0])
            cylinder(h=2.0 + eps, r1=11.0, r2=13.0);
    }
}

// ==========================================
// 5. TPU WEIGHT RELIEF (Material sparen)
// ==========================================
// 5. PETG SUPPORT BLOCKS (Das "Gestell")
// ==========================================
// Hilfsmodul: Erzeugt das perfekte Innenvolumen der Peli-Kiste abzüglich
// einer exakten TPU-Wandstärke (wall).
module tpu_safe_zone(wall = 4.0) {
    hull() {
        // Base profile (Z=0)
        translate([base_dx + wall, base_dx + wall, 0])
            rounded_rect(base_x - 2*wall, base_y - 2*wall, eps, base_r - wall);
            
        // Top profile (Z=depth)
        translate([wall, wall, depth])
            rounded_rect(rim_x - 2*wall, rim_y - 2*wall, eps, fillet_r - wall);
    }
}

// Hilfsmodul: Erzeugt einen Block mit einem 45-Grad-Dach (Zeltdach).
// Dadurch lässt sich das TPU-Teil komplett OHNE Support-Strukturen drucken,
// da es keine flachen Überhänge (Decken) in den Hohlräumen gibt!
module support_free_block(w, d, h, tol=0) {
    tw = w + 2*tol;
    td = d + 2*tol;
    th = h + tol;
    
    // Ein 45-Grad Dach braucht exakt d/2 an Höhe.
    roof_h = min(th, td/2);
    wall_h = th - roof_h;
    
    translate([-tol, -tol, 0]) {
        hull() {
            // Grundfläche
            cube([tw, td, eps]);
            // Senkrechte Wände bis zum Beginn des 45°-Daches
            if (wall_h > 0) {
                translate([0, 0, wall_h]) cube([tw, td, eps]);
            }
            // Dachfirst (Linie in der Mitte) für perfekten 45-Grad-Überhang
            translate([0, td/2, th]) cube([tw, eps, eps]);
        }
    }
}

// V170: Einfache Führungs-Stifte (Lego-Prinzip)
// Das TPU klemmt sich durch Friction-Fit stramm an die geraden Stäbe.
module petg_alignment_peg(h, d, tol=0) {
    // Die Toleranz macht den Stift beim Ausschneiden aus dem TPU dicker.
    cylinder(h = h, d = d + 2*tol, $fn=30);
}

// Spart massiv teures TPU und gibt der dünnen PETG-Platte gigantische Steifigkeit.
// 100% SUPPORT-FREE für das TPU!
module petg_support_blocks(tol = 0) {
    intersection() {
        // Safe Zone: Garantiert eine dicke, stabile 4.0mm Außenwand am TPU!
        tpu_safe_zone(wall = 4.0 - tol);
        
        union() {
            // ALIGNMENT PEGS (Führungs-Stifte)
            // Höhe 15.0 in den massiven Außen-Ecken des TPU-Blocks.
            // Spannen das größtmögliche Dreieck am Rand auf.
            
            // Ecke Unten Links (Neben den Tip-Löchern)
            translate([11.0, 11.0, 0]) petg_alignment_peg(15.0, 6.0, tol);
            
            // Ecke Oben Links (Neben dem Mikrofon-Schacht)
            translate([11.0, 77.0, 0]) petg_alignment_peg(15.0, 6.0, tol);
            
            // Ecke Oben Rechts (Neben dem Mikrofon-Kopf)
            translate([122.0, 77.0, 0]) petg_alignment_peg(15.0, 6.0, tol);

            // Block A: Unter den Silikon-Tips
            // FIX: Höhe von 14.0 auf 3.0 reduziert, da die Tip-Löcher bis Z=5.12 hinunterreichen!
            translate([11.65, 6.65, 0]) support_free_block(120, 18, 3.0, tol);
                
            // Block B: Unter dem schmalen Mikrofon-Schaft
            // Höhe auf 2.0 + eps erhöht, um Coplanar Face mit dem Z=2.0 Radikal-Schnitt zu vermeiden!
            translate([20.0, 55.0, 0]) support_free_block(60, 18, 2.0 + eps, tol);
            
            // Block C: Der "tote Winkel" (Rechts neben Kabelfach)
            translate([96.65, 31.65, 0]) support_free_block(30, 20, 18.0, tol);
        }
    }
}

// --- 5.1 TPU Aussparungen für das Gestell ---
module tpu_weight_relief() {
    // Zieht das Gestell aus dem TPU ab, mit 0.3mm Toleranz für leichten Press-Fit!
    petg_support_blocks(0.3);
}

// ==========================================
// 6. TPU TOWER SLEEVE (Das Grip-Inlay)
// ==========================================
// Dieses winzige TPU-Teil rastet in die PETG-Röhre ein und greift den Stahlschaft.
module tpu_tower_sleeve() {
    // Rendern über der PETG-Röhre für Explosions-Ansicht
    translate([109.65, 41.65, 46]) {
        difference() {
            union() {
                // Main Body (18.2mm OD = strammer Pressfit in die 18.0mm PETG Röhre)
                // USER REQUEST: Um 2mm gekürzt auf 15.5mm (Passt perfekt auf die neue Z=26 Ebene)
                cylinder(h=15.5, d=18.2, $fn=60);
                
                // Snap-In Ring (Rastet in die Rille bei Z=34 ein, also bei 8mm von unten)
                translate([0, 0, 8.0]) cylinder(h=2.0, d=19.2, $fn=60);
                
                // Top Collar (Lippe am oberen Rand)
                // Z=15.5 (Da der Main Body 15.5 hoch ist, sitzt der Deckel direkt darauf!)
                translate([0, 0, 15.5]) cylinder(h=2.0, d=22.0, $fn=60);
            }
            
            // Innerer Schaft für den 14mm Coupler (13.8mm = extremer Grip!)
            // Mit 4 professionellen, runden Entlastungs-Nuten (Spannzangen-Prinzip) für die BNC-Pins.
            union() {
                translate([0, 0, -eps]) cylinder(h=24, d=13.8, $fn=60);
                
                // 4 perfekt runde Nuten (Flutes). Max Durchmesser = 15.5mm.
                // Verhindert Einreißen des TPU und sieht aus wie ein professionelles Maschinenteil.
                for(a = [0, 90, 180, 270]) {
                    rotate([0, 0, a])
                        translate([6.0, 0, -eps]) cylinder(h=24, d=3.5, $fn=30);
                }
            }
            
            // Kabel-Schlitz (Muss mit dem PETG-Schlitz fluchten)
            translate([-15, -2.5, -eps]) cube([15, 5.0, 24]);
        }
    }
}

// --- Final Assembly Rendering ---

module dummy_coupler() {
    color("Silver") {
        cylinder(h=stem_len, d=stem_od);
        translate([0, 0, stem_len]) cylinder(h=head_len, d=head_od);
        translate([0, 0, stem_len + head_len]) cylinder(h=adapter_tip_len, d=adapter_tip_od);
    }
}

module tpu_insert_full() {
    difference() {
        union() {
            // Original TPU logic
            difference() {
                peli_body();
                cutouts();
                tpu_chassis_cutout(); // Loch für das PETG Chassis
                tpu_weight_relief();  // Massive Gewölbe an der Unterseite
            }
        }
        
        // RADIKAL-SCHNITT: Wir schneiden die untersten 2.0 mm komplett weg!
        // Dadurch wird der Boden des TPU zu 100% flach und braucht keine Supports mehr.
        // Der Slicer lässt das Teil automatisch auf Z=0 fallen.
        // Die 2.0mm dicke PETG-Platte wird später beim Zusammenbau einfach als
        // Fundament ganz unten in die Kiste gelegt, das flache TPU kommt oben drauf!
        translate([-50, -50, -10])
            cube([300, 300, 12.0]); // Schneidet alles unter Z=2.0 weg
    }
}

module assembly() {
    if (show_tpu_main) {
        color("Gold", 1.0) tpu_insert_full();
    }
    if (show_petg_chassis) {
        color("DarkSlateGray") petg_chassis();
    }
    if (show_tpu_sleeve) {
        color("OrangeRed") tpu_tower_sleeve();
    }
    if (show_dummy_mic) {
        translate([108, 40, 44]) rotate([0, 180, 0]) dummy_coupler();
    }
}

// ==========================================
// RENDER OUTPUT
// ==========================================
module test_print(part="tpu") {
    // =======================================================
    // ULTRA-MINIMALER TESTDRUCK (So wenig Material wie möglich)
    // =======================================================
    
    if (part == "tpu" || part == "both") {
        // Wir schieben das TPU-Teil um 2mm nach unten (Z=-2.0),
        // damit es flach auf dem Druckbett liegt (da das Original eine 2mm Lücke für die PETG-Bodenplatte hat!)
        translate([0, 0, -2.0]) {
            intersection() {
                tpu_insert_full();
                // Bounding Box EXAKT auf die Mulde zugeschnitten:
                // X=20 bis X=96 -> 76mm
                // Y=50 (Kabelkanal-Wand) bis Y=85 -> 35mm
                // Z=2.0 (Boden) bis Z=30 (über dem Mikrofon) -> 28mm
                translate([20.0, 50.0, 2.0])
                    cube([76.0, 35.0, 28.0]);
            }
        }
    }
}



if (show_test_print) {
    color("Gold", 1.0) test_print();
    if (show_dummy_mic) {
        translate([108, 40, 44]) rotate([0, 180, 0]) dummy_coupler();
    }
} else if (show_cross_section) {
    difference() {
        assembly();
        translate([-50, -50, -50])
            cube([300, 120, 200]);
    }
} else {
    assembly();
}
