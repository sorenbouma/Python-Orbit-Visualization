from orbit import *
from visual import *
from visual.graph import *
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

class AxisVis(frame):
    """Visualize a set of 3d axes as colored perpinecular arrows."""
    def __init__(self,arrowlen,shaftwidth='auto',pos=(0,0,0),standard=True):
        frame.__init__(self)
        if standard:
            x=(arrowlen,0,0)
            y=(0,arrowlen,0)
            z=(0,0,arrowlen)
        self.pos = pos
        shaftwidth = max(arrowlen/100,2e4)
        self.arrows={}
        self.arrows['x'] = arrow(frame=self,axis=x,color=color.green)
        self.arrows['y'] = arrow(frame=self,axis=y,color=color.red)
        self.arrows['z'] = arrow(frame=self,axis=z,color=color.blue)
        for a in self.arrows.values():
            a.shaftwidth = shaftwidth
        #self.axis = (1,0,0) #x axis
    def set_pos(self,new_pos):
        """Moves the arrows to a new position. """
        self.pos = new_pos
        for obj in self.objexts:
            obj.pos = self.pos
class OrbitVisualizer:
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah
            L - width of display in pixels
            H - height of disp;ay in pexels."""
    def __init__(self,orbit,trange,points=None,show_axis=True,L=1260,H=800):
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
        #self.sat = box(pos=self.orbit.r0,size=(1e6,1e6,1e6))
        self.sat = AxisVis(pos=self.orbit.r0,arrowlen=5e5)
        self.satlabel = label(
                pos=self.sat.pos,
                text='Doomsday device',
                box=False,
                opacity=0.07,
                yoffset=20,
                xoffset=20)
        self.trail = curve(pos=self.sat.pos,color=random_colour())
        self.timeslider = wx.Slider(self.window.panel,
            pos=(0.1*self.L,0.9*self.H),
            minValue = 0,
            maxValue = self.trange,
            size=(self.L * 0.9,20))
        self.timeslider.Bind(wx.EVT_SCROLL,self.update)
        self.timeslider.SetValue(0)
        self.battery = wx.Gauge(self.window.panel,
            name='Battery',
            style=wx.GA_HORIZONTAL,
            pos=(0.6*self.L,0.1*self.H),
            size=(self.L/4,20))
        self.battery.SetValue(100)
        #self.batterytitle = wx.StaticText(self.window.panel,-1,'Battery: 100%',pos=(0.6*self.L,0.2*self.L))
        #self.batterytitle = label(pos=(0,0,0),text='testing testing 123')
        if show_axis:
            arrowlen = max(self.orbit.a / 5, EARTH_r * 1.3)
            self.axes = AxisVis(arrowlen)
        self.hide_umbra = wx.Button(self.panel,pos=(0,0),label='Toggle umbra')
        self.hide_umbra.Bind(wx.EVT_BUTTON,self.toggle_umbra)

        self.hide_labels = wx.Button(self.panel,pos=(0,25),label='Toggle Labels')
        self.hide_labels.Bind(wx.EVT_BUTTON,self.toggle_labels)
        self.disp.up=(0,0,1)
        self.disp.userzoom = True
        #self.disp.autoscale = False
        self.disp.autocenter = False
        self.orbit_done = False
        self.get_curve(20)
        self.disp.range=(self.orbit.a*1.9,)*3;self.disp.center = (0,0,0);
        self.umbra = None
        self.show_umbra =  True
        self.set_sundir(0)
        self.comm=None


    def update(self,arg):
        """Update the display based on the value from the time slider """
        rate(100)
        t = arg.GetPosition()
        t = float(t)
        co = self.orbit.t_to_xyz(t)
        self.sat.pos = co
        self.sat.axis = -1*np.asarray(co)
        self.satlabel.pos = co
        #self.trail.append(pos=self.sat.pos)
        self.earth.set_to_time(t)
        b = self.orbit.battery_at(t)

        self.battery.SetValue(b)
        #self.batterytitle.SetLabel("Battery: {:.1f}%".format(b))
        self.set_sundir(t)
        self.satlabel.text = "Radiance: " + str(self.orbit.radiance_at_coord(co,t))
        #self.disp.forward = self.sat.axis
        #self.disp.up = self.sat.arrows['y'].axis
        self.draw_comm_line(co)

    def draw_comm_line(self,co):
        pp=self.earth.labels['auckland'].pos
        if self.comm is not None:
            self.comm.visible = False
        if passes_through_earth(co,pp):
            self.comm = curve(pos=[co,pp],color=color.red)
        else:
            self.comm = curve(pos=[co,pp],color=color.green)

        if self.show_umbra:
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
        self.disp.lights=[self.sunl,self.sunl2]
        umbralength = EARTH_r * SUN_TO_EARTH/(EARTH_r-SUN_r)
        if self.umbra is None:
            self.umbra = cone(pos=(0,0,0),radius=EARTH_r,length=-9*EARTH_r,
                            opacity=0.3,axis=self.sundir, color = color.green)

        self.umbra.axis = self.sundir; self.umbra.length = umbralength

    def toggle_umbra(self,evt):
        """Turn the umbra display` on/off """
        if self.show_umbra:
            self.show_umbra=False
            self.umbra.visible=False
        else:
            self.show_umbra=True
            self.umbra.visible=True
        print(self.show_umbra)

    def toggle_labels(self,evt):
        for x in self.earth.labels.keys():
            self.earth.labels[x].visible = not self.earth.labels[x].visible


#my_vis = OrbitVisualizer(orbit=my_orbit2,trange=3600*24*5)

points = {'random coordxn':(90,90),'target':(90,180),'auckland':(90+36.8,174.76)}

my_orbit = ExtendedOrbit(e=0.1,a=geocentric/4,inclination=-pi/9,ascend_node_long=pi/3,peri=pi/3)
my_vis = OrbitVisualizer(orbit=my_orbit,trange=3600*24,points=points)
