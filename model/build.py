#!/usr/bin/env python3
"""Reconstruct a measured, but untested, tailgate clip. All lengths are mm.

Run from any working directory: python model/build.py
Uses polygonal CSG with Manifold. This is a dimensioned reconstruction, not
photogrammetry; see parameters.json for measured and estimated dimensions.
"""
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
import numpy as np
import manifold3d as mf
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from verify_dimensions import check_export
from render_hook_section import render_section

P = json.loads((ROOT / 'model' / 'parameters.json').read_text())
M, E = P['measured'], P['estimated']
OUT = ROOT / 'stl'
PREVIEW = ROOT / 'previews'
CHECKS = ROOT / 'validation'
for d in (OUT, PREVIEW, CHECKS):
    d.mkdir(exist_ok=True)


def section(points):
    a = np.array(points, dtype=float)
    signed = np.sum(a[:, 0] * np.roll(a[:, 1], -1) - a[:, 1] * np.roll(a[:, 0], -1))
    if signed < 0:
        a = a[::-1]
    return mf.CrossSection([a])


def xz(points, width, center_y=0):
    # (u,v,w) -> (X,-Y,Z), right-handed; extrusion axis becomes -Y.
    cs=points if isinstance(points,mf.CrossSection) else section(points)
    return cs.extrude(width).transform([
        [1, 0, 0, 0], [0, 0, -1, center_y + width / 2], [0, 1, 0, 0]
    ])


def rear_plan_mask():
    w=M['body_width']/2;r=E['rear_corner_radius']
    plan=arc(r,-w+r,r,180,270,40)+[[40,-w],[40,w],[r,w]]
    plan+=arc(r,w-r,r,90,180,40)
    return section(plan).extrude(60).translate([0,0,-30])


def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1-x0, y1-y0, z1-z0]).translate([x0, y0, z0])


def arc(cx, cy, radius, a0, a1, count=80):
    ts = np.linspace(math.radians(a0), math.radians(a1), count)
    return np.column_stack([cx + radius*np.cos(ts), cy + radius*np.sin(ts)]).tolist()


def rounded_base():
    w, r = M['body_width']/2, E['rear_corner_radius']
    end = fin_start_x() + E['base_front_from_fin_start']
    # Large radii only at the rear peg end; small corners on the frame end.
    points = arc(r, -w+r, r, 180, 270, 40)
    points += [[end-0.7, -w]]
    points += arc(end-0.7, -w+0.7, 0.7, 270, 360, 12)
    points += arc(end-0.7, w-0.7, 0.7, 0, 90, 12)
    points += [[r, w]]
    points += arc(r, w-r, r, 90, 180, 40)
    return section(points).extrude(M['base_wall'])


def back_link_tangent(cx,cz,ro):
    p=np.array([E['back_link_start_x'],E['back_link_top_z']])
    center=np.array([cx,cz]);w=p-center;d2=float(w@w)
    assert d2>ro*ro
    a=ro*ro/d2;b=ro*math.sqrt(d2-ro*ro)/d2
    perp=np.array([-w[1],w[0]])
    choices=[center+a*w+b*perp,center+a*w-b*perp]
    q=min(choices,key=lambda t:t[0])
    return p,q


def hook_profile():
    ri = M['hook_cavity']/2
    ro = M['hook_drop_from_mounting_surface'] - M['hook_base_to_nearest_inside'] - ri
    direction = E['hook_opening_direction_degrees']
    half_opening = math.degrees(math.asin(M['hook_mouth']/(2*ri)))
    start, end = direction+half_opening, direction-half_opening+360
    # The free outer lip, not a removed rightmost circle quadrant, determines
    # the part's measured length with this diagonally outward-facing mouth.
    cx = M['length'] - ro*math.cos(math.radians(end))
    bottom = M['base_wall'] - M['hook_drop_from_mounting_surface']
    cz = bottom + ro
    # Add cardinal extrema explicitly so the mesh bounds preserve measured size.
    cardinals=[t for t in [0.,90.,180.,270.,360.] if start<=t<=end]
    _,tangent=back_link_tangent(cx,cz,ro)
    tangent_angle=math.degrees(math.atan2(tangent[1]-cz,tangent[0]-cx))%360
    angles = np.unique(np.r_[np.linspace(start,end,201),cardinals,tangent_angle])
    outer = [[cx+ro*math.cos(math.radians(t)), cz+ro*math.sin(math.radians(t))] for t in angles]
    inner = [[cx+ri*math.cos(math.radians(t)), cz+ri*math.sin(math.radians(t))] for t in angles[::-1]]
    return outer+inner, (cx, cz, ri, ro, half_opening)


def hook_entry_void(cx,cz,ri):
    # U points out of the diagonal mouth; V measures its 8.1 mm clear width.
    d=math.radians(E['hook_opening_direction_degrees'])
    u=np.array([math.cos(d),math.sin(d)])
    v=np.array([-math.sin(d),math.cos(d)])
    h=M['hook_mouth']/2
    start=math.sqrt(ri*ri-h*h)-0.0001
    points=[np.array([cx,cz])+u*a+v*b for a,b in [(start,-h),(40,-h),(40,h),(start,h)]]
    return xz(points,40)


def hook_envelope():
    # Smooth shoulders replace the planar diagonal cuts below the base.
    w,lip=M['body_width']/2,M['hook_lip_width']/2
    shoulder=fin_start_x()+E['frame_end_from_fin_start']-.2
    end=M['length']-1.2
    x=np.linspace(shoulder,end,101)
    widths=lip+(w-lip)*(.5+.5*np.cos(np.linspace(0,math.pi,101)))
    plan=[[-2,-w]]+[[xx,-yy] for xx,yy in zip(x,widths)]+[[36,-lip],[36,lip]]
    plan+=[[xx,yy] for xx,yy in zip(x[::-1],widths[::-1])]+[[-2,w]]
    lower=section(plan).extrude(20).translate([0,0,-20])
    # Keep the mounting platform and its front crossbar sharp and flush.
    return lower+box(-2,36,-w,w,0,20)


def round_fin_end(points,radius):
    result=[]
    for i,b in enumerate(np.asarray(points,dtype=float)):
        if i not in [3,4]:
            result.append(b);continue
        a=np.asarray(points[i-1]);c=np.asarray(points[(i+1)%len(points)])
        u=(a-b)/np.linalg.norm(a-b);v=(c-b)/np.linalg.norm(c-b)
        half=math.acos(float(np.clip(u@v,-1,1)))/2
        tangent=radius/math.tan(half)
        center=b+(u+v)/np.linalg.norm(u+v)*radius/math.sin(half)
        first=b+u*tangent;last=b+v*tangent
        start=math.atan2(*(first-center)[::-1]);end=math.atan2(*(last-center)[::-1])
        while end<start:end+=2*math.pi
        result.extend(center+radius*np.c_[np.cos(np.linspace(start,end,161)),np.sin(np.linspace(start,end,161))])
    return result


def peg():
    x = E['peg_center_from_rear']
    z0 = M['base_wall'] - 0.20
    shoulder = E['peg_barb_shoulder_z']
    top = M['peg_total_height_including_wall']
    root = M['peg_base_diameter']/2
    barb = M['peg_barb_diameter']/2
    tip = E['peg_tip_diameter']/2
    stem = mf.Manifold.cylinder(shoulder-z0, root, root, 144).translate([x,0,z0])
    # Abrupt lower retaining shoulder with a tapered insertion face above.
    head = mf.Manifold.cylinder(top-shoulder, barb, tip, 144).translate([x,0,shoulder])
    p = stem + head
    slot_z = E['peg_slot_root_z']
    collar_height=E['peg_root_collar_height']
    inner_radius=E['peg_inner_diameter']/2
    inner_root=mf.Manifold.cylinder(collar_height,E['peg_root_inner_radius'],
                                   inner_radius,144).translate([x,0,slot_z])
    inner_upper=mf.Manifold.cylinder(top-slot_z-collar_height+1,inner_radius,
                                    inner_radius,144).translate([x,0,slot_z+collar_height])
    inner=inner_root+inner_upper
    s = E['peg_slot_width']/2
    round_z=E['peg_slot_round_center_z']
    # Semicircular lower ends remove the sharp corners at the leg roots.
    slot_x=box(x-6,x+6,-s,s,round_z,top+1)+mf.Manifold.cylinder(12,s,s,144).transform([
        [0,0,1,x-6],[1,0,0,0],[0,1,0,round_z]])
    slot_y=box(x-s,x+s,-6,6,round_z,top+1)+mf.Manifold.cylinder(12,s,s,144).transform([
        [1,0,0,x],[0,0,-1,6],[0,1,0,round_z]])
    slots=slot_x+slot_y
    return p - inner - slots


def fin_start_x():
    return E['peg_center_from_rear'] + M['peg_base_diameter']/2 + M['peg_to_fin_edge_gap_along_length']


def spring_latch():
    # The close-ups show a continuous transverse wall, reinforced by three
    # gussets on the peg side. It is not a bar held only by open curved struts.
    start = fin_start_x()
    z0 = M['base_wall']
    wall_top = E['latch_top_z'] - E['latch_bar_thickness']
    foot = start + E['latch_wall_foot_from_fin_start']
    thick = E['latch_wall_thickness_x']
    lean = 1.2
    wall = xz([[foot,z0-0.15],[foot+thick,z0-0.15],
               [foot+thick+lean,wall_top+0.1],[foot+lean,wall_top+0.1]],M['latch_width'])
    t = np.linspace(0,1,48)[:,None]
    p0, p1, p2, p3 = map(np.array, ([start+0.9,z0+0.15], [start+5.3,z0+0.15],
                                  [start+4.8,wall_top-0.1], [start+9.8,wall_top+0.2]))
    center = (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
    profile = np.vstack([[center[0,0],z0-0.15],center,[center[-1,0],z0-0.15]])
    ribs = [xz(profile, E['latch_rib_width'], y) for y in [-5.4,0,5.4]]
    # One cross-section prevents coincident faces between bar and tooth.
    bar = xz([[start+9.1,wall_top],[start+10.5,wall_top],
              [start+10.5,wall_top-0.3],[start+11.2,wall_top+0.3],
              [start+10.9,E['latch_top_z']],[start+9.1,E['latch_top_z']]],M['latch_width'])
    return mf.Manifold.batch_boolean(ribs+[wall,bar],mf.OpType.Add)


def guides():
    t = M['fin_thickness']
    c = M['guide_outside_width']/2 - t/2
    start = fin_start_x()
    z0 = M['base_wall']
    fins = []
    for side,y in [('right',-c),('left',c)]:
        base = M[side+'_fin_base_length']
        top = M[side+'_fin_top_length']
        height = M[side+'_fin_height_above_surface']
        # Full design dimensions are taken at the inner base surface. Extend
        # the root vertically 0.15 mm into the skin for a robust solid union.
        profile = [[start,z0-0.15],[start+base,z0-0.15],
                   [start+base,z0],[start+top,z0+height],
                   [start,z0+height]]
        fin=xz(round_fin_end(profile,E['fin_tip_radius']),t,y)
        lean=-math.copysign(math.tan(math.radians(E['fin_inward_lean_degrees'])),y)
        fin=fin.transform([[1,0,0,0],[0,1,lean,-lean*z0],[0,0,1,0]])
        fins.append(fin)
    return fins[0]+fins[1]


def build():
    profile, dim = hook_profile()
    cx,cz,ri,ro,a = dim
    envelope = hook_envelope()
    support_width=M['body_width']
    hook_section=section(profile)
    # A single solid profile replaces the overlapping ramp and lateral webs.
    # Its rear edge meets the outside hook circle at an exact tangent.
    bottom = cz-ro
    p,tangent=back_link_tangent(cx,cz,ro)
    back_section=section([p,[fin_start_x()+E['frame_end_from_fin_start'],p[1]],
                          [cx,cz],tangent])
    # Build the circular void from the same angular vertices as the hook.
    # This avoids independent circle tessellations creating sliver faces.
    _,_,_,_,half=dim
    direction=E['hook_opening_direction_degrees']
    angles=np.unique(np.r_[np.linspace(direction+half,direction-half+360,201),
                            [90.,180.,270.],np.linspace(direction-half,direction+half,101)])
    # The host cut is 0.01 mm oversize; the untouched C shell supplies the
    # exact mating surface without near-coincident circle subtraction.
    circle=[[cx+(ri+0.01)*math.cos(math.radians(t)),cz+(ri+0.01)*math.sin(math.radians(t))] for t in angles]
    circle_section=section(circle)
    angle=math.radians(E['hook_opening_direction_degrees'])
    u=np.array([math.cos(angle),math.sin(angle)])
    v=np.array([-math.sin(angle),math.cos(angle)])
    mouth_half=M['hook_mouth']/2
    lip=math.sqrt(ri*ri-mouth_half*mouth_half)-.0001
    entry_section=section([np.array([cx,cz])+u*a+v*b for a,b in
                          [(lip,-mouth_half),(40,-mouth_half),(40,mouth_half),(lip,mouth_half)]])
    frame_end=fin_start_x()+E['frame_end_from_fin_start']
    base_end=fin_start_x()+E['base_front_from_fin_start']
    platform_section=section([[0,0],[base_end,0],[base_end,M['base_wall']],[0,M['base_wall']]])
    neck_section=section([[cx-1.5,cz+ri-.2],[frame_end,cz+ri-.2],
                          [frame_end,.1],[cx-1.5,.1]])
    # Fuse the trimmed crossbar in the same 2D profile as the base so its
    # lateral faces are exactly flush, without coincident 3D union seams.
    rail_start=fin_start_x()+E['frame_start_from_fin_start']
    rail_section=section([[rail_start,.02],[frame_end,.02],
                          [frame_end,2.5],[rail_start,2.5]])
    host_section=(platform_section+back_section+neck_section+rail_section)-circle_section-entry_section
    # A smooth upper lip relief removes the old straight angled end face.
    # Its first tangent follows the open entry, its last follows the base end.
    upper=np.array([cx,cz])+u*lip+v*mouth_half
    q=np.array([frame_end,0.0])
    c1=upper+u*E['hook_upper_blend_start_handle']
    c2=q-np.array([0,E['hook_upper_blend_end_handle']])
    t=np.linspace(0,1,121)[:,None]
    curve=(1-t)**3*upper+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*q
    relief=section(np.vstack([curve,[frame_end+4,0],[frame_end+4,-30],[upper[0],-30]]))
    host_section=host_section-relief
    body_section=host_section+hook_section
    # The corrected 1.4 x 1.4 mm tooth is diametrically opposite the mouth.
    # U points through the opening; the tooth is centred on the negative U
    # axis. Its local height runs along V. Embed the root 0.3 mm into the wall.
    h=M['hook_internal_rib_height']/2
    profile=[np.array([cx,cz])+u*a+v*b for a,b in [
        (-ri-.3,-h),(-ri+M['hook_internal_rib_projection'],-h),
        (-ri+M['hook_internal_rib_projection'],h),(-ri-.3,h)]]
    # Fuse the support and hook in 2D before extruding one flush side face.
    # This eliminates the tiny overlapping coplanar support facets in 3D.
    body=xz(body_section+section(profile),support_width)^envelope^rear_plan_mask()
    parts = [body,peg(),guides(),spring_latch()]
    clip = mf.Manifold.batch_boolean(parts,mf.OpType.Add).simplify(0.0001)
    # Isolate the actual mating profile without the bulky back link or mount.
    # This central slice is prismatic: its full broad side can sit on the bed.
    mask=xz(arc(cx,cz,ro+0.05,0,360,361)[:-1],E['coupon_width'])
    core=clip^mask
    left=cx-ro
    tab_profile=section([[left-E['coupon_handle_length'],cz-E['coupon_handle_height']/2],
                         [left+E['coupon_handle_overlap'],cz-E['coupon_handle_height']/2],
                         [left+E['coupon_handle_overlap'],cz+E['coupon_handle_height']/2],
                         [left-E['coupon_handle_length'],cz+E['coupon_handle_height']/2]])
    radius=E['coupon_handle_corner_radius']
    tab=tab_profile.offset(-radius).offset(radius).extrude(E['coupon_width']).transform([
        [1,0,0,0],[0,0,-1,E['coupon_width']/2],[0,1,0,0]])
    coupon=(core+tab).simplify(0.0001)
    return clip, coupon, dim


def as_mesh(solid):
    assert solid.status() == mf.Error.NoError, solid.status()
    m = solid.to_mesh()
    return trimesh.Trimesh(vertices=np.array(m.vert_properties)[:,:3],
                           faces=np.array(m.tri_verts),process=True)


def place_on_bed(mesh):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    m.apply_translation(-m.bounds[0])
    return m


def validate_and_save(mesh,name):
    path = OUT/name
    mesh.export(path)
    # Reload the actual STL; validate exported triangles rather than just CSG.
    saved = trimesh.load_mesh(path,process=True)
    comps = trimesh.graph.connected_components(saved.face_adjacency,
                nodes=np.arange(len(saved.faces)), min_len=1, engine='scipy')
    report = {
        'file': 'stl/'+name,
        'triangles': len(saved.faces),
        'vertices': len(saved.vertices),
        'watertight': bool(saved.is_watertight),
        'winding_consistent': bool(saved.is_winding_consistent),
        'positive_volume': bool(saved.volume > 0),
        'connected_solids': len(comps),
        'bounds_mm': saved.bounds.tolist(),
        'dimensions_mm': saved.extents.tolist(),
        'volume_mm3': float(saved.volume),
        'degenerate_triangles': int(np.count_nonzero(saved.area_faces < 1e-9)),
        'finite_coordinates': bool(np.isfinite(saved.vertices).all()),
    }
    assert report['watertight'] and report['winding_consistent'] and report['positive_volume'], report
    assert report['connected_solids'] == 1 and report['degenerate_triangles'] == 0, report
    return report


def draw_3d(ax,mesh,elev,azim):
    # Smaller preview facets improve painter-order occlusion on broad flat
    # surfaces without modifying the printable mesh.
    vertices,faces=trimesh.remesh.subdivide_to_size(mesh.vertices,mesh.faces,max_edge=2.0,max_iter=7)
    shown=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    tris=shown.triangles
    light=np.array([-0.4,-0.3,0.85]); light/=np.linalg.norm(light)
    intensity=0.45+0.55*np.maximum(0,shown.face_normals@light)
    colors=np.column_stack([intensity*0.33,intensity*0.62,intensity*0.83,np.ones(len(tris))])
    poly=Poly3DCollection(tris,facecolors=colors,linewidths=0,edgecolors='none',zsort='average')
    ax.add_collection3d(poly)
    lo,hi=mesh.bounds
    mid=(lo+hi)/2; r=max(hi-lo)*0.57
    ax.set_xlim(mid[0]-r,mid[0]+r); ax.set_ylim(mid[1]-r,mid[1]+r); ax.set_zlim(mid[2]-r,mid[2]+r)
    ax.set_box_aspect((1,1,1)); ax.set_proj_type('ortho'); ax.view_init(elev,azim); ax.set_axis_off()


def preview(mesh):
    fig=plt.figure(figsize=(13,6),facecolor='#f5f6f8')
    for i,(e,a,title) in enumerate([(27,132,'Peg, guides and spring latch'),(18,-42,'Hook channel and outside skin')],1):
        ax=fig.add_subplot(1,2,i,projection='3d',facecolor='#f5f6f8')
        draw_3d(ax,mesh,e,a); ax.set_title(title,fontsize=13,pad=-5)
    fig.suptitle(f"760 867 899 · {P['revision']} · measured-photo reconstruction",fontsize=17,y=.97)
    fig.text(.5,.035,'FIT-TEST PROTOTYPE  ·  Dimensions in mm  ·  No physical print or retention test yet',ha='center',fontsize=11,color='#5d6570')
    plt.subplots_adjust(left=0,right=1,bottom=.07,top=.91,wspace=-.13)
    fig.savefig(PREVIEW/'clip.png',dpi=160); plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14,5),facecolor='white')
    for ax,(u,v,label) in zip(axes,[(0,2,'Side · X/Z'),(0,1,'Plan · X/Y'),(1,2,'End · Y/Z')]):
        # Rasterize visible triangle projections into a silhouette without
        # altering the model, to expose the reconstructed mating outlines.
        from matplotlib.collections import PolyCollection
        ax.add_collection(PolyCollection(mesh.triangles[:,:,[u,v]],facecolors='#366582',edgecolors='none'))
        lo,hi=mesh.bounds; ax.set_xlim(lo[u]-3,hi[u]+3); ax.set_ylim(lo[v]-3,hi[v]+3)
        ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(label)
        ax.set_xlabel('mm'); ax.set_ylabel('mm')
        if (u,v)==(0,2):
            root_edge=E['peg_center_from_rear']+M['peg_base_diameter']/2
            rear=fin_start_x()
            z=hi[2]+1.2
            for x in [root_edge,rear]:
                ax.plot([x,x],[M['base_wall'],z+.2],color='#b05a25',lw=.8,ls=':')
            ax.annotate('',xy=(root_edge,z),xytext=(rear,z),
                        arrowprops={'arrowstyle':'<->','color':'#b05a25','lw':1.2})
            ax.text((root_edge+rear)/2,z+.25,'9 mm clear gap',ha='center',
                    va='bottom',fontsize=9,color='#8e451c')
    fig.suptitle('Orthographic silhouettes · compare with the original before fitting',fontsize=15)
    fig.tight_layout(); fig.savefig(PREVIEW/'orthographic.png',dpi=160); plt.close(fig)


def main():
    clip,coupon,dim=build()
    mesh=as_mesh(clip)
    coupon_in_design=as_mesh(coupon)
    coupon_mesh=place_on_bed(coupon_in_design)
    reports=[validate_and_save(mesh,'760867899_clip.stl'),
             validate_and_save(place_on_bed(mesh),'760867899_clip_on_side.stl'),
             validate_and_save(coupon_mesh,'760867899_hook_fit_test.stl')]
    # Isolate the measured split peg on a small flat base for a quick trial.
    peg_test = (box(0,14,-7,7,0,M['base_wall']) +
                peg().translate([7-E['peg_center_from_rear'],0,0])).simplify(0.0001)
    peg_mesh = as_mesh(peg_test)
    peg_mesh.apply_translation(-peg_mesh.bounds[0])
    reports.append(validate_and_save(peg_mesh,'760867899_peg_fit_test.stl'))
    highest=max(M['peg_total_height_including_wall'],
                M['base_wall']+M['right_fin_height_above_surface'],
                M['base_wall']+M['left_fin_height_above_surface'],E['latch_top_z'])
    total_height=highest-(M['base_wall']-M['hook_drop_from_mounting_surface'])
    np.testing.assert_allclose(mesh.extents,[M['length'],M['body_width'],total_height],atol=0.002)
    assert abs(reports[0]['volume_mm3']-reports[1]['volume_mm3']) < 0.01
    cx,cz,ri,ro,a=dim
    dimensional_checks={
        'overall_length_mm':float(mesh.extents[0]),
        'maximum_frame_width_mm':float(mesh.extents[1]),
        'original_frame_width_reference_mm':M['frame_width'],
        'front_crossbar_is_flush':True,
        'overall_height_mm':float(mesh.extents[2]),
        'hook_cavity_design_diameter_mm':2*ri,
        'hook_mouth_design_chord_mm':2*ri*math.sin(math.radians(a)),
        'hook_drop_from_mounting_surface_mm':M['hook_drop_from_mounting_surface'],
        'hook_base_to_nearest_inside_mm':M['hook_base_to_nearest_inside'],
        'derived_hook_shell_wall_mm':ro-ri,
        'hook_internal_rib_height_mm':M['hook_internal_rib_height'],
        'hook_internal_rib_projection_mm':M['hook_internal_rib_projection'],
        'peg_base_design_diameter_mm':M['peg_base_diameter'],
        'peg_barb_design_diameter_mm':M['peg_barb_diameter'],
        'peg_top_z_including_wall_mm':M['peg_total_height_including_wall'],
        'measured_base_wall_range_mm':[2.5,2.6],
        'base_wall_design_mm':M['base_wall'],
        'latch_bar_design_width_mm':M['latch_width'],
        'right_fin_mm':{k:M['right_fin_'+k] for k in ['base_length','top_length','height_above_surface']},
        'left_fin_mm':{k:M['left_fin_'+k] for k in ['base_length','top_length','height_above_surface']},
        'fin_thickness_mm':M['fin_thickness'],
        'peg_to_fin_edge_gap_along_length_mm':M['peg_to_fin_edge_gap_along_length'],
        'fin_rear_station_x_mm':fin_start_x(),
        'latch_has_continuous_wall':True,
        'mounting_platform_is_flat':True,
        'hook_back_link_is_solid':True,
        'nominal_and_on_side_same_volume':True,
        'physical_fit_verified':False,
        'slicer_toolpaths_verified':False,
    }
    actual_checks=check_export(OUT/'760867899_clip.stl',P)
    from verify_hook_test import check_hook_test
    hook_test_checks=check_hook_test(OUT/'760867899_hook_fit_test.stl',
                                    OUT/'760867899_clip.stl',P,dim,coupon_in_design.bounds)
    report={'revision':P['revision'],'units':'mm','meshes':reports,'dimensions':dimensional_checks,
            'exported_stl_section_measurements':actual_checks,
            'hook_fit_test_checks':hook_test_checks,
            'limitations':['Mesh checks do not validate physical fit, material fatigue, creep or retention.',
                           'Measured dimensions constrain a photo reconstruction; unmeasured features remain estimates.',
                           'No FEA, calibrated 3D scan, printed trial, or vehicle fit test has been performed.']}
    (CHECKS/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    preview(mesh)
    render_section(OUT/'760867899_clip.stl',P,PREVIEW/'hook_section.png')
    from render_peg_section import render_peg_section
    render_peg_section(OUT/'760867899_peg_fit_test.stl',P,PREVIEW/'peg_reinforcement.png')
    preview_hook_test(coupon_mesh)
    print(json.dumps(report,indent=2))


def preview_hook_test(mesh):
    fig=plt.figure(figsize=(11,5.5),facecolor='#f5f6f8')
    ax=fig.add_subplot(1,2,1,projection='3d',facecolor='#f5f6f8')
    draw_3d(ax,mesh,36,-63)
    ax.set_title('Broad flat side on the bed',fontsize=12,pad=-8)
    ax=fig.add_subplot(1,2,2,facecolor='#f5f6f8')
    from matplotlib.collections import PolyCollection
    ax.add_collection(PolyCollection(mesh.triangles[:,:,:2],facecolors='#366582',edgecolors='none'))
    lo,hi=mesh.bounds
    ax.set_xlim(lo[0]-1.5,hi[0]+1.5);ax.set_ylim(lo[1]-1.5,hi[1]+1.5)
    ax.set_aspect('equal');ax.set_axis_off();ax.set_title('Top view · opening and tooth',fontsize=12)
    fig.suptitle(f"{P['revision']} · hook fit test · Ø 9.7 / 8.1 mm mouth / 1.4 mm tooth",fontsize=15,y=.97)
    fig.text(.5,.055,'4 mm print height · flat contact face · rounded grip tab · import at 100%',ha='center',fontsize=11,color='#555')
    plt.subplots_adjust(left=.01,right=.99,top=.88,bottom=.13,wspace=.03)
    fig.savefig(PREVIEW/'hook_fit_test.png',dpi=170);plt.close(fig)


if __name__=='__main__':
    main()
