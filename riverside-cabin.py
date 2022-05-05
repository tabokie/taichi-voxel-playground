### Riverside Cabin ###
from scene import Scene;import taichi as ti;from taichi.math import *
night=False;exposure=10.0 if night else 1.2;S=Scene(0,exposure);S.set_floor(-100,(1.0,1.0,1.0))
red_1,red_2=vec3(0.953,0.431,0.38),vec3(0.8,0,0);water=vec3(0,0,0.4)
wo_1,wo_2,wdw=vec3(0.729,0.451,0.286),vec3(0.827,0.753,0.596),vec3(0.961,0.839,0) if night else vec3(0.82,0.9,1)
if night:
    S.set_directional_light((1,1,1),0.2,vec3(0.002,0.002,0.002));S.set_background_color(vec3(0,0,0))
else:
    S.set_directional_light((1,0.7,1),0.2,vec3(1,1,1));S.set_background_color(vec3(0.6,0.8,1.0))
@ti.func
def set(p, mat, c):
    if p.y>=0 and p.y<=64 and p.x>=-64 and p.x<=64 and p.z>=-64 and p.z<=64:
        S.set_voxel(vec3(p.x,-p.y,p.z), mat, c*0.4 + vec3(0,0,c.z*0.3));S.set_voxel(p, mat, c)
@ti.func
def window(dx, dy, off, mat, c):
    for x,y in ti.ndrange(dx,dy):
        if x==0 or x+1==dx or y==0 or y+1==dy: set(vec3(x,y,1)+off, 1, wo_2);set(vec3(x,y,0)+off, 1, wo_2) # Frame
        else: set(vec3(x,y,-1)+off, mat, c); set(vec3(x,y,0)+off, 0, wdw); set(vec3(x,y,1)+off, 0, wdw) # Door
@ti.kernel
def initialize_voxels():
    for p in ti.grouped(ti.ndrange((-54,22),(0,5),(-64,22))): # Land
        if p.z<=22-p.y and p.y == 4: set(p, 1, vec3(0.702, 1, 0.341)*(0.8+ti.random()/5)) # Grass
        elif p.z<=22-p.y and p.y < 2: set(p, 1, vec3(0.173, 0.173, 0.165)/2)
        elif p.z<=22-p.y: set(p, 1, vec3(0.322, 0.322, 0.196))
    h,roof_h,depth,body_depth,fl,cb_1=63,50,60,5,5,vec3(-15,63,-42) # Cabin 1
    for x, y, z in ti.ndrange(64, h, depth):
        if x < y//2.5 and z<=depth-body_depth and z>=body_depth and cb_1.y-y > fl:
            set(vec3(x,-y,z)+cb_1, 1, wo_2);set(vec3(-x,-y,z)+cb_1, 1, wo_2)
        if x <= y//2.5 and y>=h-7 and z<=depth-body_depth+1:
            set(vec3(x,-y,z)+cb_1, 1, wo_2 * 0.7);set(vec3(-x,-y,z)+cb_1, 1, wo_2 * 0.7)
        if x==y//2.5 and y<roof_h:
            set(vec3(x,-y,z)+cb_1, 1, red_1);set(vec3(-x,-y,z)+cb_1, 1, red_1)
    h,off=h*0.5,cb_1+vec3(0,-3,depth-body_depth)
    for x,y in ti.ndrange(64, h): # Window of cabin 1
        if x == y//2.5 or x < y//2.5 and (y+1==h or x==7 or y==int(h*0.6) or x==0): # Frame
            set(vec3(x,-y,1)+off, 1, wo_2);set(vec3(-x,-y,1)+off, 1, wo_2)
            set(vec3(x,-y,0)+off, 1, wo_2);set(vec3(-x,-y,0)+off, 1, wo_2)
        elif x < y//2.5:
            set(vec3(x,-y,0)+off, 0, wdw);set(vec3(-x,-y,0)+off, 0, wdw)
            set(vec3(x,-y,-1)+off, 2 if night else 1, wdw);set(vec3(-x,-y,-1)+off, 2 if night else 1 , wdw)
    h,roof_h,body_w,depth,body_depth,cb_2=45,28,30//2.5-2,35,2,vec3(-8,45,-19) # Cabin 2
    for x, y, z in ti.ndrange(depth, h, roof_h//2.5):
        if z == y//2.5:
            set(vec3(x,-y,z)+cb_2, 1, red_1);set(vec3(x,-y,-z)+cb_2, 1, red_1)
        elif z < y//2.5 and z<=body_w and x<=depth-body_depth and x>=body_depth and cb_2.y-y>fl:
            set(vec3(x,-y,z)+cb_2, 1, wo_2);set(vec3(x,-y,-z)+cb_2, 1, wo_2)
    h,off=10,cb_2+vec3(5,0,-5); # Chimney
    for x,y,z in ti.ndrange(2,(-64,h),2): set(vec3(x,y,z)+off, 1, red_2)
    for t in ti.ndrange(30): # Smoke
        w=t**0.3*(0.75+ti.random()**2/4)
        for p in ti.grouped(ti.ndrange((-w,w),(-w,w),(-w,w))):
            set(vec3(t**1.7/5,ti.sin(float(t)/8)*5+h,-t)+p+off, 1, vec3(1,1,1)*(0.8+ti.random()/4))
    length,r,off=30,3,vec3(22,20,cb_2.z) # Shaft
    for x,y,z in ti.ndrange(length,(-r,r),(-r,r)):
        if y**2+z**2 < r**2: set(vec3(x,y,z)+off, 1, wo_2)
    r,width,off=26,length-9,off+vec3(7,0,0) # Leaves
    for x,y,z in ti.ndrange(width,(-r,r),(-r,r)):
        theta=(ti.cast((ti.atan2(ti.cast(y,ti.f32),ti.cast(z,ti.f32))/3.1415/2+0.3)*12,ti.i32)/12.0-0.3)*3.1415*2.0
        if y**2+z**2<r**2 and (ti.tan(theta)*z-y)**2/(ti.tan(theta)**2+1) < 3: set(vec3(x,y,z)+off, 1, wo_1*0.5)
    r_min,r_max,dist=16,19,width-2 # Side board
    for y,z in ti.ndrange((-r_max,r_max),(-r_max,r_max)):
        if y**2+z**2 < r_max**2 and y**2+z**2>=r_min**2:
            set(vec3(-1,y,z)+off, 1, wo_2);set(vec3(0,y,z)+off, 1, wo_2)
            set(vec3(1,y,z)+off+vec3(dist,0,0), 1, wo_2);set(vec3(2,y,z)+off+vec3(dist,0,0), 1, wo_2)
    h,off=30,off+vec3(0,5-r,r) # Waterfalls
    for x,y in ti.ndrange(width,h):
        t=ti.abs(ti.cast(x,ti.f32)/width-0.5)
        if ti.random() > 1.2*t**0.5+0.05:
            set(vec3(x,y,0)+off, 1, vec3(0.322, 0.682, 0.6)+vec3(1,1,1)*t)
            if y==h-1: set(vec3(x,y,-1)+off, 1, vec3(0.322, 0.682, 0.6)+vec3(1,1,1)*t)
        if ti.random() > 0.87:
            z=(1-t)*16*ti.random()-1
            S.set_voxel(vec3(x+10*ti.random()-5,0 if z<5 else 1,z)+off, 1, vec3(0.322, 0.682, 0.6)*2.5)
    dx,dz,off=10,60,vec3(cb_1.x-5,fl,cb_1.z+55) # Dock
    for x,z in ti.ndrange(dx,dz):
        set(vec3(x,0,z)+off, 1, wo_1)
        if ti.random()>0.9:
            c=wo_1 * (0.5+ti.random()/2)
            for xx,zz in ti.ndrange(ti.min(dx-x, 4),2):set(vec3(x+xx,0,z+zz)+off, 1, c)
    for i in ti.ndrange(3): # Pole
        for p in ti.grouped(ti.ndrange(2,(-10,2),2)):
            set(off+p+vec3(-1,0,(i+1)*15), 1, wo_1*0.5);set(off+p+vec3(dx-1,0,(i+1)*15), 1, wo_1*0.5)
    for x,z in ti.ndrange((cb_1.x-26,cb_1.x+24), (cb_1.z-2,cb_1.z+62)): # Base
        if x % 2 == 0: set(vec3(x,fl,z), 1, wo_1)
    window(dx, 16, off+vec3(0,-1,0), 1, vec3(0.922,0.498,0.388))
    window(10, 7, vec3(cb_2.x+18,10,cb_2.z+10), 2 if night else 1, wdw)
    set(vec3(2,15/2-1,0)+off, 1, red_2); # Door Knob
    y0,z0,r,off=30,-20,int(ti.sqrt(20**2+30**2)),vec3(7,-5,45) # Boat
    for x,y,z in ti.ndrange((-64,64),10,10):
        d=int(ti.sqrt((float(x)*0.8)**2+(y-y0)**2+(z-z0)**2))
        if (d==r and x>-13 or d<=r and x==-13) and y+off.y>=0: # Shell above water
            set(vec3(x,y,z)+off, 1, wo_2);set(vec3(x,y,-z)+off, 1, wo_2)
        elif d==r and y+off.y<0 and x>-13 or d<=r and x==-13: # Shell below water
            S.set_voxel(vec3(x,y,z)+off, 1, wo_2);S.set_voxel(vec3(x,y,-z)+off, 1, wo_2)
        elif d<r and x>11 and y<9: # Intseriora
            set(vec3(x,y,z)+off, 1, wo_2*1.5);set(vec3(x,y,-z)+off, 1, wo_2*1.5)
initialize_voxels();S.finish()
