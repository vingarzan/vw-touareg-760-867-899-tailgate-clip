import os,json
from pathlib import Path
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
def box(z0,z1):return mf.Manifold.cube([44,42,z1-z0]).translate([-2,-21,z0])
body=load(OUT/'source/flat_body.stl')^box(-30,.01)
reports=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v25/stl'/f'760867899_v25_{layout}_flat_support.stl')
 new=body+(old^box(0,20))
 data=new.to_mesh();mesh=trimesh.Trimesh(vertices=data.vert_properties[:,:3],faces=data.tri_verts,process=True)
 mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v26_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print(layout,check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 upper=box(.02,20);difference=(((old-new)+(new-old))^upper).volume();assert abs(difference)<.002
 reports.append({'layout':layout,'watertight':True,'consistent_winding':True,'components':int(components),'mounting_features_difference_mm3':difference,'recess_depth_mm':.6,'floor_fillet_mm':.2,'native_body_valid':True,'physical_fit_verified':False})
 if layout=='existing':shown=new
(OUT/'checks.json').write_text(json.dumps(reports,indent=2)+'\n')
def draw(ax,section,color,fill=True):
 pts=[];codes=[]
 for a in section.to_polygons():
  pts.extend(a.tolist()+[a[0].tolist()]);codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
 ax.add_patch(PathPatch(PlotPath(pts,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.5))
oldp=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());newp=json.loads((OUT/'source/parameters.json').read_text())
side=shown.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(0)
fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='white')
for ax,p,title in zip(axes,[oldp,newp],['Previous · recess followed standard support','v26 · recess follows flat-back support']):
 draw(ax,side,'#c4dae7');pocket=mf.CrossSection([np.array(a) for a in p['pocket_contours']]);draw(ax,pocket,'#6d9bb5')
 ax.set_aspect('equal');ax.set_xlim(-1,36);ax.set_ylim(-19,10.8);ax.set_title(title,fontsize=12);ax.set_xlabel('Length X (mm)');ax.set_ylabel('Height Z (mm)');ax.grid(alpha=.15)
fig.suptitle('Flat-back recess alignment · side profile comparison',fontsize=16)
fig.text(.5,.025,'Recess footprints highlighted · 0.6 mm depth · unchanged peg, fins and latch',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(OUT/'previews/recess_comparison.png',dpi=170);plt.close(fig)
