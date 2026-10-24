"""R0.8 circular internal fillets at both ends of the peg root taper."""
import os,json,math
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PP
from matplotlib.patches import PathPatch

def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def box(x0,x1,y0,y1,z0,z1):return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
x=5.4;floor=3.25;bottom_r=.65;inner_r=1.61;collar_top=4.85;R=.8
beta=math.atan2(collar_top-floor,inner_r-bottom_r)
lo_t=R*math.tan(beta/2);hi_t=R*math.tan((math.pi/2-beta)/2)
lo_center=(bottom_r-lo_t,floor+R);hi_center=(inner_r-R,collar_top+hi_t)
loangles=np.linspace(-math.pi/2,beta-math.pi/2,129);hiangles=np.linspace(beta-math.pi/2,0,129)
loarc=np.column_stack([lo_center[0]+R*np.cos(loangles),lo_center[1]+R*np.sin(loangles)])
hiarc=np.column_stack([hi_center[0]+R*np.cos(hiangles),hi_center[1]+R*np.sin(hiangles)])
profile=np.vstack([[0,floor],loarc,hiarc,[inner_r,9.5],[0,9.5]])
cavity=mf.CrossSection([profile]).revolve(144).translate([x,0,0])
# Additive-only reinforcement stays entirely within the previous peg envelope.
reinforcement=mf.Manifold.cylinder(3,2.2,2.2,144).translate([x,0,3.24])-cavity
s=.52;round_z=4.15
slotx=box(x-6,x+6,-s,s,round_z,10)+mf.Manifold.cylinder(12,s,s,144).transform([[0,0,1,x-6],[1,0,0,0],[0,1,0,round_z]])
sloty=box(x-s,x+s,-6,6,round_z,10)+mf.Manifold.cylinder(12,s,s,144).transform([[1,0,0,x],[0,0,-1,6],[0,1,0,round_z]])
reinforcement=reinforcement-slotx-sloty
checks=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v27/stl'/f'760867899_v27_{layout}_flat_support.stl');new=old+reinforcement
 raw=new.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 mesh.merge_vertices(digits_vertex=5)
 mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v28_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print(layout,check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 assert abs((old-new).volume())<.002
 outside=(new-old)-box(x-2.21,x+2.21,-2.21,2.21,3.23,6.25);assert abs(outside.volume())<.002
 checks.append({'layout':layout,'watertight':True,'consistent_winding':True,'components':int(components),'internal_fillet_radius_mm':R,'added_material_mm3':(new-old).volume(),'removed_material_mm3':(old-new).volume(),'outside_envelope_unchanged':True,'physical_strength_verified':False})
 if layout=='existing':before=old;after=new
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
def side(s):return s.translate([-x,0,0]).rotate([0,0,45]).transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(0)
def draw(ax,section,color,fill):
 pts=[];codes=[]
 for a in section.to_polygons():pts.extend(a.tolist()+[a[0].tolist()]);codes.extend([PP.MOVETO]+[PP.LINETO]*(len(a)-1)+[PP.CLOSEPOLY])
 ax.add_patch(PathPatch(PP(pts,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.4))
fig,axes=plt.subplots(1,2,figsize=(11,6),facecolor='white')
for ax,s,title in zip(axes,[before,after],['v27 · straight internal taper','v28 · R0.8 rounded root transitions']):
 draw(ax,side(s),'#a6c8da',True)
 if s is after:draw(ax,side(before),'#bd752d',False)
 ax.set_aspect('equal');ax.set_xlim(-2.8,2.8);ax.set_ylim(2.6,5.8);ax.set_title(title,fontsize=12);ax.set_xlabel('Distance from peg centre (mm)');ax.set_ylabel('Height Z (mm)');ax.grid(alpha=.15)
fig.suptitle('Peg root fillets · diagonal section through opposite legs',fontsize=15)
fig.text(.5,.025,'Blue: actual STL section · orange: previous profile · exterior fit dimensions unchanged',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(OUT/'previews/peg_root_fillets.png',dpi=175);plt.close(fig)
