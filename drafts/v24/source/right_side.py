"""Create right-side fin variant by mirroring only the fins and shifting -6 X."""
import os,json,shutil
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def box(x0,x1,y0,y1,z0,z1):return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
p=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());m=p['measured'];z0=m['base_wall']
source=ROOT/'drafts/v24/stl/760867899_v24_existing_flat_support.stl';old=load(source)
# Remove only the two outside fins. 0.01 mm root overlap is filled by the exact
# original plate below; no other fixture falls in these two narrow side windows.
windows=box(18.05,28.1,9.5,12.5,z0-.01,11)+box(18.05,28.1,-12.5,-9.5,z0-.01,11)
fins=old^windows
newfins=fins.mirror([0,1,0]).translate([-6,0,0])
plate=old^box(-1,36,-20,20,-30,z0)
right=(old-windows)+plate+newfins
raw=right.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
path=OUT/'stl/760867899_v24_right_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
print('Mesh',check.is_watertight,check.is_winding_consistent,components,flush=True)
assert check.is_watertight and check.is_winding_consistent and components==1
# Preserve current part as a second, explicitly labelled file without modification.
# Existing version already generated beside this variant.
# Changes are confined to old/new fin windows, including their roots.
allowed=windows+windows.mirror([0,1,0]).translate([-6,0,0])
diff=((old-right)+(right-old))-allowed
assert abs(diff.volume())<.002
# Root spacing and longitudinal placements follow from a rigid transform of actual fins.
report={'revision':'v24','variant':'right side','fins_swapped_across_Y':True,'fin_translation_X_mm':-6,'previous_fin_start_X_mm':18.1,'right_fin_start_X_mm':12.1,'fin_root_outside_spacing_mm':24.5,'watertight':bool(check.is_watertight),'consistent_winding':bool(check.is_winding_consistent),'connected_components':int(components),'volume_changed_outside_fin_regions_mm3':abs(diff.volume()),'physical_fit_verified':False}
(OUT/'right_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
fig,axes=plt.subplots(1,2,figsize=(11,7),facecolor='white')
for ax,solid,title in zip(axes,[old,right],['Existing version · unchanged','Right-side version · swapped, 6 mm toward peg']):
 raw=solid.to_mesh();me=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 base=solid.slice(1.2)
 for pts in base.to_polygons():
  pts=np.array(pts);ax.fill(pts[:,1],pts[:,0],facecolor='#e0e8ed',edgecolor='#3c6075',lw=1.2)
 for label,y,color in [('Tall fin',1 if solid is right else -1,'#dc8744'),('Short fin',-1 if solid is right else 1,'#5798bb')]:
  triangles=me.triangles
  mask=(triangles[:,:,2].max(axis=1)>z0+.03)&(triangles[:,:,1].mean(axis=1)*y>9.5)
  pts=triangles[mask][:,:,[1,0]]
  ax.add_collection(PolyCollection(pts,facecolors=color,edgecolors='none'))
  ax.text(y*8.5,17 if solid is right else 23,label,rotation=90,ha='center',va='center',color=color,fontweight='bold')
 # Other fixtures drawn from projections of actual mesh triangles.
 tri=me.triangles;mask=(tri[:,:,2].min(axis=1)>z0-.001)&(tri[:,:,2].max(axis=1)>z0+.03)&(abs(tri[:,:,1].mean(axis=1))<8.5)
 ax.add_collection(PolyCollection(tri[mask][:,:,[1,0]],facecolors='#849baa',edgecolors='none',alpha=.7))
 ax.set_aspect('equal');ax.set_xlim(-16,16);ax.set_ylim(-2,36);ax.set_title(title,fontsize=11);ax.set_xlabel('Width Y (mm)');ax.set_ylabel('← Toward peg / back     Length X (mm)     Hook / front →');ax.grid(alpha=.13)
 axes[1].annotate('6 mm toward peg',xy=(0,12.1),xytext=(0,18.1),ha='center',arrowprops={'arrowstyle':'->','lw':1.8},fontsize=9)
fig.suptitle('Flat-backed versions · top view',fontsize=16);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'previews/right_side_comparison.png',dpi=170);plt.close(fig)
