"""Add a broad rear bevel/gusset, retaining the front lip and lower 115 degree leg."""
from pathlib import Path
import json,os,math
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
points=np.array([[26.84,4.98],[27.25,4.98],[27.25,7.2],[25.35,7.2]])
bevel=mf.CrossSection([points]).extrude(15).transform([[1,0,0,0],[0,0,-1,7.5],[0,1,0,0]])
checks=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v28/stl'/f'760867899_v28_{layout}_flat_support.stl');new=old+bevel
 raw=new.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v29_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print(layout,check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 removed=(old-new).volume();added=new-old
 assert abs(removed)<.002
 assert abs((added-box(25.34,27.26,-7.51,7.51,4.97,7.21)).volume())<.002
 checks.append({'layout':layout,'watertight':True,'consistent_winding':True,'components':int(components),'added_material_mm3':added.volume(),'removed_material_mm3':removed,'retaining_edge_unchanged':True,'lower_leg_angle_degrees':115,'rear_top_x_mm':25.35,'previous_rear_top_x_mm':26.39123858,'rear_bevel_height_mm':2.22,'physical_strength_verified':False})
 if layout=='existing':before=old;after=new
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
def side(s,y):return s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(-y)
def draw(ax,s,color,fill):
 pts=[];codes=[]
 for a in s.to_polygons():pts.extend(a.tolist()+[a[0].tolist()]);codes.extend([PP.MOVETO]+[PP.LINETO]*(len(a)-1)+[PP.CLOSEPOLY])
 ax.add_patch(PathPatch(PP(pts,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.4))
fig,axes=plt.subplots(1,2,figsize=(11.5,6),facecolor='white')
for ax,s,title in zip(axes,[before,after],['v28 · abrupt back of cap','v29 · broad angled rear transition']):
 draw(ax,side(s,2.5),'#a5c6d9',True)
 if s is after:draw(ax,side(before,2.5),'#bf7933',False)
 ax.set_aspect('equal');ax.set_xlim(24,32);ax.set_ylim(2,8);ax.grid(alpha=.15);ax.set_title(title,fontsize=12);ax.set_xlabel('← Back / peg          Length X (mm)          Front / hook →');ax.set_ylabel('Height Z (mm)')
axes[1].annotate('Added rear\nreinforcement',xy=(26,6.7),xytext=(24.2,7.6),arrowprops={'arrowstyle':'->'},fontsize=10)
fig.suptitle('Top lip back · material added for a broader load path',fontsize=15)
fig.text(.5,.025,'Actual sections between ribs · orange: previous outline · retaining tip and lower leg unchanged',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(OUT/'previews/lip_back_comparison.png',dpi=175);plt.close(fig)
