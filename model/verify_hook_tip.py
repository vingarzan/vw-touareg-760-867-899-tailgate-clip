"""Check rounded-tip arcs in actual exported STL cross-sections."""
import math
import numpy as np
import trimesh


def verify_tip(path,parameters):
    m=trimesh.load_mesh(path,process=True);mm=parameters['measured'];ee=parameters['estimated']
    ri=mm['hook_cavity']/2;ro=mm['hook_drop_from_mounting_surface']-mm['hook_base_to_nearest_inside']-ri
    theta=math.radians(ee['hook_opening_direction_degrees'])-math.asin(mm['hook_mouth']/(2*ri))
    center=np.array([mm['length']-ro*math.cos(theta),mm['base_wall']-mm['hook_drop_from_mounting_surface']+ro])
    u=np.array([math.cos(theta),math.sin(theta)]);v=np.array([-math.sin(theta),math.cos(theta)])
    results=[]
    for name,R,r,sign in [('outside',ro,ee['hook_free_tip_outer_radius'],-1),('inside',ri,ee['hook_free_tip_inner_radius'],1)]:
        a=math.sqrt(R*R+sign*2*R*r)
        c=center+a*u-r*v
        for y in [-8.,0.,8.]:
            lines=trimesh.intersections.mesh_plane(m,[0,1,0],[0,y,0])
            points=np.unique(np.round(lines[:,:,[0,2]].reshape(-1,2),6),axis=0)
            error=abs(np.linalg.norm(points-c,axis=1)-r)
            near=points[error<.0001]
            # A sharp tip has at most a few accidental intersections here.
            assert len(near)>=30,('tip arc missing',name,y,len(near))
            results.append({'corner':name,'y_mm':y,'radius_mm':r,'arc_points_checked':len(near),'maximum_radial_error_mm':float(error[error<.0001].max())})
    return results
