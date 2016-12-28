import numpy as np
from utils import *
from datetime import datetime, timedelta
#SI UNITS FOR EVERYTHING!
global G, pi, EARTH_M, EARTH_r, SUN_TO_EARTH, SUN_r
G = 6.674e-11# gravit. constant in metres cubed per (kilogram second squared)
pi = 3.14159
EARTH_M = 5.972e24#mass of earth
EARTH_r = 6.373e6#radius of earth
SUN_TO_EARTH = 1.478e11 #distance from earth to sun in metres
SUN_r = 6.957e8 #radius of sun


class EllipticOrbit1:
    """Elliptic orbit around the earth..
        """
    def __init__(self,e,a,mu=EARTH_M*G,peri=0,inclination=0,
                    ascend_node_long=0,mean_anomaly=0,trange=3600*24,timestep=1):

        self.mu = mu
        self.e=e
        self.peri = peri # argument of periapsis
        self.a = a
        self.t = np.linspace(0,trange)# whats this for again?
        self.T = 2 * pi * np.sqrt(self.a ** 3 / (mu))
        self.timestep = timestep
        self.inclination = inclination
        self.ascend_node_long = ascend_node_long
        self.mean_anomaly = mean_anomaly
        self.r0 = np.asarray(self.t_to_xyz(0))


    def time_to_tau(self,t):
        """Returns the eccentric anomaly tau for a given time value t
            (seconds).
            Computed with Newton's method.
        """
        t = t % self.T
        f = lambda tau: np.sqrt(self.a ** 3/(self.mu)) \
            * (tau - self.e * np.sin(tau)) - t
        #print("a:{}, mu: {}, e: {}".format(self.a,self.mu,self.e))
        df =  lambda tau: np.sqrt(self.a**3/(self.mu))*(1 - self.e * np.cos(tau))
        tau_guess = pi-0.1#????? how to get sensible time guess??
        tau = newtons_method(f,df,tau_guess)
        return tau

    def tau_to_inclined_coords(self,tau):
        """Returns polar inclined coords from eccentric anomaly tau """
        #if tau == 0:
        #    return self.r0[:-1]
        r =  self.a * (1 - self.e * np.cos(tau))
        phi = np.arctan2(np.sqrt(1-self.e**2)*np.sin(tau),np.cos(tau)-self.e)
        return (r,phi)

    def inclined_to_xyz(self,r_i,phi_i):
        """takes polar coords rotated to the plane of the orbit and returns
            normal cartesian xyz (xy plane on equator)"""
        omegaB,i,w = self.ascend_node_long, self.inclination,self.peri
        x = r_i * (np.cos(omegaB) * np.cos(phi_i + w)\
            - np.sin(omegaB) * np.sin(phi_i + w) \
            * np.cos(i))

        y = r_i * (np.sin(omegaB) * np.cos(phi_i + w)\
            + np.cos(omegaB) * np.sin(phi_i + w) \
            * np.cos(i))

        z = r_i * np.sin(phi_i + w) * np.sin(i)

        return (x,y,z)

    def t_to_xyz(self,t):
        """Returns the xyz coords at a given time in seconds. """
        tau = self.time_to_tau(t)
        (r,phi) = self.tau_to_inclined_coords(tau)
        (x,y,z) = self.inclined_to_xyz(r,phi)
        return (x,y,z)




class Earth:
    """Earth! - Get coords for the rotation of the earth, and points on it! """
    def __init__(self,att_i=0,rotation_axis=(0,0,1),apoints={'test':(0,pi/3)},start_datetime=datetime(2018,1,1)):
            self.rotation_axis = rotation_axis
            self.att_i = att_i #initial angle about rotation axis
            self.apoints = apoints #list of lattitude/longitude pairs
            #these two attributes are for
            self.change_angle = angle_between(rotation_axis,(0,0,1))
            self.change_ax = tuple(np.cross((0,0,1),rotation_axis))
            self.start_datetime = start_datetime
            print(self.apoints)
            if self.apoints is not None:
                for k in self.apoints.keys():
                    p = (EARTH_r,) + rad(self.apoints[k])
                    print("point {} in polar coords: {}".format(k,p))
                    p = spherical_to_cartesian1(p)
                    p = vector(p).rotate(self.change_angle,self.change_ax)
                    print("point {}  in plotting coords: {}".format(k,p))
                    self.apoints[k] = p

    def attitude_at(self,t):
        """Get the angle of the earth at time t (assuming 24 hour days) """
        day = 24*3600 # seconds in a day
        s_today = t - (t // day) * day #number of seconds passed today
        return s_today * 2 * pi / day  #angle

    def point_coords_angle(self,angle,point):
        """ """
        (r,theta,phi) = spherical_to_cartesian1(self.apoints[point])
        phi =  phi - angle
        return spherical_to_cartesian(r,theta,phi)

    def datetime_at(self,t):
        td=timedelta(seconds=t)
        return str(self.start_datetime + td)


class ExtendedOrbit(EllipticOrbit1):
    """Extends the EllipticOrbit class to have utilities that are
        useful but not strictly related to the orbit of the satellite
        These include:
        >formatted date/time at any delta t in seconds
        >battery(will remove soon, should be part of a Satellite class)
        """

    def __init_(self,e,a,mu=EARTH_M*G,peri=0,inclination=0,start_datetime=datetime(2017,1,1),
                    ascend_node_long=0,mean_anomaly=0,timestep=1):
        EllipticOrbit1.__init__(self,e,a,mu,peri,inclination,ascend_node_long,mean_anomaly)
        self.start_datetime = start_datetime

        self.decay_rate = 1 - 1e-5
        self.umbra_length = self.a


    def datetime_at(self,t):
        """Convert seconds passed to time/date """
        td = timedelta(seconds=t)
        return str(self.start_datetime + td)

    def battery_at(self,t):
        """replace this soon """
        return (1-1e-5) ** t * 100

    def sun_coords_at(self,t):
        """Gets the suns coords at time t. Assumes circular orbit because I suck.
            Not yet synced up with the almanac so won't be accurate to date."""
        earthT = 365.25*24*3600 # period of earths orbit in seconds
        x = SUN_TO_EARTH * np.cos(t * 2 * 3.141 / earthT)
        y = SUN_TO_EARTH * np.sin(t * 2 * 3.141 / earthT)
        z = 0.0
        return (x,y,z)

    def radiance_at_coord(self,coord,t):
        """Pretty sure this works properly"""
        #D is the distance from centre of earth to tip of its umbra.
        sundir = np.asarray(self.sun_coords_at(t))
        D = EARTH_r*SUN_TO_EARTH/(SUN_r-EARTH_r)
        #this is like a vector from tip of umbra to centre of earth
        umbra_tip = -D * sundir / mag(sundir)
        #this is a vector from the tip of the umbra to the satellite
        sat_to_tip = umbra_tip + np.asarray(coord)
        #print(np.arccos(sat_to_tip.dot(umbra_tip)/(mag(umbra_tip)*mag(sat_to_tip))))
        a = angle_between(umbra_tip,sat_to_tip)
        max_angle = np.arctan(EARTH_r/D)
        #print("current angle: {}, max angle: {}".format(a,max_angle))
        if passes_through_earth(sundir,coord) and a < max_angle:
            return 0
        else:
            return 1366
