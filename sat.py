from utils import *
from visual import *
import numpy as np

class AxisVis(frame):
    """Visualize a set of 3d axes as colored perpinecular arrows."""
    def __init__(self,arrowlen,shaftwidth='auto',pos=(0,0,0),standard=True):
        frame.__init__(self)
        if standard:
            x=(arrowlen,0,0)
            y=(0,arrowlen,0)
            z=(0,0,arrowlen)
        self.pos = pos
        if shaftwidth == 'auto':
            shaftwidth = max(arrowlen/100,2e4)
        self.arrows={}
        self.arrows['x'] = arrow(frame=self,axis=x,color=color.green)
        self.arrows['y'] = arrow(frame=self,axis=y,color=color.red)
        self.arrows['z'] = arrow(frame=self,axis=z,color=color.blue)
        for a in self.arrows.values():
            a.shaftwidth = shaftwidth
        #self.axis = (1,0,0) #x axis
    #def set_pos(self,new_pos):
    #    """Moves the arrows to a new position. """
    #    self.pos = new_pos
    #    for obj in self.objects:
    #        obj.pos = self.pos



class SatVis(AxisVis):
    """This is for visualizing the orientation and field of view of a satellite.
        probably a temporary class.? """
    def __init__(self,gain,length,arrowlen,shaftwidth='auto',pos=(0,0,0),standard=True):
        AxisVis.__init__(self,arrowlen,shaftwidth,pos,standard)
        r = np.tan(gain/2) * length
        a = np.asarray(self.arrows['x'].axis)
        a/=mag(a)
        print("A:")
        print(a)
        self.fov_cone=cone(frame=self,length=length,radius=r,axis=-a,opacity=0.2, pos=a*length,color=color.orange,
                        )
        #self.fov_cone = cone(frame=self,pos=self.pos - a * length,length=length,radius=r,axis=a)

class Satellite:
    """Satellite utility class - at the moment I do NOT want this to 'own' an orbit.
        If it can interact with many orbits, it will be more usable for transfer orbits/
        numerical simulated chaotic orbits or whatever"""
    def __init__(self,capacity,orbit,orientation=(1,0,0),timestep=1,
                mass=8,dim=(0.1,0.2,0.3),antenna_gain=0.3):
        self.current_orient = orientation
        self.current_coord = (0,0,0)
        self.efficiency=0.2
        self.area = 0.3 * 0.1 #area of solar panel in square metres
        self.timestep = timestep
        self.antenna_gain = antenna_gain
        self.currently_collecting = False
        self.currently_transmitting = {}#dict to store all locations tras
        self.capacity = capacity
        self.current_battery = capacity
        self.mass = mass #satellite mass in kg
        self.dim = np.asarray(dim)#dimensions of cuboid satellite in metres
        (h,w,d) = self.dim
        #rotational inertia tensor and its inverse for numerical simulation purposes
        #won't be using this for a while...
        self.I = np.zeros(3)
        np.fill_diagonal(self.I, self.mass / 12 * (w**2 + d**2, d**2 + h**2, w**2 + h**2))
        self.I_inverrse = np.inv(self.I)

    def energy_recieved(self,orbit,t):
        """Gives the energy recieved at time t with orbit orbit. Think this should work?"""
        co = orbit.coords_at(t)
        radiance=orbit.radiance_at_coord(orbit.coords_at(t),t)
        sundir = orbit.sun_coords_at(t)
        sat_to_sun = sundir - co
        p = np.dot(np.asarray(sundir),np.asarray(self.current_orient))
        p *= self.efficiency
        p *= self.area
        e = p * self.timestep
        return e

    def energy_used(self,t):
        p = 1 #1 watt intermittent power use
        if self.currently_transmitting != {}:
            p += 5
        if self.currently_collecting:
            p += 3
        e = p * self.timestep
        return e

    def power_balance(self,orbit,t):
        e_in = self.energy_recieved(orbit,t)
        e_out = self.energy_used(t)
        self.current_battery += (e_in - e_out)
        if self.current_battery > self.capacity:
            self.current_battery = self.capacity
        if self.current_battery <= 0:
            raise ValueError("OUT OF BATTERY OH SHIT")
        return e_in, e_out

    def communication_possible(self,coord,t):
        """Determines if the satellite can make contact with a given coord"""
        sat_to_coord = coord - self.current_coord#vector from satellite to coord
        if angle_between(self.current_orient, sat_to_coord) <= self.gain/2:
            if not passes_through_earth(self.current_coord,coord):
                return True
        return False

    def simulate_comms(self,earth,t):
        """ """
        self.currently_transmitting = {}
        for place in earth.labels.keys():
            if self.communication_possible(place,t):
                self.currently_transmitting[key] = earth.labels[key]
