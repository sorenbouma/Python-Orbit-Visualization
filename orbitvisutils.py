from orbit import *
from visual import *
from visual.graph import *
import wx
import numpy as np
from datetime import datetime
geocentric = 42164e3

def v_circ(r):
    return np.sqrt(G*EARTH_M/r)

v = v_circ(geocentric*2)

#my_orbit2 = ExtendedOrbit(r=(geocentric*2,0,0),v=(0,v,0),trange=3600*24,
#        inclination=pi/6,  ascend_node_long=pi/10)


class OrbitVisualizer:
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of EllipticOrbit or ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah"""
    def __init__(self,orbit,trange,show_axis=True):
        self.orbit = orbit
        self.L=100
        self.Hgraph = 50
        self.trange = trange
        #earth sphere display
        scene.title='Satellite Toolkit Display'

        self.earth = sphere(material=materials.earth,radius=EARTH_r,)
        self.earth.rotate(angle=pi/2,axis=(0,0,1))
        self.earth.rotate(angle=pi/2,axis=(0,1,0))
        self.earth_angle = 0
        #satellite display
        self.sat = box(pos=self.orbit.r0,size=(1e6,1e6,1e6))
        self.trail = curve(pos=self.sat.pos,color=color.magenta)
        self.window = window(width=2*(self.L+window.dwidth), height=200,
           menus=True, title='Satellite Toolkit Controls',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.timeslider = wx.Slider(self.window.panel,
            pos=(0.6*self.L,0.8*self.L),
            minValue = 0,
             maxValue = self.trange,
             size=(self.L,20))
        self.timeslider.Bind(wx.EVT_SCROLL,self.update)
        self.timeslider.SetValue(0)
        self.battery = wx.Gauge(self.window.panel,
            name='Battery',
            pos=(0.6*self.L,0.4*self.L),
            size=(self.L,20))
        self.battery.SetValue(100)
        self.batterytitle = wx.StaticText(self.window.panel,-1,'Battery: 100%',pos=(0.6*self.L,0.1*self.L))
        if show_axis:
            self.make_axes()
        scene.up=(0,0,1)
        scene.userzoom = True
        scene.autoscale = False
        scene.autocenter = False
        self.orbit_done = False
        self.get_curve(20)
        scene.range=(1e7,1e7,1e7);scene.center = (0,0,0);
        self.umbra = None
        self.set_sundir(0)
        #sun = sphere(pos=self.sundir,radius=EARTH_r,color=color.yellow)
        print(scene.autoscale)
        print(scene.center, scene.range)

    def update(self,arg):
        """Update the display based on the value from the time slider """
        t = arg.GetPosition()
        t = float(t)
        self.sat.pos = self.orbit.t_to_xyz(t)
        #self.trail.append(pos=self.sat.pos)
        self.set_earth(self.orbit.earth_attitude_at(t))
        b = self.orbit.battery_at(t)
        self.battery.SetValue(b)
        self.batterytitle.SetLabel("Battery: {:.1f}%".format(b))
        self.set_sundir(t)
        self.umbra.rotate(axis=(0,0,1),angle=0.01)

    def set_earth(self,theta):
        """Sets the displayed earths orientation to theta(in radians) """
        diff = theta - self.earth_angle
        a = 23.1 #
        polar_axis = (-np.sin(a),0,-np.cos(a))
        self.earth.rotate(angle=diff,axis=(0,0,1))
        self.earth_angle = theta


    def get_curve(self,resolution=20):
        """Plot a curve of the satellites orbit. """
        t=0
        while not self.orbit_done:
            self.sat.pos = self.orbit.t_to_xyz(t)
            self.trail.append(pos=self.sat.pos)
            t+=resolution
            if t >= self.orbit.T:
                break
                self.orbit_done = True

    def make_axes(self):
        """Puts arrows to represent xyz axes on display.
            green=x,red=y,blue=z"""
        arrowlen = max(self.orbit.a / 5, EARTH_r * 1.3)
        x=(arrowlen,0,0)
        y=(0,arrowlen,0)
        z=(0,0,arrowlen)
        self.xarrow = arrow(pos=(0,0,0),axis=x,color=color.green,shaftwidth=arrowlen/100)
        self.yarrow = arrow(pos=(0,0,0),axis=y,color=color.red,shaftwidth=arrowlen/100)
        self.zarrow = arrow(pos=(0,0,0),axis=z,color=color.blue,shaftwidth=arrowlen/100)
        #self.polarvec = arrow(axis=(-arrowlen*np.sin(23.1),0,-arrowlen*np.cos(23.1)),shaftwidth=arrowlen/100)

    def set_sundir(self,t):
        """Sets the direction of the sun/lighting tp where it should be at
            time t. """
        self.sundir = self.orbit.sun_coords_at(t)
        #self.sun.pos = sundir
        self.sunl = distant_light(direction=self.sundir,color=color.white)
        self.sunl2 = distant_light(direction=self.sundir,color=color.white)
        scene.lights=[self.sunl,self.sunl2]

        umbralength = EARTH_r * SUN_TO_EARTH/(EARTH_r-SUN_r)
        umbralength = -9*EARTH_r
        if self.umbra is None:
            self.umbra = cone(pos=(0,0,0),radius=EARTH_r,length=umbralength,
                            opacity=0.1,axis=self.sundir, color = color.white)
        self.umbra.axis = self.sundir; self.umbra.length = umbralength


#my_vis = OrbitVisualizer(orbit=my_orbit2,trange=3600*24*5)
my_orbit = ExtendedOrbit(e=0.3,a=geocentric/4,inclination=pi/4,ascend_node_long=pi/3,peri=pi/3)
my_vis = OrbitVisualizer(orbit=my_orbit,trange=3600*24*365)
