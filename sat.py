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


class SatVis(AxisVis):
    """This is for visualizing the orientation and field of view of a satellite.
        probably a temporary class.? """
    def __init__(self,gain,length,arrowlen,shaftwidth='auto',pos=(0,0,0),standard=True):
        AxisVis.__init__(self,arrowlen,shaftwidth,pos,standard)
        r = np.tan(gain/2) * length
        a = np.asarray(self.arrows['x'].axis)
        a/=mag(a)
        self.fov_cone=cone(frame=self,length=length,radius=r,axis=-a,opacity=0.2, pos=a*length,color=color.orange,
                        )
        #self.fov_cone = cone(frame=self,pos=self.pos - a * length,length=length,radius=r,axis=a)

class Satellite(object):
    """Satellite utility class"""
    def __init__(self,orbit,earth,capacity=35400.0,orientation=(1,0,0),timestep=1,
                mass=8,dim=(0.1,0.2,0.3),antenna_gain=1.5):
        self.orbit = orbit
        self.earth = earth
        self.t = 0
        self.current_orient = orientation
        self.current_coord = self.orbit.r0
        self.spanel_offset = np.asarray((-1,0,1))
        self.efficiency = 0.21
        self.area = 0.3 * 0.1 #area of solar panel in square metres
        self.timestep = timestep
        self.antenna_gain = antenna_gain
        self.currently_collecting = True
        self.currently_transmitting = {}#dict to store all locations tras
        self.capacity = capacity
        self.current_battery = capacity
        self.mass = mass #satellite mass in kg
        self.dim = np.asarray(dim)#dimensions of cuboid satellite in metres


    def energy_recieved(self):
        """Gives the energy recieved at time t with orbit orbit. Think this should work?"""
        radiance = self.orbit.radiance_at_coord(self.current_coord,self.t)
        sundir=self.orbit.sun_coords_at(self.t)
        sat_to_sun = sundir - self.current_coord
        solar_orient = self.current_orient + self.spanel_offset
        p = np.dot(sundir,solar_orient)/(mag(sundir)*mag(solar_orient))
        #p = np.cos(angle_between(sundir,solar_orient))
        #p=1
        p=abs(p)
        p*= radiance
        #print("dot product:{}".format(p))
        p *= self.efficiency
        p *= self.area
        #print("final power:"+str(p))
        e = p * self.timestep
        return e

    def energy_used(self):
        p = 4 #1 watt intermittent power use
        if self.currently_transmitting != {}:
            p += 5
        if self.currently_collecting:
            p += 3
        e = p * self.timestep
        return e

    def power_balance(self):
        self.e_in = self.energy_recieved()

        self.e_out = self.energy_used()
        #print("e_in: {}, e_out: {}".format(self.e_in,self.e_out))
        self.current_battery += (self.e_in - self.e_out)
        #print(self.current_battery)
        if self.current_battery > self.capacity:
            self.current_battery = self.capacity
        if self.current_battery <= 0:
            print("OUT OF BATTERY")
            pass

    def communication_possible(self,coord):
        """Determines if the satellite can make contact with a given coord"""

        sat_to_coord = np.asarray(coord) - self.current_coord#vector from satellite to coord
        if angle_between(self.current_orient, sat_to_coord) <= self.antenna_gain/2:
            if not passes_through_earth(self.current_coord,coord):
                return True
        return False

    def simulate_comms(self):
        """simulate_comms """
        self.currently_transmitting = {}
        for place in self.earth.labels.keys():
            place_coord = self.earth.frame.frame_to_world(self.earth.labels[place].pos)
            if self.communication_possible(place_coord):
                self.currently_transmitting[place] = place_coord

    def perform_timestep(self):
        """do one timestep and update the satellite's state. """
        self.current_coord = np.asarray(self.orbit.t_to_xyz(self.t))
        self.simulate_comms()
        #TEMPORARY - REPLACE WITH POLICY SETTER SOON.
        #(this just always points to earth's center)
        self.current_orient = np.asarray(self.current_coord) * -1
        self.power_balance()
        self.t += self.timestep

class SatelliteVis(Satellite):
    def __init__(self,orbit,earth,capacity=35400,orientation=(1,0,0),timestep=1,
                mass=8,dim=(0.1,0.2,0.3),antenna_gain=1.5):
        Satellite.__init__(self,orbit,earth,capacity,orientation,timestep,mass,dim,antenna_gain)
        self.vis = SatVis(length=5e6,gain=self.antenna_gain,pos=self.orbit.r0,arrowlen=5e5)
        self.comm_lines = {}
        self.display_string = "Ready for use"
        self.hud = label(pos=(0,0,0),xoffset=-310,yoffset=100,text=self.display_string,line=False)
        self.e_in=0
        self.e_out=0

    def perform_timestep(self):
        super(SatelliteVis,self).perform_timestep()
        self.vis.pos = self.current_coord
        self.vis.axis = self.current_orient
        #delete any lines from other timesteps
        #draw line from satellite to any points making communication
        for line in self.comm_lines.values():
            line.visible=False

        for place in self.currently_transmitting.keys():
            place_coord = self.currently_transmitting[place]
            self.comm_lines[place] = curve(pos=[self.current_coord, place_coord],
                                            color=color.cyan)
        self.hud.text = self.get_display_string()

    def get_display_string(self):
        disp_string = 'Date/time: ' + str(self.earth.datetime_at(self.t))
        disp_string += "\nBattery: {:.1f}%".format(self.current_battery/self.capacity * 100)
        disp_string += "\nPower in: {:.1f} W".format(self.e_in/self.timestep)
        disp_string += "\nPower used: {} W".format(self.e_out / self.timestep)

        if self.currently_transmitting == {}:
            disp_string += "\nNo communication with earth."
        else:
            disp_string += "\nTransmitting data to points:"
            for place in self.currently_transmitting.keys():
                disp_string += "\n  " + place

        return disp_string
