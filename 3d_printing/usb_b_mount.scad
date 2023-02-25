
usb_b = [10.2, 12.1, 16.4];
wall_t = 1;
t = 1.5;
gap = usb_b.z/2;
hole = [-1.2, 6.9, usb_b.z*100];
hole_r = 2.7/2;

difference(){
    union(){
        cube(usb_b + [2*t, 2*t + (hole.y + 2*t)*2, t-wall_t], center=true);
    }
    translate([0, 0, t/2])
    cube(usb_b + [0, 0, -wall_t], center=true);
    translate([t, 0, t/2 - (usb_b.z - wall_t)/2 + gap/2])
    cube([usb_b.x, usb_b.y, gap], center=true);
    for (y = [-1, 1]){
        translate([hole.x, (hole.y + usb_b.y/2)*y, -hole.z/2])
        cylinder(hole.z, hole_r, hole_r, $fn=10);
    }
}
