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
    ro=measured['hook_drop_from_mounting_surface']-measured['hook_base_to_nearest_inside']-measured['hook_cavity']/2
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
    nearest_checks=[]
    for y in [-8.,0.,8.]:
        vertical=axis_crossings(m,y,center,[0,1])
        nearest_inside_z=cz+float(vertical[vertical>0].min())
        gap=measured['base_wall']-nearest_inside_z
        assert abs(gap-measured['hook_base_to_nearest_inside'])<.003,('incorrect base-to-inside distance',y,gap)
        nearest_checks.append({'y_mm':y,'mounting_face_to_nearest_inside_mm':gap})
    result['hook_base_to_nearest_inside_sections']=nearest_checks
    lip_station=math.sqrt(ri*ri-(measured['hook_mouth']/2)**2)
    for y in [-8.0,0.0,8.0]:
        for name,origin,axis,want in [
            ('hook_cavity_diameter_mm',center,[0,1],measured['hook_cavity']),
            ('hook_mouth_clearance_mm',center+outward*(lip_station+eps),across,measured['hook_mouth'])
        ]:
            ts=axis_crossings(m,y,origin,axis)
            got=float(ts[ts>0].min()-ts[ts<0].max())
            if name=='hook_mouth_clearance_mm':
                assert want-.003<=got<=want+.103,(name,y,got,want)
            else:
                assert abs(got-want)<.003,(name,y,got,want)
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
    side=measured['body_width']/2-.3
    for y in [-side,-8.0,0.0,8.0,side]:
        for z in [-0.7,-2.7,-4.7,-6.7]:
            xs=section_crossings(m,y,z)
            assert len(xs)==2,('gap in solid hook back link',y,z,xs)
            assert xs[0]<23.0<xs[1],('back link missing at former gap',y,z,xs)
            link_checks.append({'y_mm':y,'z_mm':z,'solid_x_interval_mm':xs.tolist()})
    result['solid_hook_back_link_sections']=link_checks
    below=m.vertices[m.vertices[:,2]<-.001]
    below_width=float(below[:,1].max()-below[:,1].min())
    assert below_width<=measured['body_width']+.003,('protruding lateral hook support',below_width)
    result['hook_support_max_width_below_base_mm']=below_width
    # Include the front crossbar ABOVE the underside; v09's check below Z=0
    # could not detect the remaining 0.65 mm lateral tabs at the base edge.
    actual_width=float(m.bounds[1,1]-m.bounds[0,1])
    assert abs(actual_width-measured['body_width'])<.003,('base-side tabs remain',actual_width)
    rail_widths=[]
    rail_x=fin_start+estimated['frame_end_from_fin_start']-.1
    for z in [.1,1.25,2.4]:
        lines=trimesh.intersections.mesh_plane(m,[1,0,0],[rail_x,0,0])
        ys=[]
        for a,b in lines:
            if abs(b[2]-a[2])<1e-10:continue
            t=(z-a[2])/(b[2]-a[2])
            if -1e-8<=t<=1+1e-8:ys.append(a[1]+t*(b[1]-a[1]))
        width=max(ys)-min(ys)
        assert abs(width-measured['body_width'])<.003,('crossbar not flush',z,width)
        rail_widths.append({'z_mm':z,'width_mm':float(width)})
    result['flush_front_crossbar_sections']=rail_widths

    shoulder_checks=[]
    shoulder=fin_start+estimated['frame_end_from_fin_start']-.2
    end=measured['length']-1.2
    for x in [30.4,31.0,31.6,32.2]:
        lines=trimesh.intersections.mesh_plane(m,[1,0,0],[x,0,0]);ys=[]
        for a,b in lines:
            if abs(b[2]-a[2])<1e-10:continue
            t=(-15-a[2])/(b[2]-a[2])
            if -1e-8<=t<=1+1e-8:ys.append(a[1]+t*(b[1]-a[1]))
        width=max(ys)-min(ys)
        wanted=measured['hook_lip_width']+(measured['body_width']-measured['hook_lip_width'])*(.5+.5*math.cos(math.pi*(x-shoulder)/(end-shoulder)))
        assert abs(width-wanted)<.003,('hook shoulder not curved',x,width,wanted)
        shoulder_checks.append({'x_mm':x,'z_mm':-15,'width_mm':width})
    result['rounded_hook_shoulder_sections']=shoulder_checks
    upper=[float(section_crossings(m,0,z).max()) for z in [-1.,-2.,-3.,-4.]]
    assert upper[0]-upper[-1]>.4,('upper hook still has straight vertical end',upper)
    assert np.ptp(np.diff(upper))>.02,('upper hook still has planar angled cut',upper)
    result['curved_upper_hook_end_x_at_z_minus_1_2_3_4_mm']=upper

    # Check the actual rear outline against the tangent line, then ensure
    # that no old support corner projects past the circular lower surface.
    p=np.array([estimated['back_link_start_x'],estimated['back_link_top_z']])
    w=p-center;d2=float(w@w);perp=np.array([-w[1],w[0]])
    choices=[center+(ro*ro/d2)*w+sign*ro*math.sqrt(d2-ro*ro)/d2*perp for sign in [-1,1]]
    q=min(choices,key=lambda point:point[0])
    for y in [-side,0,side]:
        for z in [-1.0,-3.0,-6.0,-9.0]:
            xs=section_crossings(m,y,z)
            wanted=p[0]+(z-p[1])*(q[0]-p[0])/(q[1]-p[1])
            if parameters['construction'].get('flat_support_variant'):
                # The rear base has rounded plan-view corners: near its sides,
                # the footprint starts forward of the rear-centre tangent plane.
                r=estimated['rear_corner_radius']
                dy=max(abs(y)-(measured['body_width']/2-r),0)
                rear_limit=r-math.sqrt(max(r*r-dy*dy,0)) if dy else 0
                wanted=max(wanted,rear_limit)

            assert abs(xs.min()-wanted)<.003,('non-flush backing profile',y,z,xs.min(),wanted)
    low=m.vertices[m.vertices[:,2]<q[1]-.05]
    low_radii=np.linalg.norm(low[:,[0,2]]-center,axis=1)
    assert low_radii.max()<=ro+.003,('support bump outside hook diameter',low_radii.max(),ro)
    result['back_link_tangent_point_xz_mm']=q.tolist()
    result['maximum_lower_hook_radius_mm']=float(low_radii.max())
    # Check the radial projection and tangential height at both sides and
    # the centre. The tooth must lie on the diameter opposite the mouth.
    rib_results=[]
    for y in [-side,0,side]:
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
        c=measured['guide_outside_width']/2-measured['fin_thickness']/2
        z0=measured['base_wall'];h=measured[side+'_fin_height_above_surface']
        base=measured[side+'_fin_base_length'];top=measured[side+'_fin_top_length']
        radius=estimated['fin_tip_radius'];lean=math.tan(math.radians(estimated['fin_inward_lean_degrees']))
        # Original measured lengths describe the unrounded design envelope.
        corner_angle=math.acos(-(base-top)/math.hypot(base-top,h))
        tangent=radius/math.tan(corner_angle/2)
        spans={'unrounded_top_envelope_length_mm':top}
        for name,dz in [('base',eps),('top',h-eps),('rounded_tip',h-.05)]:
            z=z0+dz;y=sign*(c-dz*lean)
            xs=section_crossings(m,y,z)
            assert len(xs)==2,(side,name,xs)
            span=float(xs[-1]-xs[0])
            if name=='base':
                want=base-(base-top)*dz/h
                rear=fin_start
                gap=float(xs[0]-(estimated['peg_center_from_rear']+measured['peg_base_diameter']/2))
                assert abs(gap-measured['peg_to_fin_edge_gap_along_length'])<.003
                spans['peg_to_fin_longitudinal_edge_gap_mm']=gap
            else:
                delta=h-dz
                cap=math.sqrt(2*radius*delta-delta*delta)
                want=top-radius-tangent+2*cap
                rear=fin_start+radius-cap
            assert abs(span-want)<.003,(side,name,span,want)
            assert abs(xs[0]-rear)<.003,(side,name,'rear tip radius')
            spans[name+'_length_mm']=span
        # Measure width and centre at three heights, independent of the shear.
        lines=trimesh.intersections.mesh_plane(m,[1,0,0],[fin_start+2,0,0])
        lean_checks=[]
        for dz in [.1,h/2,h-.1]:
            ys=[]
            for a,b in lines:
                if abs(b[2]-a[2])<1e-10:continue
                t=(z0+dz-a[2])/(b[2]-a[2])
                if -1e-8<=t<=1+1e-8:
                    y=a[1]+t*(b[1]-a[1])
                    if sign*y>9:ys.append(y)
            width=max(ys)-min(ys);center=(max(ys)+min(ys))/2
            assert abs(width-measured['fin_thickness'])<.003
            assert abs(center-sign*(c-dz*lean))<.003
            lean_checks.append({'height_above_surface_mm':dz,'center_y_mm':center,'thickness_mm':width})
        points=m.vertices[(sign*m.vertices[:,1]>9)&(m.vertices[:,2]>z0+.001)]
        got_h=float(points[:,2].max()-z0)
        assert abs(got_h-h)<.003
        spans['height_above_surface_mm']=got_h
        spans['tip_inward_offset_mm']=h*lean
        spans['lean_sections']=lean_checks
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
    lip=m.vertices[(m.vertices[:,0]>m.bounds[1,0]-.05)]
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
    result['peg_root_reinforcement']=check_peg_roots(m,measured,estimated)
    from verify_hook_tip import verify_tip
    result['rounded_free_tip_arcs']=verify_tip(path,parameters)
    result['tolerance_mm']=0.003
    return result


def check_peg_roots(mesh,measured,estimated):
    checks=[]
    floor=estimated['peg_slot_root_z'];height=estimated['peg_root_collar_height']
    r0=estimated['peg_root_inner_radius'];r1=estimated['peg_inner_diameter']/2
    for angle in [45,135]:
        section_mesh=mesh.copy()
        section_mesh.apply_translation([-estimated['peg_center_from_rear'],0,0])
        section_mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-angle),[0,0,1]))
        for z in [floor+.05,floor+.5,floor+height-.05,floor+height+.2]:
            xs=axis_crossings(section_mesh,0,[0,z],[1,0])
            radius=float((xs[xs>0].min()-xs[xs<0].max())/2)
            wanted=r0+(r1-r0)*min((z-floor)/height,1)
            assert abs(radius-wanted)<.003,('missing inside peg collar',angle,z,radius,wanted)
            checks.append({'section_degrees':angle,'z_mm':z,'inner_radius_mm':radius})
    slot_radius=estimated['peg_slot_width']/2
    rounded_checks=[]
    for angle in [0,90]:
        section_mesh=mesh.copy()
        section_mesh.apply_translation([-estimated['peg_center_from_rear'],0,0])
        section_mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-angle),[0,0,1]))
        for y in [-.45,-.25,0,.25,.45]:
            zs=axis_crossings(section_mesh,y,[3.0,0],[0,1])
            wanted=estimated['peg_slot_round_center_z']-math.sqrt(slot_radius*slot_radius-y*y)
            top=float(zs.max())
            assert abs(top-wanted)<.003,('peg slot root is not rounded',angle,y,top,wanted)
            rounded_checks.append({'slot_degrees':angle,'offset_mm':y,'bottom_z_mm':top})
    return {'collar_sections':checks,'rounded_slot_sections':rounded_checks,
            'physical_strength_verified':False}
