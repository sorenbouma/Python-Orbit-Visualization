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

def plot_orbit(orbit,timestep = 150):
    t = 0
    trail = curve(pos=[orbit.r0],color=random_colour())
    while t <= orbit.T:
        coord = orbit.t_to_xyz(t)
        trail.append(coord)
        t += timestep
    return trail


class OrbitConstructor:
    def __init__(self,frame=None,width=400,height=200):
        self.window = window(width=width, height=height,
           menus=True, title='OWO WHATS THIS?',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        p=self.window.panel
        wx.StaticText(p,pos=(0,15),label="eccentricity:")
        self.e_slider = wx.Slider(p,pos=(0,30),size=(width*0.8,20))
        wx.StaticText(p,pos=(0,45),label="Longitude of ascending node:")

        self.loan_slider = wx.Slider(p,pos=(0,60),size=(width*0.8,20))
        self.a_select = wx.TextCtrl(p,pos=(0,80),size=(width*0.8,20),value="enter semimajor axis")


    def show(self,orbit):
        pass


class EarthVis(Earth):
    """Adds visualization to the Earth class(found in orbit.py)."""
    def __init__(self,att_i,rotation_axis,apoints={'test':(pi/3,pi/5)}):
        Earth.__init__(self,att_i,rotation_axis,apoints)
        self.frame = frame()
        self.orb = sphere(frame=self.frame,material=materials.earth,radius=EARTH_r,)
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
        self.dots = points(frame=self.frame,pos=[(0,0,0)],size=4,color=color.magenta)
        for k in self.apoints.keys():
            self.labels[k] = label(frame=self.frame,pos=self.apoints[k],text=k,xoffset=20,yoffset=0,box=False,height=9)
            self.dots.append(self.apoints[k])
    def set_angle(self,theta):
        """Sets the displayed earths orientation to theta(in radians),
            about the rotation_axis """
        diff = theta - self.att
        self.frame.rotate(angle=diff,axis=self.rotation_axis)
        self.att = theta
        #for k in self.apoints.keys():
        #    self.labels[k].pos = self.labels[k].pos.rotate(diff,self.rotation_axis)

    def set_to_time(self,t):
        """Sets the display to what it should look like at time t(seconds)"""
        theta = self.attitude_at(t)
        self.set_angle(theta)



class CompleteVisualizer:
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah
            L - width of display in pixels
            H - height of disp;ay in pexels."""
    def __init__(self,orbit,trange,apoints=None,show_axis=True,L=1260,H=800,timestep=50):
        self.c = OrbitConstructor()
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
        self.earth = EarthVis(0,rot_axis,apoints=apoints)
        #satellite and whatnot
        self.sat = SatelliteVis(self.orbit,self.earth,timestep=timestep)
        self.trail = plot_orbit(orbit=self.orbit)
        self.timeslider = wx.Slider(self.window.panel,
            pos=(0.1*self.L,0.9*self.H),
            minValue = 0,
            maxValue = self.trange,
            size=(self.L * 0.9,20))
        self.timeslider.Bind(wx.EVT_SCROLL,self.slider_update)
        if show_axis:
            arrowlen = max(self.orbit.a / 5, EARTH_r * 1.3)
            self.axes = AxisVis(arrowlen)
        self.hide_umbra = wx.Button(self.panel,pos=(0,0),label='Toggle umbra')
        self.hide_umbra.Bind(wx.EVT_BUTTON,self.toggle_umbra)
        self.hide_labels = wx.Button(self.panel,pos=(0,25),label='Toggle Labels')
        self.hide_labels.Bind(wx.EVT_BUTTON,self.toggle_labels)

        self.toggle_view = wx.Button(self.panel,pos=(0,75),label="Change view")
        self.toggle_view.Bind(wx.EVT_BUTTON,self.change_view)

        self.animate_button = wx.Button(self.panel,pos=(0,50),label='Animate orbit')
        self.animate_button.Bind(wx.EVT_BUTTON,self.animate)
        self.disp.up=(0,0,1)
        self.orbit_done = False
        self.disp.range=(self.orbit.a*1.9,)*3;self.disp.center = (0,0,0);
        self.umbra = None
        self.set_sundir(0)
        self.comm={}
        self.umbra.visible = False
        self.sat_view = False
        self.toggle_labels()

        self.animate()

    def slider_update(self,arg):
        t = arg.GetPosition()
        self.update(t)

    def update(self,t):
        """Update the display based on the value from the time slider """
        rate(100)
        t = float(t)
        self.earth.set_to_time(t)
        self.set_sundir(t)
        if self.sat_view:
            self.disp.center = -self.sat.current_coord * 1.2
            self.disp.forward = self.sat.current_orient
        if self.orbit_done:
            self.sat.current_coord = self.sat.orbit.t_to_xyz(t)


    def set_sundir(self,t):
        """Sets the direction of the sun/lighting tp where it should be at
            time t. """
        self.sundir = self.orbit.sun_coords_at(t)
        #self.sun.pos = sundir
        self.sunl = distant_light(direction=self.sundir,color=color.white)
        self.sunl2 = distant_light(direction=self.sundir,color=color.white)
        self.disp.lights=[self.sunl,self.sunl2]
        if self.umbra is None:
            self.umbra = cone(pos=(0,0,0),radius=EARTH_r,length=-9*EARTH_r,
                            opacity=0.3,axis=self.sundir, color = color.green)

        self.umbra.axis = self.sundir;

    def toggle_umbra(self,evt):
        """Turn the umbra display` on/off """
        self.umbra.visible = not self.umbra.visible

    def change_view(self,evt):
        self.sat_view = not self.sat_view
        if not self.sat_view:
            self.disp.center = (0,0,0)

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
            sleep(0.0001)
        self.orbit_done = True


v= tuple(np.random.randint(low=0,high=360,size=(2,)))
print(v)

my_points = {'penguins':(180,180),'random coordxn':v,'target':(90,180),'auckland':(90+36.8,174.76),'yurop':(45,21)}
#my_points=random_coordinates(0)
my_orbit = ExtendedOrbit(e=0,a=EARTH_r + 1e6,inclination=1.5,ascend_node_long=rad(174),peri=pi/3)
my_vis = CompleteVisualizer(orbit=my_orbit,trange=3600*2,apoints=my_points,timestep=40)
