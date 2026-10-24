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
    return section(points).extrude(width).transform([
        [1, 0, 0, 0], [0, 0, -1, center_y + width / 2], [0, 1, 0, 0]
    ])


def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1-x0, y1-y0, z1-z0]).translate([x0, y0, z0])


def arc(cx, cy, radius, a0, a1, count=80):
    ts = np.linspace(math.radians(a0), math.radians(a1), count)
    return np.column_stack([cx + radius*np.cos(ts), cy + radius*np.sin(ts)]).tolist()


def rounded_base():
    w, r, end = M['body_width']/2, E['rear_corner_radius'], E['base_length']
    # Large radii only at the rear peg end; small corners on the frame end.
    points = arc(r, -w+r, r, 180, 270, 40)
    points += [[end-0.7, -w]]
    points += arc(end-0.7, -w+0.7, 0.7, 270, 360, 12)
    points += arc(end-0.7, w-0.7, 0.7, 0, 90, 12)
    points += [[r, w]]
    points += arc(r, w-r, r, 90, 180, 40)
    return section(points).extrude(M['base_wall'])


def hook_profile():
    ri = M['hook_cavity']/2
    ro = ri + M['hook_wall']
    cx = M['length'] - ro
    highest = max(M['peg_total_height_including_wall'],
                  M['base_wall'] + M['right_fin_height_above_surface'],
                  M['base_wall'] + M['left_fin_height_above_surface'], E['latch_top_z'])
    bottom = highest - M['overall_height']
    cz = bottom + ro
    a = math.degrees(math.acos(M['hook_mouth'] / (2*ri)))
    # Add cardinal extrema explicitly so the mesh bounds preserve measured size.
    angles = np.unique(np.r_[np.linspace(180-a, 360+a, 181), 180., 270., 360.])
    outer = [[cx+ro*math.cos(math.radians(t)), cz+ro*math.sin(math.radians(t))] for t in angles]
    inner = [[cx+ri*math.cos(math.radians(t)), cz+ri*math.sin(math.radians(t))] for t in angles[::-1]]
    return outer+inner, (cx, cz, ri, ro, a)


def hook_envelope():
    # Front free lip narrows to the measured 17.3 mm. Side shoulders support
    # the wider 27.6 mm frame; the precise taper is estimated from photographs.
    w, lip = M['frame_width']/2, M['hook_lip_width']/2
    plan = [[-2,-w], [21.5,-w], [31.2,-lip], [36,-lip],
            [36,lip], [31.2,lip], [21.5,w], [-2,w]]
    return section(plan).extrude(40).translate([0,0,-20])


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
    inner = mf.Manifold.cylinder(top-slot_z+1, E['peg_inner_diameter']/2,
                                E['peg_inner_diameter']/2, 96).translate([x,0,slot_z])
    s = E['peg_slot_width']/2
    slots = box(x-6,x+6,-s,s,slot_z,top+1) + box(x-s,x+s,-6,6,slot_z,top+1)
    return p - inner - slots


def spring_latch():
    # Three curved flexible ribs visibly connect the foot to the transverse
    # latch. Their free ends stay clear of the frame cross rail.
    t = np.linspace(0,1,48)[:,None]
    p0, p1, p2, p3 = map(np.array, ([10.4,2.2], [14.8,2.2], [14.3,5.8], [19.3,6.25]))
    center = (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
    tangent = np.gradient(center, axis=0)
    normal = np.column_stack([-tangent[:,1],tangent[:,0]])
    normal /= np.linalg.norm(normal,axis=1)[:,None]
    h = E['latch_rib_thickness']/2
    profile = np.vstack([center+normal*h, (center-normal*h)[::-1]])
    ribs = [xz(profile, E['latch_rib_width'], y) for y in [-5.4,0,5.4]]
    w = M['latch_width']/2
    # One cross-section prevents coincident faces between bar and tooth.
    bar = xz([[18.6,5.9],[20.0,5.9],[20.0,5.6],[20.7,6.2],
              [20.4,7.2],[18.6,7.2]],M['latch_width'])
    return mf.Manifold.batch_boolean(ribs+[bar],mf.OpType.Add)


def guides():
    t = M['fin_thickness']
    c = M['guide_outside_width']/2 - t/2
    start = E['fin_rear_edge_from_peg_end']
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
        fins.append(xz(profile,t,y))
    return fins[0]+fins[1]


def build():
    profile, dim = hook_profile()
    cx,cz,ri,ro,a = dim
    envelope = hook_envelope()
    hook = xz(profile,M['frame_width'])
    # Ramp skin and two outer shoulder webs join the rear plate to the hook.
    # The common cylindrical cut preserves the 9.4 mm channel through them.
    bottom = cz-ro
    ramp_profile = [[16.5,-0.1],[19.8,-0.1],[25.0,bottom+3.8],
                    [23.0,bottom+2.1],[18.0,0.2],[16.5,0.2]]
    ramp = xz(ramp_profile,M['frame_width'])
    web_profile = [[13.6,0.1],[21.5,2.5],[27.6,bottom+0.5],
                   [24.0,bottom+0.5],[17.8,-1.0]]
    thick = E['side_web_thickness']
    web_c = M['frame_width']/2-thick/2
    webs = xz(web_profile,thick,-web_c)+xz(web_profile,thick,web_c)
    # Oversize the structural clearance by 0.01 mm so independent circle
    # tessellations cannot create sliver faces; the hook itself defines fit.
    channel = mf.Manifold.cylinder(40,ri+0.01,ri+0.01,192).transform([
        [1,0,0,cx],[0,0,-1,20],[0,1,0,cz]
    ])
    # Keep the peg and latch side of the skin continuous; only the lower hook
    # receives the circular channel cut.
    lower = (hook + ((ramp + webs) - channel)) ^ envelope
    # Slight overlap avoids leaving disconnected faces at the rail root.
    # Extend the rail foot into the ramp so the shallower v02 hook cannot
    # leave a sealed sliver-shaped pocket under the rear of the cross rail.
    rail = box(19.4,21.7,-M['frame_width']/2,M['frame_width']/2,-0.8,2.5)
    body = rounded_base() + lower + rail
    parts = [body,peg(),guides(),spring_latch()]
    clip = mf.Manifold.batch_boolean(parts,mf.OpType.Add).simplify(0.0001)
    # The dimension test uses the exact same hook section, made only 5 mm wide.
    coupon = xz(profile,E['coupon_width'])
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
    tris=mesh.triangles
    light=np.array([-0.4,-0.3,0.85]); light/=np.linalg.norm(light)
    intensity=0.45+0.55*np.maximum(0,mesh.face_normals@light)
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
    fig.suptitle('Orthographic silhouettes · compare with the original before fitting',fontsize=15)
    fig.tight_layout(); fig.savefig(PREVIEW/'orthographic.png',dpi=160); plt.close(fig)


def main():
    clip,coupon,dim=build()
    mesh=as_mesh(clip)
    coupon_mesh=place_on_bed(as_mesh(coupon))
    reports=[validate_and_save(mesh,'760867899_clip.stl'),
             validate_and_save(place_on_bed(mesh),'760867899_clip_on_side.stl'),
             validate_and_save(coupon_mesh,'760867899_hook_fit_test.stl')]
    # Isolate the measured split peg on a small flat base for a quick trial.
    peg_test = (box(0,14,-7,7,0,M['base_wall']) +
                peg().translate([7-E['peg_center_from_rear'],0,0])).simplify(0.0001)
    peg_mesh = as_mesh(peg_test)
    peg_mesh.apply_translation(-peg_mesh.bounds[0])
    reports.append(validate_and_save(peg_mesh,'760867899_peg_fit_test.stl'))
    np.testing.assert_allclose(mesh.extents,[M['length'],M['frame_width'],M['overall_height']],atol=0.002)
    assert abs(reports[0]['volume_mm3']-reports[1]['volume_mm3']) < 0.01
    cx,cz,ri,ro,a=dim
    dimensional_checks={
        'overall_length_mm':float(mesh.extents[0]),
        'maximum_frame_width_mm':float(mesh.extents[1]),
        'overall_height_mm':float(mesh.extents[2]),
        'hook_cavity_design_diameter_mm':2*ri,
        'hook_mouth_design_chord_mm':2*ri*math.cos(math.radians(a)),
        'peg_base_design_diameter_mm':M['peg_base_diameter'],
        'peg_barb_design_diameter_mm':M['peg_barb_diameter'],
        'peg_top_z_including_wall_mm':M['peg_total_height_including_wall'],
        'measured_base_wall_range_mm':[2.5,2.6],
        'base_wall_design_mm':M['base_wall'],
        'latch_bar_design_width_mm':M['latch_width'],
        'right_fin_mm':{k:M['right_fin_'+k] for k in ['base_length','top_length','height_above_surface']},
        'left_fin_mm':{k:M['left_fin_'+k] for k in ['base_length','top_length','height_above_surface']},
        'fin_thickness_mm':M['fin_thickness'],
        'nominal_and_on_side_same_volume':True,
        'physical_fit_verified':False,
        'slicer_toolpaths_verified':False,
    }
    actual_checks=check_export(OUT/'760867899_clip.stl',P)
    report={'revision':P['revision'],'units':'mm','meshes':reports,'dimensions':dimensional_checks,
            'exported_stl_section_measurements':actual_checks,
            'limitations':['Mesh checks do not validate physical fit, material fatigue, creep or retention.',
                           'Measured dimensions constrain a photo reconstruction; unmeasured features remain estimates.',
                           'No FEA, calibrated 3D scan, printed trial, or vehicle fit test has been performed.']}
    (CHECKS/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    preview(mesh)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
