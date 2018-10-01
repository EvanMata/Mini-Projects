import numpy as np
import matplotlib.pyplot as plt
import math
import random
import time
from mpl_toolkits.mplot3d import Axes3D

'''
Chaos and Nonlinear Dynamics project to do a basic simulation of chaotic
mixing on the surface of a sphere due to two vortices that alternate being
on and off.

Two main functions - drawing a pathline for a single/multiple particles 
to watch how they are mixed (note different input parameters can have vastly
different behaviours), and a scattering function that shows how a blob ends
after a long period of mixing. Again, different parameters have different
regimes of behaviour. The scatter function is computationally intense, so
it can take a long (or very long - as in multiple hours/days) time to run
if too many points are used or too small a time step.
'''


#Fib algo from:
'''
https://stackoverflow.com/questions/9600801/
evenly-distributing-n-points-on-a-sphere
'''
def fibonacci_sphere(samples, randomize):
    '''
    Generate a ~almost~ even distribution of points across a sphere.
    '''
    #randomize is True or a seed val
    rnd = 1.
    if randomize:
        rnd = random.random() * samples
    else:
        random.seed(randomize)
        rnd = random.random() * samples
    points = []
    offset = 2./samples
    increment = math.pi * (3. - math.sqrt(5.));
    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2);
        r = math.sqrt(1 - pow(y,2))
        phi = ((i + rnd) % samples) * increment
        x = math.cos(phi) * r
        z = math.sin(phi) * r
        points.append([x,y,z])
    return points

def into_3(original_list):
    a = []
    b = []
    c = []
    for item in original_list:
        a0 = item[0]
        b0 = item[1]
        c0 = item[2]
        a.append(a0)
        b.append(b0)
        c.append(c0)
    return a, b, c

def into_6(original_list):
    a = []
    b = []
    c = []
    d = []
    e = []
    f = []
    for item in original_list:
        a0 = item[0]
        b0 = item[1]
        c0 = item[2]
        d0 = item[3]
        e0 = item[4]
        f0 = item[5]
        a.append(a0)
        b.append(b0)
        c.append(c0)
        d.append(d0)
        e.append(e0)
        f.append(f0)
    return a, b, c, d, e, f

def basic_votic(vort_vec, num_pts):
    #Create the data for a basic quiver plot.
    vects = []
    sph_pts = fibonacci_sphere(num_pts, 11111)
    for pt in sph_pts:
        vec = u_val(pt, vort_vec, 1) 
        if mag(vec) < 10:
            six_vec = []
            for component in pt:
                six_vec.append(component)
            for component in vec:
                six_vec.append(component)
            vects.append(six_vec)
    return vects

def u_val(pt, vort_vec, direct):
    #Get the magnitude of u. No direction currently included.
    arc_len = 1*angle_between(vort_vec, pt, True) #r of sphere = 1
    vec = 1.0 /(arc_len)
    if direct < 0:
        vec = -vec
    return vec

def mag(vect):
    #Get the mag of a vector.
    tot = 0
    for i in range(len(vect)):
        component = vect[i]
        tot += component**2
    tot = tot**(0.5)
    return tot    

def unit_vector(vector):
    """ Returns the unit vector of the vector. """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2, acute):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    if (acute == True):
        return angle
    else:
        return 2 * np.pi - angle

def map_pt(pt_loc, vort_loc, dt, direct):
    '''
    Takes a pt, rotates it around the vortex (of the given sign in direct)
    by u*dt in the local angle coordinate system.
    '''
    pt_loc = unit_vector(pt_loc)
    vort_loc = unit_vector(vort_loc)
    #first project onto x,y plane
    x_axis = np.array([1, 0, 0])
    y_axis = np.array([0, 1, 0])
    z_axis = np.array([0, 0, 1])
    vort_xy = [vort_loc[0], vort_loc[1], 0]
    acu = True
    if vort_loc[1] < 0:
        acu = False
    #Find all my rotation matrices then rotate my system.
    phi = angle_between(vort_xy, x_axis, acu)
    Ea = Ez(phi)
    EaI = Ez(-phi)
    vort1 = np.matmul(Ea, vort_loc)
    pt1 = np.matmul(Ea, pt_loc)
    theta = angle_between(vort1, z_axis, True)
    Eb = Ey(theta)
    EbI = Ey(-theta)
    pt2 = np.matmul(Eb, pt1)
    #I have my point in my coord sys, now rotate it about z
    #b.c. z is the axis my vort is aligned w/.
    u = u_val(pt_loc, vort_loc, direct) 
    delta_angle = u*dt
    Ec = Ez(delta_angle)
    pt2b = np.matmul(Ec, pt2)
    #Now undo my rotations of the reference frame.
    pt1b = np.matmul(EbI, pt2b)
    ptb = np.matmul(EaI, pt1b)

    return ptb

def to_spherical2(vect):
    x = vect[0]
    y = vect[1]
    z = vect[2]
    XsqPlusYsq = x**2 + y**2
    rho = math.sqrt(XsqPlusYsq + z**2)       
    phi = math.atan2(z, math.sqrt(XsqPlusYsq))
    theta = math.atan2(y, x)                           
    return [rho, theta, phi]

def to_cartesian(vect):
    rho = vect[0]
    theta = vect[1]
    phi = vect[2]
    x = rho*math.sin(phi)*math.cos(theta)
    y = rho*math.sin(phi)*math.sin(theta)
    z = rho*math.cos(phi)
    return [x, y, z]

#Euler angle's.
def Ez(phi):
    E = np.array([[math.cos(phi), math.sin(phi), 0],
                  [-math.sin(phi), math.cos(phi), 0],
                  [0, 0, 1]])
    return E

def Ey(theta):
    E = np.array([[math.cos(theta), 0, -math.sin(theta)],
                 [0, 1, 0],
                 [math.sin(theta), 0, math.cos(theta)]])
    return E

def Ex(psi):
    E = np.array([[1, 0, 0],
                  [0, math.cos(psi), math.sin(psi)],
                  [0, -math.sin(psi), math.cos(psi)]])
    return E

def test_mapping(vort):
    pts = fibonacci_sphere(10, 11111)
    new_pts = []
    for pt in pts:
        new_pt = map_pt(pt, vort, .5, 1)
        new_pts.append(new_pt)
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    a1, b1, c1 = into_3(pts)
    a2, b2, c2 = into_3(new_pts)
    ax.scatter(a1, b1, c1, color = 'b')
    ax.scatter(a2, b2, c2, color = 'r')
    plt.show()    

def patch(n, seed):
    '''
    Generates a patch of points within preset theta & phi bounds.
    Useful to have the exact same patch sometimes, as chaotic dynamics
    makes it so tiny changes can have a huge impact.
    '''
    points = fibonacci_sphere(n, seed)
    patch_pts = []
    for point in points:
        sph_pt = to_spherical2(point)
        theta = sph_pt[1]
        phi = sph_pt[2]
        if theta < 1.2 and theta > 0.8:
            if phi < 1.2 and phi > 0.8:
                if point[0] > 0:
                    patch_pts.append(point)
    return patch_pts

def patch2(n, seed, theta_mi, theta_ma, phi_mi, phi_ma):
    '''
    Generates a patch of points within given theta & phi bounds.
    '''
    points = fibonacci_sphere(n, seed)
    patch_pts = []
    for point in points:
        sph_pt = to_spherical2(point)
        theta = sph_pt[1]
        phi = sph_pt[2]
        if ((theta < theta_ma) and (theta > theta_mi)):
            #print("one pt")
            #print(phi)
            if phi < phi_ma and phi > phi_mi:
                #print("one pt")
                if point[0] > 0:
                    patch_pts.append(point)
    return patch_pts

def patch3(pts, theta_mi, theta_ma, phi_mi, phi_ma):
    '''
    Takes a patch of points and narrows it to be within 
    given theta & phi bounds.
    '''
    points = pts
    patch_pts = []
    for point in points:
        sph_pt = to_spherical2(point)
        theta = sph_pt[1]
        phi = sph_pt[2]
        if ((theta < theta_ma) and (theta > theta_mi)):
            #print("one pt")
            #print(phi)
            if phi < phi_ma and phi > phi_mi:
                #print("one pt")
                if point[0] > 0:
                    patch_pts.append(point)
    return patch_pts

#Could easily combine patch 1, 2, and 3 by using some optional arguements, 
#and if not given then use other things.

def test_patch(n, seed):
    '''
    Makes sure my patch is on the mesh grid.
    '''
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)
    ax.set_aspect("equal")
    pts = patch(n, seed)
    a2, b2, c2 = into_3(pts)
    ax.scatter(a2, b2, c2, color = 'r', zorder = 1)
    ax.plot_wireframe(x, y, z, color="r", zorder = 2)    
    plt.show() 

def arc(vort):
    #Demonstrates that my map does just arc around the vortex.
    pts = fibonacci_sphere(1, 11111)
    new_pts = []
    pt = pts[0]
    for i in range(300):
        pt = map_pt(pt, vort, .005, 1)
        new_pts.append(pt)
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #a1, b1, c1 = into_3(pts)
    a2, b2, c2 = into_3(new_pts)
    #ax.scatter(a1, b1, c1, color = 'b')
    ax.scatter(a2, b2, c2, color = 'r')
    plt.show() 

def path_line(vort1, vort2, init_pt, N, T):
    '''
    Takes a SINGLE point and maps its path around two vortexs, in step size N
    over time T.
    '''
    init_pt = unit_vector(init_pt)
    vort1 = unit_vector(vort1)
    vort2 = unit_vector(vort2)
    #pts = fibonacci_sphere(1, 11111)
    new_pts = [init_pt]
    #pt = pts[0]
    pt = init_pt
    dt = T/10.0
    t = 0
    for i in range(N):
        if (t % 2*T) < T:
            pt = map_pt(pt, vort1, dt, 1)
            new_pts.append(pt)
        else:
            pt = map_pt(pt, vort2, dt, 1)
            new_pts.append(pt)
        t += dt
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #Get rid of the first few points b.c. they don't indiciate long term behaviour.
    new_pts = new_pts[150:]
    a3, b3, c3 = into_3(new_pts)
    vort1 = list(vort1)
    vort2 = list(vort2)
    #Collect the vortex info to graph them.
    a1 = vort1[0]
    b1 = vort1[1]
    c1 = vort1[2]
    a2 = vort2[0]
    b2 = vort2[1]
    c2 = vort2[2]
    xs = [a1, a2]
    ys = [b1, b2]
    zs = [c1, c2]
    #Graph the vortexs, the starting point, then the path taken.
    ax.quiver(xs, ys, zs, xs, ys, zs, pivot = 'tail', linewidth = 3)
    ax.scatter(init_pt[0], init_pt[1], init_pt[2], color = 'c')
    ax.scatter(a3, b3, c3, color = 'r', s = 1)
    
    #Background Sphere data
    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(0, np.pi, 200)
    x = .97 * np.outer(np.cos(u), np.sin(v))
    y = .97 * np.outer(np.sin(u), np.sin(v))
    z = .97 * np.outer(np.ones(np.size(u)), np.cos(v))

    # Plot the surface
    ax.plot_surface(x, y, z, color='palegreen')
    plt.show()


def path_line2(vort1, vort2, init_pts, N, T):
    '''
    Takes a series of points, and effectively opperates path line on all of them.
    '''
    vort1 = unit_vector(vort1)
    vort2 = unit_vector(vort2)
    #pts = fibonacci_sphere(1, 11111)
    new_pts = []
    for i in range(len(init_pts)):
        new_pts.append([])
    dt = T/30.0
    for j in range(len(init_pts)):
        pt = init_pts[j]
        pt = unit_vector(pt)
        t = 0
        new_pts_sublst = new_pts[j]
        for i in range(N):
            if (t % 2*T) < T:
                pt = map_pt(pt, vort1, dt, 1)
                new_pts_sublst.append(pt)
            else:
                pt = map_pt(pt, vort2, dt, 1)
                new_pts_sublst.append(pt)
            t += dt
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for j in range(len(new_pts)):
        sublst = new_pts[j]
        sublst = sublst[150:]
        a3, b3, c3 = into_3(sublst)
        ax.scatter(a3, b3, c3, color = 'r', marker = '.')
    vort1 = list(vort1)
    vort2 = list(vort2)
    #Collect the vortex info to graph them.
    a1 = vort1[0]
    b1 = vort1[1]
    c1 = vort1[2]
    a2 = vort2[0]
    b2 = vort2[1]
    c2 = vort2[2]
    xs = [a1, a2]
    ys = [b1, b2]
    zs = [c1, c2]
    ax.quiver(xs, ys, zs, xs, ys, zs, pivot = 'tail', linewidth = 3)
    #Background Sphere data
    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(0, np.pi, 200)
    x = .97 * np.outer(np.cos(u), np.sin(v))
    y = .97 * np.outer(np.sin(u), np.sin(v))
    z = .97 * np.outer(np.ones(np.size(u)), np.cos(v))

    # Plot the surface
    ax.plot_surface(x, y, z, color='palegreen')
    plt.show()

def scatter(vort1, vort2, pts, N, T):
    '''
    Shows how a blob evolves in time.
    '''
    a = 2.0 #T step size
    start = time.time()
    vx = [vort1[0], vort2[0]]
    vy = [vort1[1], vort2[1]]
    vz = [vort1[2], vort2[2]]
    vxn = [vort1[0]/mag(vort1), vort2[0]/mag(vort2)]
    vyn = [vort1[1]/mag(vort1), vort2[1]/mag(vort2)]
    vzn = [vort1[2]/mag(vort1), vort2[2]/mag(vort2)]
    end_pts = []
    dt = T/a
    M = int(N*a) #number of itterations necessary to do N time cycles.
    #For each point
    for pt in pts:
        #itterate it N times
        c1 = 0
        c2 = 0
        t = 0
        for i in range(M):
            if (t % (2*T)) < T:
                pt = map_pt(pt, vort1, dt, 1)
                c1 += 1
            else:
                pt = map_pt(pt, vort2, dt, 1)
                c2 += 1
            #If its the last point, add it to the map.
            if i == (M - 1):
                end_pts.append(pt)
            t += dt
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    a3, b3, c3 = into_3(end_pts)
    ax.quiver(vxn, vyn, vzn, vx, vy, vz, pivot = 'tail', linewidth = 3)
    ax.set_aspect("equal")
    a2, b2, c2 = into_3(pts)
    ax.scatter(a2, b2, c2, color = 'r', zorder = 1, marker = '.', s = 1)
    #ax.plot_wireframe(x, y, z, color="r", zorder = 2)
    #End pts
    ax.scatter(a3, b3, c3, color = 'b', zorder = 2, marker = '.', s = 1)
    #Background Sphere data
    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(0, np.pi, 200)
    x = .97 * np.outer(np.cos(u), np.sin(v))
    y = .97 * np.outer(np.sin(u), np.sin(v))
    z = .97 * np.outer(np.ones(np.size(u)), np.cos(v))

    # Plot the surface
    ax.plot_surface(x, y, z, color='palegreen')
    end = time.time()
    tot_time = abs(end - start)
    print(tot_time)
    
    plt.show() 

def BetaGamma(B, G):
    '''
    Converts a Beta and Gamma value to two vectors 
    ie used to create my vortexes.
    '''
    v1 = np.array([1, 0, 0])
    v2 = v1*G #G is just a scaling factor
    v1 = v2
    B = B % (2*np.pi) #B is an angle/arclength
    Ea = Ez(-B)
    v2 = np.matmul(Ea, v2)
    return v1, v2

    
v1, v2 = BetaGamma(np.pi/2, 0.5)
#path_line2(v1, v2, [[1, 1, 0], [1, 0, 1], [0, 1, 1], [2, 0, 2]], 2000, 1)
path_line(v1, v2, [1, 1, 0], 10000, 0.05)

'''
#theta min, ma, phi mi, ma
t_mi = 0
t_ma = 0.4
p_ma = np.pi/4 + 0.2
p_mi = np.pi/4 - 0.2

pts = fibonacci_sphere(10000, 22222)
patches = patch2(200000, 22222, t_mi, t_ma, p_mi, p_ma)
scatter(v1, v2, patches, 200, 2)
'''





















        
