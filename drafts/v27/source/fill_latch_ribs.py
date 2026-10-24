"""Fill the three root-to-wall gaps without changing the 115 degree latch."""
from pathlib import Path
import json,math,os
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch

def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def xz(points,width,y):
 a=np.array(points);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1))
 return mf.CrossSection([a if area>0 else a[::-1]]).extrude(width).transform([[1,0,0,0],[0,0,-1,y+width/2],[0,1,0,0]])
p=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());m=p['measured'];e=p['estimated'];z0=m['base_wall'];foot=28.;ztop=6.;slope=1/math.tan(math.radians(115));lean=(ztop-z0)*slope
rib_end=foot+lean+.6;bottom=z0-.15
# Wedge overlaps the existing vertical rib end and the peg-facing wall by 0.2 mm.
# Its wall-side edge follows exactly the 115 degree leg from plate to cap.
points=[[rib_end-.05,bottom],[foot+(bottom-z0)*slope+.2,bottom],[foot+lean+.2,ztop],[foot+lean-.2,ztop]]
y_positions=[-5.4,0,5.4];fill=mf.Manifold.batch_boolean([xz(points,e['latch_rib_width'],y) for y in y_positions],mf.OpType.Add)
checks=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v26/stl'/f'760867899_v26_{layout}_flat_support.stl');new=old+fill
 raw=new.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v27_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print(layout,check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 # Each rib must provide continuous support right up to the wall at every height.
 for y in y_positions:
  for z in np.linspace(z0+.01,5.89,75):
   wallx=foot+(z-z0)*slope
   probe=mf.Manifold.cube([.12,.5,.006]).translate([wallx-.04,y-.25,z-.003])
   assert (probe-new).volume()<1e-7,(y,z)
 assert abs((old-new).volume())<.002
 checks.append({'layout':layout,'watertight':True,'consistent_winding':True,'connected_components':int(components),'added_material_mm3':(new-old).volume(),'removed_material_mm3':(old-new).volume(),'ribs':3,'full_height_wall_contact_checked':True,'contact_height_samples_per_rib':75,'wall_angle_degrees':115,'physical_fit_verified':False})
 if layout=='existing':before=old;after=new
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
def side(s,y=0):return s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(-y)
def draw(ax,section,color,fill=True):
 pts=[];codes=[]
 for a in section.to_polygons():
  pts.extend(a.tolist()+[a[0].tolist()]);codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
 ax.add_patch(PathPatch(PlotPath(pts,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.4))
fig,axes=plt.subplots(1,2,figsize=(12,5.8),facecolor='white')
for ax,s,title in zip(axes,[before,after],['v26 · gap behind the rib','v27 · filled, full-height contact']):
 draw(ax,side(s),'#a3c5d9')
 if s is after:draw(ax,side(before),'#c67b34',False)
 ax.set_aspect('equal');ax.set_xlim(20,32);ax.set_ylim(1.8,8);ax.set_xlabel('Length X (mm) · peg toward left');ax.set_ylabel('Height Z (mm)');ax.set_title(title);ax.grid(alpha=.15)
axes[1].annotate('Filled up to the\n115° wall',xy=(27.3,3.7),xytext=(23,6.7),arrowprops={'arrowstyle':'->'},fontsize=11)
fig.suptitle('Section through a support rib · same fix on all three ribs',fontsize=15)
fig.text(.5,.025,'Blue: actual STL section · orange: previous outline',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(OUT/'previews/rib_gap_comparison.png',dpi=175);plt.close(fig)
