import numpy as np
#this file is for utilitys/convenience function like newtons method,
#coordinate transforms etc
#SI UNITS FOR EVERYTHING!
global G, pi, EARTH_M, EARTH_r, SUN_TO_EARTH
G = 6.674e-11# gravit. constant in metres cubed per (kilogram second squared)
pi = 3.14159
EARTH_M = 5.972e24#mass of earth
EARTH_r = 6.373e6#radius of earth
SUN_TO_EARTH = 1.478e11 #distance from earth to sun in metres


def mag(vec):
    s=0
    for i in vec:
        s+= i**2
    return np.sqrt(s)

def polar_to_cartesian(r,phi):
    return (r*np.cos(phi),r*np.sin(phi))

def cartesian_to_spherical(x,y,z):
    """Convert cartesian coords to spherical coords.
        Note phi is azimuth, theta is inclination"""
    r = np.sqrt(x**2+y**2 +z**2)
    theta = np.arccos(z/r)
    phi = np.arctan(y/x)
    return(r,theta,phi)

def spherical_to_cartesian(r,theta,phi):
    """Convert spherical coords to cartesian coords.
        Note phi is azimuth, theta is inclination"""
    z = r * np.cos(theta)
    x =  r * np.sin(theta) * np.cos(phi)
    y =  r * np.sin(theta) * np.sin(phi)
    return (x,y,z)

def newtons_method(f,dfdx,x0,epsilon=1e-3):
    """run newtons method on f with inital guess x0 until it converges
        to the root"""
    x=x0
    converged=False
    x_prev = None
    n=0
    while not converged:
        x_prev = x
        #print(dfdx(x).shape)
        n+=1
        if n > 100:
            break
        if np.abs(dfdx(x)) < 1e-5:
            print("WARNING: small second derivative,newtons method might be unstable")
        x = x - f(x)/dfdx(x)
        #print("residual:{}".format(f(x)))
        if abs(f(x)) <= epsilon:
            #print("converged")
            converged = True
    return x


def inclined_to_3d(xi,yi,i):
    """For an orbit with inclination i, changes coordinates from
        cartesian in the planet of the orbit to standard"""
    raise NotImplementedError()
