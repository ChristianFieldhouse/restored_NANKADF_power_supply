
pico = [11.4, 48.26, 1.06];
r = (2.1 - 0.05)/2;
l = 6 - pico.z;
t = 1.5;

r0 = 0.7;

difference(){
    union(){
        cube([pico.x + 2*(r + t), pico.y + 2*(r + t), t]);
        for (x = [0, 1]){
            for (y = [0, 1]){
                translate([x*pico.x + t + r, y*pico.y + t + r])
                difference(){
                    translate([0, 0, t + l/2])
                    cube([2*(r+t), 2*(r+t), l], center=true);
                    translate([0, 0, t])
                    cylinder(l, r, r, $fn=20);
                }
            }
        }
    }
    hull()
    for (y = [0, 5]){
        for (x = [0, 2.5, 5, 7.5, 10, 12.5]){
            translate([x + 2.5, y + 12.5/2, 0])
            cylinder(t, r0, r0, $fn=10);
        }
    }
    hull()
    for (y = [17.5, 22.5]){
        for (x = [0, 2.5, 5, 7.5, 10, 12.5]){
            translate([x + 2.5, y + 12.5/2, 0])
            cylinder(t, r0, r0, $fn=10);
        }
    }
    
    hull()
    for (y = [22.5 + 12.5]){
        for (x = [0, 2.5, 5, 7.5, 10, 12.5]){
            translate([x + 2.5, y + 12.5/2, 0])
            cylinder(t, r0, r0, $fn=10);
        }
    }
}