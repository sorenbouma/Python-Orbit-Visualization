from orbit import *
from visual import *
from sat import *
from visual.graph import *
import wx
import numpy as np
from datetime import datetime


geocentric = 42164e3



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



def plot_orbit(orbit,disp,timestep = 150):
    t = 0
    trail = curve(disp=disp,pos=[(0,0,0),orbit.r0],color=random_colour())
    T = orbit.T + timestep
    while t <= T:
        coord = orbit.t_to_xyz(t)
        trail.append(coord)
        t += timestep
    return trail


class SatConstructor:
    def __init__(self,visualizer,frame=None,x=500,y=100,width=200,height=300):
        L,H = wx.DisplaySize()
        self.window = window(x=L-width,y=100,width=width, height=height,
            menus=True, title='Adjust Satellite parameters',
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.STAY_ON_TOP | wx.TRANSPARENT_WINDOW)
        p=self.window.panel
        self.window.panel.SetPosition(wx.Point(500,0))
        wx.StaticText(p,pos=(0,0),label="Scanning Camera Field of View")
        p.Center()

        self.cgain_slider = wx.Slider(p,pos=(0,20),minValue=0,maxValue=90,
            size=(width*0.9,40),style=wx.SL_LABELS)
        self.cgain_slider.Bind(wx.EVT_SCROLL,self.adjust_sat)

        wx.StaticText(p,pos=(0,60),label='Comm Antenna Field of View')
        self.gain_slider = wx.Slider(p,pos=(0,100),minValue=0,maxValue=90,
            size=(width*0.9,40),style=wx.SL_LABELS)
        self.gain_slider.Bind(wx.EVT_SCROLL,self.adjust_sat)
        self.vis = visualizer
        self.toggle_collect_button = wx.Button(p,pos=(0,200),label='toggle data collection')
        self.toggle_collect_button.Bind(wx.EVT_BUTTON,self.toggle_collection)
    def adjust_sat(self,evt):
        gain = self.gain_slider.GetValue() * pi / 180
        cgain=self.cgain_slider.GetValue() * pi / 180
        self.vis.sat.set_gain(gain)
        self.vis.sat.set_cam_gain(cgain)
    def toggle_collection(self,evt):
        self.vis.sat.toggle_collection()



class OrbitConstructor(wx.Frame):
    """GUI window that allows user to adjust orbit parameters in real time.
        """
    def __init__(self,visualizer,frame=None,width=200,height=300):
        (L,H) = wx.DisplaySize()
        self.window = window(x=L-width,y=H-height-50,width=width, height=height,
           menus=True, title='Adjust orbit parameters',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        p=self.window.panel
        p.SetPosition((500,0))
        #text entry to set orbit altitude
        wx.StaticText(p,pos=(10,0),label='Orbit altitude (metres):')
        self.a_select = wx.TextCtrl(p,pos=(0,20),size=(width*0.9,20),value="1000000",style=wx.TE_MULTILINE)
        self.a_select.Bind(wx.EVT_TEXT,self.adjust_orbit)
        #slider for inclination
        wx.StaticText(p,pos=(10,40),label="inclination")
        self.i_slider = wx.Slider(p,pos=(0,50),minValue=0,maxValue=90,
                size=(width*0.9,40),style=wx.SL_LABELS)
        self.i_slider.Bind(wx.EVT_SCROLL,self.adjust_orbit)
        #slider for longitude of ascending node
        wx.StaticText(p,pos=(10,80),label="Long. of ascending node")
        self.loan_slider = wx.Slider(p,pos=(0,100),size=(width*0.9,40),
                                        minValue=0,maxValue=360,style=wx.SL_LABELS)
        self.loan_slider.Bind(wx.EVT_SCROLL,self.adjust_orbit)
        #slider for Eccentricity
        wx.StaticText(p,pos=(10,140),label="Eccentricity(%)")
        self.e_slider = wx.Slider(p,pos=(0,160),minValue=0,maxValue=100,
                size=(width*0.9,40),style=wx.SL_LABELS)
        self.e_slider.Bind(wx.EVT_SCROLL,self.adjust_orbit)
        #slider for argument of periapsis
        wx.StaticText(p,pos=(10,200),label="Arg. of Periapsis")
        self.p_slider = wx.Slider(p,pos=(0,220),minValue=0,maxValue=360,
                size=(width*0.9,40),style=wx.SL_LABELS)
        self.p_slider.Bind(wx.EVT_SCROLL,self.adjust_orbit)

        self.disp = visualizer.disp
        self.visualizer = visualizer
        self.orbit = None
        self.trail = plot_orbit(self.visualizer.orbit,self.disp)

    def adjust_orbit(self,evt):
        """When user adjusts orbit parameters, adjust the orbit of the
            CompleteVisualizer class """
        a=float(self.a_select.GetValue()) + EARTH_r
        e=self.e_slider.GetValue() / 100.0
        i = self.i_slider.GetValue() / 90.0 * pi / 2
        loan=self.loan_slider.GetValue() * pi / 180.0
        p = self.p_slider.GetValue() * pi / 180.0
        orbit=ExtendedOrbit(e,a,ascend_node_long=loan,inclination=i,peri=p)

        self.trail.visible = False

        self.trail=plot_orbit(orbit,self.disp,timestep = orbit.T / 50.0)
        #self.disp.range = (orbit.a*1.3,)*3
        self.visualizer.set_orbit(orbit)

    def bring_to_front(self,evt=None):
        print("Called bring to front")
        #self.window.panel.ToggleWindowStyle(wx.STAY_ON_TOP)


class PointAdder:
    def __init(self,visualizer):
        pass
        self.window = window(x=500,y=500,width=100,height=100,style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        p=self.window.panel
        self.visualizer=visualizer
        self.ok = wx.Button(p,pos=(0,50),label='ok')
        self.lat_entry=wx.TextCtrl(p,pos=(0,0))


class CompleteVisualizer(wx.Frame):
    """Class for visualizing 3d orbit around earth, using the ExtendedOrbit class.
        Parameters:
        -----------
            orbit - instance of ExtendedOrbit class
            trange - int, how many seconds of time to simulate
            show_axis - bool, display axis vectors or nah
            L - width of display in pixels
            H - height of disp;ay in pexels.
            """
    def __init__(self,trange,apoints=None,show_axis=True,timestep=50):
        self.trange = trange
        L,H=wx.DisplaySize()
        self.L = L
        self.H = H
        self.window = window(width=self.L, height=self.H,
           menus=True, title='Python Satellite Toolkit',
           style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.panel = self.window.panel
        self.frame = wx.Frame.__init__(self, self.panel, -1, 'Hello',wx.DefaultPosition,(400,500),style=  wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        #earth sphere display
        sidewidth = 100
        self.disp = display(window=self.window,x=sidewidth,y=0,height=self.H-80,width=self.L-sidewidth)
        self.orbit = ExtendedOrbit(e=0,a=EARTH_r+1e6)
        self.orbit_con = OrbitConstructor(self)
        rot_axis = vector(0,0,EARTH_r).rotate(rad(23),(0,1,0))
        self.earth = EarthVis(0,rot_axis,apoints=apoints)
        #satellite and whatnot
        self.sat = SatelliteVis(self.orbit,self.earth,timestep=timestep)
        self.sat_con= SatConstructor(self)
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
        self.disp.forward = (-1,-1,-1)
        self.orbit_done = False
        self.disp.range=(self.orbit.a*1.9,)*3;self.disp.center = (0,0,0);
        self.umbra = None
        self.set_sundir(0)
        self.comm={}
        #self.umbra.visible = False
        self.sat_view = False
        self.toggle_labels()
        self.umbra.visible=False
        #self.animate()

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
            self.disp.center = -self.sat.current_coord * 1
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


    def set_orbit(self,new_orbit):
        self.orbit = new_orbit
        self.sat.set_orbit(new_orbit)
        self.disp.range=(self.orbit.a*1.9,)*3

    def animate(self,evt=None):
        """animates the orbit for trange timesteps."""
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

my_points = {'los angeles':(90-34,360-118),'penguins':(180,180),
'random coordxn':v,'Pacific OCean':(90,180),'Auckland':(90+36.8,174.76),'yurop':(45,21)}
#my_points=random_coordinates(0)
my_vis = CompleteVisualizer(trange=3600*24,apoints=my_points,timestep=40)
