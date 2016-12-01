import numpy as np
from utils import *
from datetime import datetime
#SI UNITS FOR EVERYTHING!
global G, pi, EARTH_M, EARTH_r, SUN_TO_EARTH, SUN_r
G = 6.674e-11# gravit. constant in metres cubed per (kilogram second squared)
pi = 3.14159
EARTH_M = 5.972e24#mass of earth
EARTH_r = 6.373e6#radius of earth
SUN_TO_EARTH = 1.478e11 #distance from earth to sun in metres
SUN_r = 6.957e8 #radius of sun

#TESTING FOR GIT - THIS SHOULD ONLY BE IN MODULAR_EARTH BRANCH

class EllipticOrbitOLD:
    """Elliptic orbit around the earth..
        >gets geocentric orbit right(e=0)
        Makes really weird bean shaped orbit sometimes? not sure what's wrong
        with it.. could be because I'm picking initial coord/v that won't
        correspond to a stable elliptic orbit??"""
    def __init__(self,r,v,trange,mu=EARTH_M*G,inclination=0,
                    ascend_node_long=0,mean_anomaly=0):
        self.r0 = r # initial position, geocentric cartesian coords
        self.v0 = v # initial velocity, geocentric cartesian coords
        self.h = np.cross(r,v)# specific angular momentum
        #specific orbital energy, stays constant
        self.e_specific = mag(self.v0) ** 2 / 2 - (mu)/mag(self.r0)
        self.mu = mu

        #a: length of semimajor axis of orbit ellpse
        self.a = -mu / (self.e_specific*2)
        self.t = np.linspace(0,trange)# whats this for again?
        #eccentricity
        self.e = np.sqrt(1 + 2*self.e_specific*mag(self.h)**2 / (self.mu)**2)#eccentricity
        #period of orbit
        self.T = 2 * pi * np.sqrt(self.a ** 3 / (mu))
        self.inclination = inclination
        self.ascend_node_long = ascend_node_long
        self.mean_anomaly = mean_anomaly

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
        if tau == 0:
            return self.r0[:-1]
        r =  self.a * (1 - self.e * np.cos(tau))
        phi = np.arctan2(np.sqrt(1-self.e**2)*np.sin(tau),np.cos(tau-self.e))
        return (r,phi)

    def inclined_to_xyz(self,r_i,phi_i):
        """takes polar coords rotated to the plane of the orbit and returns
            normal cartesian xyz (xy plane on equator)"""
        omegaB,i = self.ascend_node_long, self.inclination
        x = r_i * (np.cos(omegaB) * np.cos(phi_i)\
            - np.sin(omegaB) * np.sin(phi_i) \
            * np.cos(i))

        y = r_i * (np.sin(omegaB) * np.cos(phi_i )\
            + np.cos(omegaB) * np.sin(phi_i ) \
            * np.cos(i))

        z = r_i * np.sin(phi_i) * np.sin(i)

        return(x,y,z)

    def t_to_xyz(self,t):
        """Returns the xyz coords at a given time in seconds. """
        tau = self.time_to_tau(t)
        (r,phi) = self.tau_to_inclined_coords(tau)
        (x,y,z) = self.inclined_to_xyz(r,phi)
        return (x,y,z)


class EllipticOrbit1:
    """Elliptic orbit around the earth..
        """
    def __init__(self,e,a,mu=EARTH_M*G,peri=0,inclination=0,
                    ascend_node_long=0,mean_anomaly=0,trange=3600*24):

        self.mu = mu
        self.e=e
        self.peri = peri
        self.a = a
        self.t = np.linspace(0,trange)# whats this for again?
        self.T = 2 * pi * np.sqrt(self.a ** 3 / (mu))
        self.inclination = inclination
        self.ascend_node_long = ascend_node_long
        self.mean_anomaly = mean_anomaly
        self.r0 = self.t_to_xyz(0)


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

        return(x,y,z)

    def t_to_xyz(self,t):
        """Returns the xyz coords at a given time in seconds. """
        tau = self.time_to_tau(t)
        (r,phi) = self.tau_to_inclined_coords(tau)
        (x,y,z) = self.inclined_to_xyz(r,phi)
        return (x,y,z)



class ExtendedOrbit(EllipticOrbit1):
    """Extends the EllipticOrbit class to have utilities that are
        useful but not strictly related to the orbit of the satellite
        These include:
        >formatted date/time at any delta t in seconds
        >earth rotation
        >battery(will remove soon)
        """

    def __init_(self,e,a,mu=EARTH_M*G,peri=0,inclination=0,start_datetime=datetime(2017,1,1),
                    ascend_node_long=0,mean_anomaly=0 ):
        EllipticOrbit1.__init__(self,e,a,mu,peri,inclination,ascend_node_long,mean_anomaly)
        self.start_datetime = start_datetime

        self.decay_rate = 1 - 1e-5
        self.umbra_length = self.a

    def earth_attitude_at(self,t):
        """Get the angle of the earth at time t (assuming 24 hour days) """
        day = 24*3600 # seconds in a day
        s_today = t - (t // day) * day #number of seconds passed today
        return s_today * 2 * pi / day  #angle

    def datetime_at(self,t):
        """Convert seconds passed to time/date """
        td = timedelta(seconds=t)
        return str(self.start_datetime + td)

    def battery_at(self,t):
        return (1-1e-5) ** t * 100

    def sun_coords_at(self,t):
        earthT = 365.25*24*3600
        x = SUN_TO_EARTH * np.cos(t * 2 * 3.141 / earthT)
        y = SUN_TO_EARTH * np.sin(t * 2 * 3.141 / earthT)
        z = 0.0
        return (x,y,z)

    def radiance_at_coord(self,coord):
        (x,y,z) = coord

        pass
