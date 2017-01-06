import numpy as np
from visual import *
#this file is for utilitys/convenience function like newtons method,
#coordinate transforms etc
#SI UNITS FOR EVERYTHING!
global G, pi, EARTH_M, EARTH_r, SUN_TO_EARTH
G = 6.674e-11# gravit. constant in metres cubed per (kilogram second squared)
pi = 3.14159
EARTH_M = 5.972e24#mass of earth
EARTH_r = 6.373e6#radius of earth
SUN_TO_EARTH = 1.478e11 #distance from earth to sun in metres


def random_colour():
    colourdict = {0:color.red,1:color.blue,2:color.orange,3:color.yellow}
    a = np.random.randint(low=0,high=3)
    return colourdict[a]


def mag(vec):
    s=0
    for i in vec:
        s+= i**2
    return np.sqrt(s)


def normalize(vec):
    if isinstance(vec,tuple):
        m=mag(vec)
        for v in vec:
            v = v / m
        return np.asarray(vec)
    else:
        return vec / mag(vec)


def angle_between(v1,v2):
    """Returns the angle between 2 vectors in 3 space."""
    return np.arccos(np.dot(v1,v2)/(mag(v1)*mag(v2)))

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

def spherical_to_cartesian1(coord):
    """Convert spherical coords to cartesian coords.
        Note phi is azimuth, theta is inclination"""
    (r,theta,phi) = coord
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
        if n > 20:
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


def translation_matrix(v):
    """Returns a matrix to translate by a vector v, uses homogeneous coords """
    v.append(1)
    v=np.asarray(v)
    R = np.identity(4)
    R[:,-1] = -1*v
    R[-1,-1] = 1
    return R

def rad(deg):
    qr = lambda x: x * pi / 180
    if isinstance(deg,tuple):
        assert len(deg) == 2
        return (qr(deg[0]),qr(deg[1]))
    return qr(deg)

def deg(rad):
    return rad * 180 / pi

def rotation_matrix(u,theta):
    """Returns a matrix(3x3, not homogeneous coords)
        which represents a rotation of theta radians about
        unit vector u(3 space). UNFINISHED"""
    R = np.ones((3,3)) * (1 - np.cos(theta))
    (l,m,n) = u
    for i in range(3):
        R[i,:] *= u[i]
        R[:,i] *= u[i]
    R += np.identity(3) * np.cos(theta)
    R[1,0] += n * np.sin(theta)
    R[2,0] += - m * np.sin(theta)
    #??? need to add those sin terms/ cross product matrix
    return R

def rotate(vector,axis,angle):
    """Rotates a vector angle radians about axis, all in nonhomogensous coordinates"""
    v=np.matmul(rotation_matrix(axis,angle),vector)
    return tuple(v)


def passes_through_earth(x1,x2):
    """Returns true if a line between coordinates x1 and x2 passes through the earth.
        x1,x2 should be ndarrays. Pretty sure it works.
        see:
        http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html """
    #centre of earth/ is origin
    x0 = np.zeros((3,))
    #make sure we have numpy arrays
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    t = -np.dot((x1 - x0), (x2 - x1))/(mag(x2-x1)**2)
    #If there is a line going from x1 to x2, this gives the...
    # ...minimum distance of this line to the origin/earths center.
    if not(t >= 1 or t < 0):
        return True
    else:
        return False

def random_coordinates(n=20):
    """this just makes a bunch of random spherical coords to plot for funsies """
    coord_dict = {}
    for i in range(n):
        coord=tuple(np.random.randint(low=-360,high=360,size=(2,)))
        coord_dict['coord no {}: {}'.format(i,coord)] = coord
    return coord_dict
