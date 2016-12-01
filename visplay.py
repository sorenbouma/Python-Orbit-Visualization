from orbit import *
from visual import *
geocentric = 42164e3

earth = sphere(material=materials.earth,radius=EARTH_r,)
earth.rotate(angle=pi/2,axis=(0,0,1))
earth.rotate(angle=pi/2,axis=(0,1,0))
ecliptic = box(pos=(0,0,0),size=(20e7,20e7,0.001), opacity= 0.5)
xarrow = arrow(pos=(0,0,0),axis =(geocentric,0,0),color=color.green,shaftwidth=EARTH_r/4)
yarrow = arrow(pos=(0,0,0),axis =(0,geocentric,0),color=color.red,shaftwidth=EARTH_r/5)
zarrow = arrow(pos=(0,0,0),axis =(0,0,geocentric),color=color.blue,shaftwidth=EARTH_r/5)
scene.up=(0,0,1)


def v_circ(r):
    return np.sqrt(G*EARTH_M/r)

v=v_circ(geocentric*2)


my_orbit = EllipticOrbit(r=(geocentric*2,0,0),v=(0,v,0),trange=3600*24,
                    inclination=pi/6)


my_orbit2 = EllipticOrbit(r=(geocentric*2,0,0),v=(0,v,0),trange=3600*24,
        inclination=pi/6,  ascend_node_long=pi/10)


def quickplot(orbit):
    my_sat = box(pos=orbit.r0,size=(2e6,2e6,2e6))
    copy = my_sat
    my_sat.trail=curve(color=color.red)
    for t in range(0,3600*24*5,5):
        (x,y,z) = orbit.t_to_xyz(t)

        my_sat.pos = (x,y,z)
        if t % 3600 == 0:
            pass
            #a=box(pos=my_sat.pos,size=my_sat.size)
        my_sat.trail.append(pos=my_sat.pos)
        #print("current position: {}, {}".format(x,y))


def test_circle():
    my_sat = box(pos=(geocentric,0,0),size=(2e6,2e6,2e6))
    for t in range(3600*24*2):
        rate(10)
        x=geocentric*np.cos( t * 2 * pi / (3600*10) )
        y=geocentric*np.sin( t * 2 * pi / (3600*10) )
        my_sat.pos=(x,y,0)
        print(my_sat.pos)
quickplot(my_orbit)
quickplot(my_orbit2)
