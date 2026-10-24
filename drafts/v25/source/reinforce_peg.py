"""Add internal peg material only; preserve the v24 exterior and both fin layouts."""
import json,math,os
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def box(x0,x1,y0,y1,z0,z1):return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
p=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());m=p['measured'];e=p['estimated'];x=e['peg_center_from_rear'];z0=m['base_wall']-.2;shoulder=e['peg_barb_shoulder_z'];top=m['peg_total_height_including_wall'];root=m['peg_base_diameter']/2;barb=m['peg_barb_diameter']/2;tip=e['peg_tip_diameter']/2
outer=mf.Manifold.cylinder(shoulder-z0,root,root,144).translate([x,0,z0])+mf.Manifold.cylinder(top-shoulder,barb,tip,144).translate([x,0,shoulder])
# 0.5 mm more material on each inside face; longer tapered internal root collar.
inner_radius=1.6;root_inner_radius=.65;collar=1.6;slot_z=e['peg_slot_root_z'];s=e['peg_slot_width']/2+.01;round_z=4.15
inner=mf.Manifold.cylinder(collar,root_inner_radius,inner_radius,144).translate([x,0,slot_z])+mf.Manifold.cylinder(top-slot_z-collar+1,inner_radius,inner_radius,144).translate([x,0,slot_z+collar])
slotx=box(x-6,x+6,-s,s,round_z,top+1)+mf.Manifold.cylinder(12,s,s,144).transform([[0,0,1,x-6],[1,0,0,0],[0,1,0,round_z]])
sloty=box(x-s,x+s,-6,6,round_z,top+1)+mf.Manifold.cylinder(12,s,s,144).transform([[1,0,0,x],[0,0,-1,6],[0,1,0,round_z]])
peg=(outer-inner-slotx-sloty)^mf.Manifold.cylinder(7,2.2,2.2,144).translate([x,0,2.35])
reports=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v24/stl'/f'760867899_v24_{layout}_flat_support.stl');new=old+peg
 data=new.to_mesh();mesh=trimesh.Trimesh(vertices=data.vert_properties[:,:3],faces=data.tri_verts,process=True)
 mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v25_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print('Mesh',check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 added=new-old;outside=added-box(x-4.41,x+4.41,-4.41,4.41,2.34,8.51)
 assert abs(outside.volume())<.002 and abs((old-new).volume())<.002
 report={'layout':layout,'watertight':True,'consistent_winding':True,'connected_components':int(components),'added_material_mm3':added.volume(),'removed_material_mm3':(old-new).volume(),'added_material_outside_peg_region_mm3':outside.volume(),'inner_diameter_mm':3.2,'previous_inner_diameter_mm':4.2,'stem_radial_wall_mm':2.1,'previous_stem_radial_wall_mm':1.6,'root_collar_height_mm':1.6,'previous_root_collar_height_mm':1.1,'slot_round_center_z_mm':4.15,'previous_slot_round_center_z_mm':3.9,'outside_root_diameter_mm':7.4,'outside_barb_diameter_mm':8.8,'total_peg_height_mm':8.5,'physical_strength_verified':False}
 reports.append(report);print(json.dumps(report),flush=True)
 if layout=='existing':oldshow=old;newshow=new
(OUT/'checks.json').write_text(json.dumps(reports,indent=2)+'\n')
def draw(ax,section,color,fill):
 # Compound path preserves hollow interiors.
 from matplotlib.path import Path as P
 from matplotlib.patches import PathPatch
 points=[];codes=[]
 for a in section.to_polygons():
  points.extend(a.tolist()+[a[0].tolist()]);codes.extend([P.MOVETO]+[P.LINETO]*(len(a)-1)+[P.CLOSEPOLY])
 ax.add_patch(PathPatch(P(points,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.3))
def diagonal(s):
 return s.translate([-x,0,0]).rotate([0,0,45]).transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(0)
fig,axes=plt.subplots(1,2,figsize=(11,6),facecolor='white')
draw(axes[0],diagonal(newshow),'#93bbd1',True);draw(axes[0],diagonal(oldshow),'#b86f28',False)
axes[0].set_xlim(-5,5);axes[0].set_ylim(2,9);axes[0].set_title('Diagonal section through opposite legs');axes[0].set_xlabel('Distance from peg centre (mm)');axes[0].set_ylabel('Height Z (mm)')
for s,color,fill in [(newshow,'#93bbd1',True),(oldshow,'#b86f28',False)]:draw(axes[1],s.slice(5.4).translate([-x,0]),color,fill)
axes[1].set_xlim(-5,5);axes[1].set_ylim(-5,5);axes[1].set_title('Four legs · cross-section at Z=5.4 mm');axes[1].set_xlabel('X relative to peg centre (mm)');axes[1].set_ylabel('Width Y (mm)')
for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
fig.suptitle('v25 · stronger peg interiors and taller root reinforcement',fontsize=16)
fig.text(.5,.025,'Blue: v25 · orange outline: v24 · external peg dimensions and 1 mm slots retained',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(OUT/'previews/peg_reinforcement.png',dpi=175);plt.close(fig)
