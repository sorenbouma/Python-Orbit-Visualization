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



class EarthVis(Earth):
    """Adds visualization to the Earth class(found in orbit.py)."""
    def __init__(self,att_i,rotation_axis,points=None):
        Earth.__init__(self,att_i,rotation_axis,points)
        self.orb = sphere(material=materials.earth,radius=EARTH_r,)
        self.orb.rotate(angle=pi/2,axis=(0,0,1))
        self.orb.rotate(angle=pi/2,axis=(0,1,0))
        #axis to rotate earth about to get initial orient right.
        axv = tuple(np.cross((0,0,1),rotation_axis))
        #angle between z and rotation axis()()
        theta = np.dot((0,0,1),rotation_axis) / (mag((0,0,1)) * mag(rotation_axis))
        theta = np.arccos(theta)
        self.orb.rotate(angle=theta,axis=axv)

        self.att_i = 0
        self.att = self.att_i

    def set_angle(self,theta):
        """Sets the displayed earths orientation to theta(in radians),
            about the rotation_axis """
        diff = theta - self.att
        self.orb.rotate(angle=diff,axis=self.rotation_axis)
        self.att = theta

    def set_to_time(self,t):
        """Sets the display to what it should look like at time t(seconds)"""
        theta = self.attitude_at(t)
        self.set_angle(theta)



class AxisVis:
    """Visualize a set of 3d axes as colored arrows."""
    def __init__(self,arrowlen,center=(0,0,0),standard=True):
        if standard:
            x=(arrowlen,0,0)
            y=(0,arrowlen,0)
            z=(0,0,arrowlen)
        self.center = center
        self.arrows={}
        self.arrows['x'] = arrow(pos=center,axis=x,color=color.green,shaftwidth=arrowlen/100)
        self.arrows['y'] = arrow(pos=center,axis=y,color=color.red,shaftwidth=arrowlen/100)
        self.arrows['z'] = arrow(pos=center,axis=z,color=color.blue,shaftwidth=arrowlen/100)

    def set_pos(self,new_pos):
        """Moves the arrows to a new position. """
        self.center = new_pos
        for arrow in arrow:
            arrow.pos = new_pos




class OrbitVisualizer:
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of EllipticOrbit or ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah"""
    def __init__(self,orbit,trange,show_axis=True):
        self.orbit = orbit
        self.L = 200
        self.Hgraph = 150
        self.trange = trange
        self.window = window(width=1.9*(self.L+window.dwidth), height=self.Hgraph,
           menus=True, title='Satellite Toolkit Controls',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        #earth sphere display
        scene.title='Satellite Toolkit Display'
        rot_axis = (0,1.3*EARTH_r*np.sin(13.1*pi/180),1.3*EARTH_r*np.cos(13.1*pi/180),)
        #for debug
        a = arrow(axis=rot_axis,color=color.white,shaftwidth=EARTH_r/100)
        self.earth = EarthVis(0,rot_axis)
        #satellite display
        self.sat = box(pos=self.orbit.r0,size=(1e6,1e6,1e6))
        self.trail = curve(pos=self.sat.pos,color=color.magenta)


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
            arrowlen = max(self.orbit.a / 5, EARTH_r * 1.3)
            self.axes = AxisVis(arrowlen)
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
        #print(scene.autoscale)
        #print(scene.center, scene.range)

    def update(self,arg):
        """Update the display based on the value from the time slider """
        t = arg.GetPosition()
        t = float(t)
        self.sat.pos = self.orbit.t_to_xyz(t)
        #self.trail.append(pos=self.sat.pos)
        self.earth.set_to_time(t)
        b = self.orbit.battery_at(t)
        self.battery.SetValue(b)
        self.batterytitle.SetLabel("Battery: {:.1f}%".format(b))
        self.set_sundir(t)
        self.umbra.rotate(axis=(0,0,1),angle=0.01)


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
my_vis = OrbitVisualizer(orbit=my_orbit,trange=3600*24)
