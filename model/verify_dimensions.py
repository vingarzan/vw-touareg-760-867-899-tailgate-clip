"""Measure exported STL sections independently of the CSG construction."""
import math
import numpy as np
import trimesh


def section_crossings(mesh, y, z):
    lines = trimesh.intersections.mesh_plane(
        mesh, plane_normal=[0,1,0], plane_origin=[0,y,0])
    values=[]
    for p,q in lines:
        if abs(q[2]-p[2]) < 1e-10:
            continue
        t=(z-p[2])/(q[2]-p[2])
        if -1e-8 <= t <= 1+1e-8:
            values.append(p[0]+t*(q[0]-p[0]))
    return np.unique(np.round(values,6))


def check_export(path, parameters):
    m=trimesh.load_mesh(path,process=True)
    measured=parameters['measured']; estimated=parameters['estimated']
    ro=measured['hook_cavity']/2+measured['hook_wall']
    cx=measured['length']-ro
    cz=m.bounds[0,2]+ro
    ri=measured['hook_cavity']/2
    angle=math.acos(measured['hook_mouth']/(2*ri))
    eps=0.0001
    result={}
    for name,z,want in [
        ('hook_cavity_horizontal_mm',cz,measured['hook_cavity']),
        ('hook_mouth_horizontal_mm',cz+ri*math.sin(angle)-eps,measured['hook_mouth'])
    ]:
        xs=section_crossings(m,0,z)
        got=float(xs[xs>cx].min()-xs[xs<cx].max())
        assert abs(got-want)<0.003,(name,got,want)
        result[name]=got
    for side,sign in [('right',-1),('left',1)]:
        y=sign*(measured['guide_outside_width']/2-measured['fin_thickness']/2)
        z0=measured['base_wall']
        h=measured[side+'_fin_height_above_surface']
        spans={}
        for where,z in [('base',z0+eps),('top',z0+h-eps)]:
            xs=section_crossings(m,y,z)
            assert len(xs)==2,(side,where,xs)
            span=float(xs[-1]-xs[0])
            want=measured[side+'_fin_'+('base_length' if where=='base' else 'top_length')]
            assert abs(span-want)<0.003,(side,where,span,want)
            spans[where+'_length_mm']=span
            # Both top and bottom must have the same vertical rear edge.
            assert abs(xs[0]-estimated['fin_rear_edge_from_peg_end'])<0.003
        points=m.vertices[(sign*m.vertices[:,1]>measured['guide_outside_width']/2-measured['fin_thickness']-.001)
                           & (m.vertices[:,2]>z0+.001)]
        got_h=float(points[:,2].max()-z0)
        assert abs(got_h-h)<0.003,(side,got_h,h)
        spans['height_above_surface_mm']=got_h
        spans['thickness_mm']=float(points[:,1].max()-points[:,1].min())
        assert abs(spans['thickness_mm']-measured['fin_thickness'])<0.003
        result[side+'_fin']=spans
    peg_points=m.vertices[(abs(m.vertices[:,0]-estimated['peg_center_from_rear'])<5)
                          & (abs(m.vertices[:,1])<5)
                          & (m.vertices[:,2]>measured['base_wall'])]
    result['peg_total_height_mm']=float(peg_points[:,2].max())
    assert abs(result['peg_total_height_mm']-measured['peg_total_height_including_wall'])<0.003
    # Horizontal mesh sections around the peg, excluding other features.
    def peg_radius_at(z):
        lines=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,z])
        pts=lines.reshape(-1,3)
        radii=np.linalg.norm(pts[:,:2]-[estimated['peg_center_from_rear'],0],axis=1)
        pts=pts[radii<measured['peg_barb_diameter']/2+.05]
        return float(np.linalg.norm(pts[:,:2]-[estimated['peg_center_from_rear'],0],axis=1).max())
    result['peg_base_diameter_mm']=2*peg_radius_at(measured['base_wall']+.1)
    result['peg_barb_diameter_mm']=2*peg_radius_at(estimated['peg_barb_shoulder_z']+eps)
    assert abs(result['peg_base_diameter_mm']-measured['peg_base_diameter'])<0.003
    assert abs(result['peg_barb_diameter_mm']-measured['peg_barb_diameter'])<0.003
    lip=m.vertices[(m.vertices[:,0]>cx+3)&(m.vertices[:,2]>cz+ro*math.sin(angle)-.05)]
    result['hook_lip_width_mm']=float(lip[:,1].max()-lip[:,1].min())
    assert abs(result['hook_lip_width_mm']-measured['hook_lip_width'])<.003
    latch=m.vertices[(m.vertices[:,0]>20.5)&(m.vertices[:,2]>5)]
    result['latch_width_mm']=float(latch[:,1].max()-latch[:,1].min())
    assert abs(result['latch_width_mm']-measured['latch_width'])<.003
    result['tolerance_mm']=0.003
    return result
