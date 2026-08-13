// =====================================================================
//  CỐP CỨNG ĐỰNG MÁY HÚT SỮA KHÔNG DÂY eufy S2 Pro
//  Vỏ 2 nửa mở gập (clamshell) + nắp trên phẳng + quai xách gập
//
//  Đơn vị: mm.  Cần OpenSCAD >= 2021.01
//  Render 1 chi tiết:  openscad -D 'part="base"' -o base.stl cop-eufy-s2-pro.scad
//  Hoặc chạy:          ./build.sh
//
//  !!! ĐỌC TRƯỚC KHI IN: các số ở MỤC 1 và MỤC 2 là ƯỚC LƯỢNG.
//      Phải đo máy hút sữa thật rồi sửa lại, xem README.md.
// =====================================================================

/* [Chi tiết cần render] */
// all = lắp ráp | open = mở nắp | cut = bổ đôi xem thành
part = "all";               // ["all","open","cut","base","lid","cap","handle","pin"]
show_payload = false;       // hiện khối bao của máy hút sữa (chỉ để xem)

/* ---------------------------------------------------------------
   MỤC 1. KÍCH THƯỚC LÒNG CỐP  <-- SỬA Ở ĐÂY
   --------------------------------------------------------------- */
in_len   = 165;   // lòng cốp theo trục X (chiều dài)
in_wid   = 140;   // lòng cốp theo trục Y (chiều ngang)
dep_bot  = 82;    // độ sâu nửa dưới, tính từ mặt chia xuống đáy
dep_top  = 75;    // chiều cao "ảo" nửa trên (phần chỏm bị cắt phẳng làm nắp)
n_bot    = 3.0;   // độ "vuông" của nửa dưới: 2 = ellipsoid, càng lớn càng đứng thành
n_top    = 2.4;   // độ "vuông" của nửa trên

foot_cut = 5;     // cắt phẳng đáy bấy nhiêu mm để cốp đứng vững + bám bàn in

/* ---------------------------------------------------------------
   MỤC 2. KHỐI BAO CỦA MÁY HÚT SỮA (chỉ dùng để kiểm tra vừa/không)
   --------------------------------------------------------------- */
pay_x = 130;      // 2 cốc hút úp vào nhau: chiều dài
pay_y = 118;      //                        chiều ngang
pay_z = 118;      //                        chiều cao
pay_gap = 3;      // kê cách đáy

/* ---------------------------------------------------------------
   MỤC 3. THÀNH VỎ & DUNG SAI
   --------------------------------------------------------------- */
wall = 2.4;       // dày thành (in 3 perimeter với vòi 0.4)
fit  = 0.35;      // khe hở giữa các chi tiết khớp vào nhau
seg  = 128;       // độ mịn mặt cong

/* ---------------------------------------------------------------
   MỤC 4. GỜ CHẶN MIỆNG (nửa dưới thò lên, chui vào nửa trên)
   --------------------------------------------------------------- */
lip_h    = 7;     // cao gờ
lip_t    = 2.0;   // dày gờ
lip_root = 10;    // chân gờ ăn xuống dưới mặt chia bấy nhiêu (để dính vào thành)

/* ---------------------------------------------------------------
   MỤC 5. BẢN LỀ (phía -X, chốt xỏ que ø3)
   --------------------------------------------------------------- */
hg_r    = 5;      // bán kính ống bản lề
hg_pin  = 3.2;    // lỗ xỏ trục (que in sẵn, hoặc vít M3)
hg_w    = 14;     // bề rộng mỗi khấc
hg_gap  = 0.5;    // khe giữa khấc trên và khấc dưới
hg_clr  = 0.8;    // khe từ mặt vỏ ra tới ống bản lề

/* ---------------------------------------------------------------
   MỤC 6. CHỐT KHOÁ (phía +X: dây chốt ở nửa dưới, vấu ở nửa trên)
   --------------------------------------------------------------- */
lt_w      = 22;   // rộng dây chốt
lt_t      = 2.4;  // dày dây chốt (mỏng thì dễ bật, dày thì cứng)
lt_clr    = 0.7;  // khe giữa dây chốt và mặt vỏ
lt_z0     = -36;  // cao độ chân dây chốt
lt_z1     = 27;   // cao độ đỉnh dây chốt (chỗ bấm ngón tay)
lt_hole_z = 9.0;  // đáy lỗ trên dây chốt
lt_hole_h = 5.0;  // cao lỗ
lt_hole_w = 13;   // rộng lỗ
lt_flex_t = 1.6;  // dày đoạn eo mềm — chỗ dây chốt gập khi bấm mở
lt_flex_h = 12;   // cao đoạn eo mềm (bỏ eo này thì phải bấm rất nặng)
nub_out   = 4.2;  // vấu nhô ra (khi bấm, dây chốt phải lệch nub_out - lt_clr mm)
nub_w     = 11;   // rộng vấu
nub_z0    = 5.5;  // chân dốc vát của vấu
nub_z1    = 13.6; // mặt trên vấu (mặt chịu lực)

/* ---------------------------------------------------------------
   MỤC 7. NẮP TRÊN (cắt chỏm để in không cần support)
   --------------------------------------------------------------- */
max_ang  = 45;    // góc dốc nhỏ nhất còn in được -> quyết định chỗ cắt chỏm
cap_t    = 3.2;   // dày nắp trên
cap_ch   = 1.2;   // vát mép trên nắp
fl_w     = 9;     // bề rộng vành đỡ nắp (bên trong nửa trên)
fl_t     = 4.5;   // dày vành đỡ
screw_d  = 2.6;   // lỗ mồi vít M3 tự ren
screw_cs = 6.4;   // đường kính khoét đầu vít chìm trên nắp
spig_h   = 4;     // gờ định vị dưới nắp
spig_t   = 2.2;
cap_text = "";    // khắc chữ lên nắp, vd "eufy S2 Pro" (để "" là không khắc)
cap_text_size = 11;

/* ---------------------------------------------------------------
   MỤC 8. QUAI XÁCH (gập được, gắn vào hông nửa dưới)
   --------------------------------------------------------------- */
bail_on   = true;
bail_w    = 16;   // bề rộng quai
bail_t    = 5;    // dày quai
bail_rise = 18;   // đỉnh quai cao hơn mặt nắp bấy nhiêu
lug_h     = 8;    // tai quai nhô ra khỏi hông
lug_d     = 14;   // đường kính tai quai
lug_z     = -8;   // cao độ tâm trục quai
peg_d     = 3.2;  // chốt quai
peg_l     = 5;

// =====================================================================
//                      TÍNH TOÁN — KHÔNG SỬA
// =====================================================================
AXi = in_len/2;  AYi = in_wid/2;  HBi = dep_bot;  HTi = dep_top;   // mặt trong
AX  = AXi+wall;  AY  = AYi+wall;  HB  = HBi+wall; HT  = HTi+wall;  // mặt ngoài

z_floor_o = -HB + foot_cut;          // đáy ngoài (mặt phẳng)
z_floor_i = z_floor_o + wall;        // đáy trong

// Cao độ cắt chỏm: chỗ mặt ngoài dốc đúng max_ang (hướng X thoải nhất nên lấy AX)
function z_tan(a, h, n, ang) =
    let(p = 2/n, th = atan(pow((h/a)/tan(ang), 1/(2-p))))
    h*pow(sin(th), p);

z_cap  = z_tan(AX, HT, n_top, max_ang);   // mặt trên cùng của cốp
z_seat = z_cap - cap_t;                   // mặt tựa của nắp = mép trên nửa trên

// Bán kính mặt cắt ngang ở cao độ z (dùng cho tính vị trí vít, in bảng tra)
function fac(z, h, n) = pow(1 - pow(abs(z)/h, n), 1/n);
function rX(z, g=0) = (AXi-g) * fac(z, (z>=0?HTi:HBi)-g, z>=0?n_top:n_bot);
function rY(z, g=0) = (AYi-g) * fac(z, (z>=0?HTi:HBi)-g, z>=0?n_top:n_bot);

PX   = AX + hg_r + hg_clr;   // tâm trục bản lề (x = -PX)
hg_z = hg_r;                 // trục bản lề nằm trên mặt chia, ống tiếp tuyến mặt bàn in
                             // -> nửa trên in úp miệng xuống vẫn không cần support

z_mid  = z_seat - fl_t/2;
sx_scr = (rX(z_mid,0) + rX(z_mid,fl_w))/2;   // vị trí 2 vít theo trục X
sy_scr = (rY(z_mid,0) + rY(z_mid,fl_w))/2;   // vị trí 2 vít theo trục Y

y_lug  = rY(lug_z) + wall + lug_h;           // mặt ngoài tai quai
y_bail = y_lug + 0.6 + bail_t/2;             // tim chân quai
b_bail = (z_cap + bail_rise) - lug_z;        // bán trục đứng của quai

pay_z0 = z_floor_i + pay_gap;

// ---------- Báo số liệu ra console ----------
echo(str("== KÍCH THƯỚC NGOÀI: ", AX*2, " x ", AY*2, " x ", -z_floor_o + z_cap, " mm (chưa kể bản lề/chốt)"));
echo(str("== LÒNG CỐP: cao ", z_seat - z_floor_i, " mm (đáy ", z_floor_i, " -> nắp ", z_seat, ")"));
echo(str("== NẮP TRÊN: ", rX(z_seat)*2 + wall*2, " x ", rY(z_seat)*2 + wall*2, " mm, cắt ở z = ", z_cap));
echo("== BẢNG TRA LÒNG CỐP (z: dài X x ngang Y) ==");
for (z = [-70, -60, -40, -20, 0, 20, 30, 40]) if (z > z_floor_i && z < z_seat)
    echo(str("   z=", z, ": ", floor(rX(z)*2), " x ", floor(rY(z)*2)));

// Kiểm tra khối bao máy hút sữa
function inside(x, y, z) =
    let(h = z>=0 ? HTi : HBi, n = z>=0 ? n_top : n_bot,
        rr = sqrt(pow(x*AYi/AXi, 2) + y*y))
    (pow(rr/AYi, n) + pow(abs(z)/h, n) <= 1) && z <= z_seat && z >= z_floor_i;
ok_pay = inside( pay_x/2,  pay_y/2, pay_z0) && inside( pay_x/2,  pay_y/2, pay_z0+pay_z)
      && inside(-pay_x/2, -pay_y/2, pay_z0) && inside(-pay_x/2, -pay_y/2, pay_z0+pay_z);
echo(str("== KHỐI BAO MÁY ", pay_x, "x", pay_y, "x", pay_z, ": ",
         ok_pay ? "LỌT (4 góc đều trong lòng)"
                : "GÓC HỘP CHẠM VỎ — máy thật bo tròn nên vẫn có thể vừa, xem bảng tra ở trên"));

// =====================================================================
//                          HÌNH HỌC CƠ SỞ
// =====================================================================
module slab(z0, z1) translate([-600,-600,z0]) cube([1200,1200,z1-z0]);

// Biên dạng nửa mặt cắt dọc: siêu-ellipse, đáy phẳng dần khi n lớn
function prof(a, hb, ht, nb, nt, st=48) = concat(
    [ for (i=[0:st]) let(t = 90 - 90*i/st) [ a*pow(cos(t), 2/nb), -hb*pow(sin(t), 2/nb) ] ],
    [ for (i=[1:st]) let(t = 90*i/st)      [ a*pow(cos(t), 2/nt),  ht*pow(sin(t), 2/nt) ] ]
);

module body(ax, ay, hb, ht)
    scale([ax/ay, 1, 1]) rotate_extrude($fn=seg) polygon(prof(ay, hb, ht, n_bot, n_top));

module outer_body(g=0) body(AX+g,  AY+g,  HB+g,  HT+g);
module inner_body(g=0) body(AXi-g, AYi-g, HBi-g, HTi-g);

module inner_solid() intersection(){ inner_body(); slab(z_floor_i, 600); }   // khoang rỗng

module shell() difference(){
    intersection(){ outer_body(); slab(z_floor_o, 600); }
    inner_solid();
}

// =====================================================================
//                          NỬA DƯỚI (base)
// =====================================================================
module rim_lip() difference(){
    union(){
        intersection(){ inner_body(-0.2); slab(-lip_root, 0); }  // chân gờ, dính vào thành
        intersection(){ inner_body(fit);  slab(0, lip_h); }      // phần thò lên, chừa khe fit
    }
    inner_body(fit + lip_t);
    slab(-600, z_floor_i);
}

module hinge_barrel(w) translate([-PX, 0, hg_z]) rotate([90,0,0])
    cylinder(h=w, r=hg_r, center=true, $fn=48);

module hinge_hull(w, up)                    // ống bản lề + nêm nối vào vỏ
    hull(){
        hinge_barrel(w);
        translate([-AX+4, 0, up ? 9 : -9]) cube([8, w, 10], center=true);
    }

// Phần nằm ngoài mặt vỏ (x <= -PX+hg_r) giữ nguyên cả trên lẫn dưới mặt chia;
// phần thò vào trong mới bị cắt theo mặt chia, nếu không nêm sẽ rời khỏi ống.
module hinge_base(){                        // 2 khấc ngoài
    for (s = [-1, 1]) translate([0, s*(hg_w + hg_gap), 0]) {
        intersection(){ hinge_hull(hg_w, false); translate([-600,-600,-600]) cube([600-PX+hg_r, 1200, 1200]); }
        intersection(){ hinge_hull(hg_w, false); slab(-600, 0); }
    }
}
module hinge_lid() hinge_hull(hg_w, true);  // 1 khấc giữa, nằm trọn trên mặt chia
module hinge_pin() translate([-PX, 0, hg_z]) rotate([90,0,0])
    cylinder(h=200, d=hg_pin, center=true, $fn=32);

module latch_strap(){                       // dây chốt trên nửa dưới
    x0 = AX + lt_clr;
    difference(){
        union(){
            translate([x0, -lt_w/2, lt_z0]) cube([lt_t, lt_w, lt_z1-lt_z0]);
            translate([x0, -lt_w/2, lt_z1-6]) cube([lt_t+4, lt_w, 6]);          // mấu bấm ngón
            hull(){                                                              // chân dây chốt
                translate([x0, -lt_w/2, lt_z0]) cube([lt_t, lt_w, 10]);
                translate([AX-6, -lt_w/2, lt_z0-12]) cube([6, lt_w, 8]);
            }
        }
        translate([x0-1, -lt_hole_w/2, lt_hole_z])                               // lỗ ăn vấu
            cube([lt_t+8, lt_hole_w, lt_hole_h]);
        hull() for (z = [lt_z0+11, lt_z0+11+lt_flex_h])                          // eo mềm (mặt trong)
            translate([x0, -lt_w/2-1, z]) rotate([-90,0,0])
                cylinder(r=lt_t-lt_flex_t, h=lt_w+2, $fn=24);
        translate([x0+lt_t, -lt_w/2-1, lt_z1-6])                                 // vát dưới mấu bấm
            rotate([0,45,0]) cube([8, lt_w+2, 8]);
    }
}

module latch_nub()                          // vấu trên nửa trên
    hull(){
        translate([AX-3, -nub_w/2, nub_z0]) cube([3, nub_w, 0.1]);
        translate([AX-3, -nub_w/2, nub_z0 + nub_out]) cube([3+nub_out, nub_w, nub_z1-nub_z0-nub_out]);
    }

module bail_lugs() if (bail_on) for (s = [-1,1]) hull(){
    translate([0, s*(y_lug - lug_d/2), lug_z]) rotate([90,0,0])
        cylinder(h=lug_d, d=lug_d, center=true, $fn=48);
    translate([0, s*(y_lug - lug_d/2), lug_z - 14]) rotate([90,0,0])
        cylinder(h=lug_d, d=2, center=true, $fn=16);          // nêm 45° phía dưới -> in được
}
module bail_holes() if (bail_on) for (s = [-1,1])
    translate([0, s*(y_lug + 0.5), lug_z]) rotate([90,0,0])
        cylinder(h=peg_l+1.5, d=peg_d+0.4, $fn=32);

module base() difference(){
    union(){
        intersection(){ shell(); slab(-600, 0); }
        difference(){ union(){ hinge_base(); latch_strap(); bail_lugs(); } inner_solid(); }
        rim_lip();
    }
    hinge_pin();
    bail_holes();
}

// =====================================================================
//                          NỬA TRÊN (lid)
// =====================================================================
module top_flange() difference(){            // vành đỡ nắp, mặt dưới vát 45° cho in được
    intersection(){ inner_body(); slab(z_seat - fl_t, z_seat); }
    hull(){
        intersection(){ inner_body(fl_w);        slab(z_seat - 0.02, z_seat); }
        intersection(){ inner_body(fl_w - fl_t); slab(z_seat - fl_t, z_seat - fl_t + 0.02); }
    }
}

module screw_pts(){
    for (p = [[sx_scr,0], [-sx_scr,0], [0,sy_scr], [0,-sy_scr]])
        translate([p[0], p[1], 0]) children();
}
module screw_pilot() screw_pts() translate([0,0,z_seat - fl_t - 0.5])
    cylinder(h=fl_t+1, d=screw_d, $fn=24);

module lid() difference(){
    union(){
        intersection(){ shell(); slab(0, z_seat); }
        difference(){ union(){ hinge_lid(); latch_nub(); } inner_solid(); }
        top_flange();
    }
    hinge_pin();
    screw_pilot();
}

// =====================================================================
//                          NẮP TRÊN (cap)
// =====================================================================
module cap() difference(){
    union(){
        hull(){                                                   // tấm nắp + vát mép
            intersection(){ outer_body();          slab(z_seat, z_cap - cap_ch); }
            intersection(){ outer_body(-cap_ch);   slab(z_cap - cap_ch, z_cap); }
        }
        difference(){                                             // gờ định vị chui vào vành đỡ
            intersection(){ inner_body(fl_w + fit); slab(z_seat - spig_h, z_seat); }
            inner_body(fl_w + fit + spig_t);
        }
    }
    screw_pts(){                                                  // lỗ vít + khoét đầu chìm
        translate([0,0,z_seat-1]) cylinder(h=cap_t+2, d=screw_d+0.9, $fn=24);
        translate([0,0,z_cap-1.6]) cylinder(h=1.7, d1=screw_d+0.9, d2=screw_cs, $fn=24);
    }
    if (cap_text != "")
        translate([0,0,z_cap-0.6]) linear_extrude(1)
            text(cap_text, size=cap_text_size, halign="center", valign="center");
}

// =====================================================================
//                          QUAI XÁCH (handle)
// =====================================================================
// Trục bản lề in sẵn. Thay được bằng: que tre xiên ø3, vít M3x50, hoặc đoạn dây thép ø3.
module pin(){
    L = hg_w*3 + hg_gap*2 + 2;
    cylinder(h=L, d=hg_pin-0.25, $fn=32);
    cylinder(h=1.8, d=hg_pin+2.6, $fn=32);      // đầu chặn
}

module bail(){
    a = y_bail;
    difference(){
        union(){
            // vòng cung nằm trong mặt phẳng YZ (bắc qua chiều ngang), dày bail_w theo X
            translate([0,0,lug_z]) rotate([0,0,90]) rotate([90,0,0]) translate([0,0,-bail_w/2])
                linear_extrude(bail_w) difference(){
                    scale([a + bail_t/2, b_bail + bail_t/2]) circle(r=1, $fn=seg);
                    scale([a - bail_t/2, b_bail - bail_t/2]) circle(r=1, $fn=seg);
                }
            // chốt quai: cắm từ mặt trong thân quai, chĩa vào trong, ăn vào lỗ trên tai
            for (s=[-1,1]) translate([0, s*(y_bail - bail_t/2 + 1), lug_z])
                rotate([s>0?90:-90,0,0]) cylinder(h=peg_l+1, d=peg_d, $fn=32);
        }
        slab(-600, lug_z);
    }
}

// =====================================================================
//                          LẮP RÁP / XEM TRƯỚC
// =====================================================================
module payload_box() if (show_payload)
    %translate([-pay_x/2, -pay_y/2, pay_z0]) cube([pay_x, pay_y, pay_z]);

module lid_group(){ lid(); cap(); }

module assembled(open_ang = 0){
    base();
    translate([-PX, 0, hg_z]) rotate([0, -open_ang, 0]) translate([PX, 0, -hg_z]) lid_group();
    if (bail_on) bail();
    payload_box();
}

if      (part == "base")   base();
else if (part == "lid")    lid();
else if (part == "cap")    cap();
else if (part == "handle") bail();
else if (part == "pin")    pin();
else if (part == "open")   assembled(105);
else if (part == "cut")    difference(){ assembled(0); translate([-600,0,-600]) cube([1200,600,1200]); }
else                       assembled(0);
