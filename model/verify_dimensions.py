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


def axis_crossings(mesh,y,origin,direction):
    """Intersect an arbitrary line with the actual exported X/Z section."""
    lines=trimesh.intersections.mesh_plane(mesh,[0,1,0],[0,y,0])
    origin=np.asarray(origin); direction=np.asarray(direction)
    values=[]
    for p,q in lines[:,:,[0,2]]:
        matrix=np.column_stack([direction,p-q])
        if abs(np.linalg.det(matrix))<1e-10:
            continue
        t,s=np.linalg.solve(matrix,p-origin)
        if -1e-8<=s<=1+1e-8:
            values.append(t)
    return np.unique(np.round(values,6))


def check_export(path, parameters):
    m=trimesh.load_mesh(path,process=True)
    measured=parameters['measured']; estimated=parameters['estimated']
    ro=measured['hook_cavity']/2+estimated['hook_shell_wall']
    direction=math.radians(estimated['hook_opening_direction_degrees'])
    ri=measured['hook_cavity']/2
    half=math.asin(measured['hook_mouth']/(2*ri))
    cx=measured['length']-ro*math.cos(direction-half)
    cz=m.bounds[0,2]+ro
    center=np.array([cx,cz])
    outward=np.array([math.cos(direction),math.sin(direction)])
    across=np.array([-math.sin(direction),math.cos(direction)])
    eps=0.0001
    result={}
    fin_start=estimated['peg_center_from_rear']+measured['peg_base_diameter']/2+measured['peg_to_fin_edge_gap_along_length']
    result['hook_drop_from_mounting_surface_mm']=float(measured['base_wall']-m.bounds[0,2])
    assert abs(result['hook_drop_from_mounting_surface_mm']-measured['hook_drop_from_mounting_surface'])<.003
    lip_station=math.sqrt(ri*ri-(measured['hook_mouth']/2)**2)
    for y in [-8.0,0.0,8.0]:
        for name,origin,axis,want in [
            ('hook_cavity_diameter_mm',center,[0,1],measured['hook_cavity']),
            ('hook_mouth_clearance_mm',center+outward*(lip_station+eps),across,measured['hook_mouth'])
        ]:
            ts=axis_crossings(m,y,origin,axis)
            got=float(ts[ts>0].min()-ts[ts<0].max())
            assert abs(got-want)<0.003,(name,y,got,want)
            result[name]=got
        # Prove the entry remains open beyond the lips: these rays would hit
        # any roof, frame, or other host geometry closing the usable mouth.
        for v in np.linspace(-measured['hook_mouth']/2+.05,measured['hook_mouth']/2-.05,17):
            ts=axis_crossings(m,y,center+across*v,outward)
            blocked=ts[ts>lip_station+.003]
            assert len(blocked)==0,('blocked hook entrance',y,float(v),blocked)
    result['unobstructed_entry_rays_checked']=3*17
    # Each rear-link section must have one continuous material interval.
    # These stations crossed the large air gap in v05; checking a single
    # connected 3D solid alone would not detect that gap.
    link_checks=[]
    for y in [-13.5,-8.0,0.0,8.0,13.5]:
        for z in [-0.7,-2.7,-4.7,-6.7]:
            xs=section_crossings(m,y,z)
            assert len(xs)==2,('gap in solid hook back link',y,z,xs)
            assert xs[0]<23.0<xs[1],('back link missing at former gap',y,z,xs)
            link_checks.append({'y_mm':y,'z_mm':z,'solid_x_interval_mm':xs.tolist()})
    result['solid_hook_back_link_sections']=link_checks
    # Check the radial projection and tangential height at both sides and
    # the centre. The tooth must lie on the diameter opposite the mouth.
    rib_results=[]
    for y in [-13.5,0,13.5]:
        ts=axis_crossings(m,y,center,outward)
        tip=float(ts[ts<0].max())
        projection=tip+ri
        assert abs(projection-measured['hook_internal_rib_projection'])<.003
        station=center+outward*(-ri+measured['hook_internal_rib_projection']/2)
        zs=axis_crossings(m,y,station,across)
        height=float(zs[zs>0].min()-zs[zs<0].max())
        assert abs(height-measured['hook_internal_rib_height'])<.003
        offset=float((zs[zs>0].min()+zs[zs<0].max())/2)
        assert abs(offset)<.003,('tooth not opposite mouth',y,offset)
        rib_results.append({'y_mm':y,'height_mm':height,'projection_mm':projection,
                            'tangential_center_offset_mm':offset})
    result['internal_rib_sections']=rib_results
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
            assert abs(xs[0]-fin_start)<0.003
            if where=='base':
                gap=float(xs[0]-(estimated['peg_center_from_rear']+measured['peg_base_diameter']/2))
                assert abs(gap-measured['peg_to_fin_edge_gap_along_length'])<0.003
                spans['peg_to_fin_longitudinal_edge_gap_mm']=gap
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
    lip=m.vertices[(m.vertices[:,0]>measured['length']-.05)]
    result['hook_lip_width_mm']=float(lip[:,1].max()-lip[:,1].min())
    assert abs(result['hook_lip_width_mm']-measured['hook_lip_width'])<.003
    latch=m.vertices[(m.vertices[:,0]>fin_start+11.0)&(m.vertices[:,2]>5)]
    result['latch_width_mm']=float(latch[:,1].max()-latch[:,1].min())
    assert abs(result['latch_width_mm']-measured['latch_width'])<.003
    # The section between ribs must still contain a wall, from the platform
    # to the underside of the latch bar. In v02 these positions were air.
    wall_checks=[]
    for y in [-6.9,-3.0,3.0,6.9]:
        for z in [measured['base_wall']+.2,4.0,5.5]:
            xs=section_crossings(m,y,z)
            xs=xs[(xs>fin_start+7.0)&(xs<fin_start+10.9)]
            assert len(xs)==2,('continuous latch wall',y,z,xs)
            thickness=float(xs[1]-xs[0])
            assert thickness>=estimated['latch_wall_thickness_x']-.003
            wall_checks.append(thickness)
    result['latch_wall_minimum_x_thickness_between_ribs_mm']=min(wall_checks)
    result['tolerance_mm']=0.003
    return result
