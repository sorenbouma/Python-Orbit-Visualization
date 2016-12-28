from orbit import *
from visual import *
from visual.graph import *
from sat import *

import wx
import numpy as np
from datetime import datetime
import sys

sys.setrecursionlimit(99999)

geocentric = 42164e3

def v_circ(r):
    return np.sqrt(G*EARTH_M/r)

v = v_circ(geocentric*2)

#my_orbit2 = ExtendedOrbit(r=(geocentric*2,0,0),v=(0,v,0),trange=3600*24,
#        inclination=pi/6,  ascend_node_long=pi/10)



class EarthVis(Earth):
    """Adds visualization to the Earth class(found in orbit.py)."""
    def __init__(self,att_i,rotation_axis,points={'test':(pi/3,pi/5)}):
        Earth.__init__(self,att_i,rotation_axis,points)
        
        self.orb = sphere(material=materials.earth,radius=EARTH_r,)
        self.orb.rotate(angle=pi/2,axis=(0,0,1))
        self.orb.rotate(angle=pi/2,axis=(0,1,0))
        #axis to rotate earth about to get initial orient right.
        axv = tuple(np.cross((0,0,1),rotation_axis))
        axv = self.change_ax
        #angle between z and rotation axis()()
        #theta = np.dot((0,0,1),rotation_axis) / (mag((0,0,1)) * mag(rotation_axis))
        #theta = np.arccos(theta)
        self.orb.rotate(angle=self.change_angle,axis=self.change_ax)
        self.att_i = 0
        self.att = self.att_i
        self.labels={}
        for k in self.points.keys():
            self.labels[k] = label(pos=self.points[k],text=k,xoffset=20,yoffset=0,box=False,height=9)

    def set_angle(self,theta):
        """Sets the displayed earths orientation to theta(in radians),
            about the rotation_axis """
        diff = theta - self.att
        self.orb.rotate(angle=diff,axis=self.rotation_axis)
        self.att = theta
        for k in self.points.keys():
            self.labels[k].pos = self.labels[k].pos.rotate(diff,self.rotation_axis)

    def set_to_time(self,t):
        """Sets the display to what it should look like at time t(seconds)"""
        theta = self.attitude_at(t)
        self.set_angle(theta)


def plot_orbit(orbit,timestep = 150):
    t = 0
    trail = curve(pos=[orbit.r0])
    while t <= orbit.T:
        coord = orbit.t_to_xyz(t)
        trail.append(coord)
        t += timestep
    return trail



class CompleteVisualizer:
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah
            L - width of display in pixels
            H - height of disp;ay in pexels."""
    def __init__(self,orbit,trange,points=None,show_axis=True,L=1260,H=800,timestep=50):
        self.orbit = orbit
        self.L = L
        self.H = H
        self.trange = trange
        self.window = window(width=self.L, height=self.H,
           menus=True, title='Satellite Toolkit Controls!',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        self.panel = self.window.panel
        #earth sphere display
        sidewidth = 100
        self.disp = display(window=self.window,x=sidewidth,y=0,height=self.H-80,width=self.L-sidewidth)
        rot_axis = vector(0,0,EARTH_r).rotate(rad(23),(0,1,0))
        #for debug
        a = arrow(axis=rot_axis,color=color.white,shaftwidth=EARTH_r/100)
        self.earth = EarthVis(0,rot_axis,points=points)
        #satellite display
        #self.sat = AxisVis(pos=self.orbit.r0,arrowlen=5e5)
        #self.sat = SatVis(length=5e6,gain=1.6,pos=self.orbit.r0,arrowlen=5e5)
        self.sat = SatelliteVis(self.orbit,self.earth,timestep=timestep)

        self.trail = plot_orbit(orbit=self.orbit)
        self.timeslider = wx.Slider(self.window.panel,
            pos=(0.1*self.L,0.9*self.H),
            minValue = 0,
            maxValue = self.trange,
            size=(self.L * 0.9,20))
        self.timeslider.Bind(wx.EVT_SCROLL,self.slider_update)
        self.battery = wx.Gauge(self.window.panel,
            name='Battery',
            style=wx.GA_HORIZONTAL,
            pos=(0.6*self.L,0.1*self.H),
            size=(self.L/4,20))
        self.battery.SetValue(100)
        self.batterytitle = wx.StaticText(self.window.panel,-1,'Battery: 100%',pos=(0.02*self.L,0.2*self.L))
        self.batterytitle.SetForegroundColour((255,0,0))
        self.batterytitle.SetBackgroundColour((0,0,255))

        #self.batterytitle = label(pos=(0,0,0),text='testing testing 123')
        if show_axis:
            arrowlen = max(self.orbit.a / 5, EARTH_r * 1.3)
            self.axes = AxisVis(arrowlen)
        self.hide_umbra = wx.Button(self.panel,pos=(0,0),label='Toggle umbra')
        self.hide_umbra.Bind(wx.EVT_BUTTON,self.toggle_umbra)


        self.hide_labels = wx.Button(self.panel,pos=(0,25),label='Toggle Labels')
        self.hide_labels.Bind(wx.EVT_BUTTON,self.toggle_labels)

        self.animate_button = wx.Button(self.panel,pos=(0,50),label='Animate orbit')
        self.animate_button.Bind(wx.EVT_BUTTON,self.animate)
        self.disp.up=(0,0,1)
        self.disp.autocenter = False
        self.orbit_done = False
        self.disp.range=(self.orbit.a*1.9,)*3;self.disp.center = (0,0,0);
        self.umbra = None
        self.set_sundir(0)
        self.comm={}
        self.umbra.visible = False
        self.toggle_labels()
        self.animate()

    def slider_update(self,arg):
        t = arg.GetPosition()
        self.update(t)

    def update(self,t):
        """Update the display based on the value from the time slider """
        rate(100)
        t = float(t)
        #co = self.orbit.t_to_xyz(t)
        #self.sat.pos = co
        #self.sat.axis = -1 * np.asarray(co)
        #self.satlabel.pos = co
        #self.trail.append(pos=self.sat.pos)
        self.earth.set_to_time(t)
        #b = self.orbit.battery_at(t)

        #self.battery.SetValue(b)
        #self.batterytitle.SetLabel("Battery: {:.1f}%".format(b))
        self.set_sundir(t)
        #self.disp.forward = self.sat.axis
        #self.disp.up = self.sat.arrows['y'].axis
        #self.draw_comm_lines(co)
        #self.hud.text = "Current date/time: {}".format(self.earth.datetime_at(t))

    def draw_comm_lines(self,co):
        """Should delete this soon. """
        for place in self.earth.labels.keys():
            if place in self.comm.keys():
                self.comm[place].visible = False
                del self.comm[place]
            place_coord = self.earth.labels[place].pos
            if not passes_through_earth(co,place_coord):
                self.comm[place] = curve(pos=[co, place_coord],color=color.green)

    def set_sundir(self,t):
        """Sets the direction of the sun/lighting tp where it should be at
            time t. """
        self.sundir = self.orbit.sun_coords_at(t)
        #self.sun.pos = sundir
        self.sunl = distant_light(direction=self.sundir,color=color.white)
        self.sunl2 = distant_light(direction=self.sundir,color=color.white)
        self.disp.lights=[self.sunl,self.sunl2]
        umbralength = EARTH_r * SUN_TO_EARTH/(EARTH_r-SUN_r)
        if self.umbra is None:
            self.umbra = cone(pos=(0,0,0),radius=EARTH_r,length=-9*EARTH_r,
                            opacity=0.3,axis=self.sundir, color = color.green)

        self.umbra.axis = self.sundir; self.umbra.length = umbralength

    def toggle_umbra(self,evt):
        """Turn the umbra display` on/off """
        self.umbra.visible = not self.umbra.visible

    def toggle_labels(self,evt=None):
        """Turn the comm point labels on/off """
        for x in self.earth.labels.keys():
            self.earth.labels[x].visible = not self.earth.labels[x].visible

    def animate(self,evt=None):
        """Replace soon. """
        print('animating')
        t = 0
        while t < self.trange:
            self.sat.perform_timestep()
            self.update(self.sat.t)
            t += self.sat.timestep



v= tuple(np.random.randint(low=0,high=360,size=(2,)))
print(v)

#points = {'random coordxn':v,'target':(90,180),'auckland':(90+36.8,174.76),'yurop':(45,21)}
points=random_coordinates(100)
my_orbit = ExtendedOrbit(e=0.01,a=EARTH_r + 1e6,inclination=1.5,ascend_node_long=pi/3,peri=pi/3)
my_vis = CompleteVisualizer(orbit=my_orbit,trange=3600*24*5,points=points,timestep=10)
