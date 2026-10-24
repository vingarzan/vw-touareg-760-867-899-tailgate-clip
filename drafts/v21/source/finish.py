import sys,json
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'model'))
from render_rounding import load,draw,side
import matplotlib.pyplot as plt
from build import draw_3d
OUT=ROOT/'drafts/v21';(OUT/'stl').mkdir(parents=True,exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
oldroot=ROOT.parents[1]/'outputs/model/v19-draft'
reports=[];meshes=[];solids=[]
for label,suffix in [('standard',''),('flat','_flat_support')]:
 native=load(ROOT/'work-native'/f'{label}_body.stl');old=load(oldroot/f'760867899_v19_draft{suffix}.stl')
 # Preserve measured upper fixtures, overlapping the plate by 0.05 mm for a robust union.
 fixturebox=mf.Manifold.cube([42,40,20]).translate([-1,-20,2.5])
 result=native+(old^fixturebox)
 raw=result.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v21{suffix}.stl';mesh.export(path)
 check=trimesh.load_mesh(path,process=True)
 # Graph components without networkx.
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;graph=coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces)))
 components=connected_components(graph,directed=False,return_labels=False)
 report={'variant':label,'watertight':bool(check.is_watertight),'consistent_winding':bool(check.is_winding_consistent),'components':int(components),'volume_mm3':float(check.volume),'extents_mm':check.extents.tolist(),'native_body_valid':json.loads((ROOT/'work-native'/f'{label}_native.json').read_text())['native_valid'],'physical_fit_verified':False}
 assert report['watertight'] and report['consistent_winding'] and components==1 and check.volume>0,report
 reports.append(report);meshes.append(check);solids.append(result)
 print(report,flush=True)
(OUT/'checks.json').write_text(json.dumps(reports,indent=2))
fig=plt.figure(figsize=(12,6),facecolor='white')
for i,(mesh,title) in enumerate(zip(meshes,['Standard support','Flat-backed support']),1):
 ax=fig.add_subplot(1,2,i,projection='3d');draw_3d(ax,mesh,-18,110);ax.set_title(title)
fig.suptitle('v21 · contour-following recess and CAD edge treatment',fontsize=16)
fig.tight_layout();fig.savefig(OUT/'previews/clip.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='white')
params=json.loads((ROOT/'work-native/parameters.json').read_text())
for ax,solid,title in zip(axes,solids,['Standard support','Flat-backed support']):
 draw(ax,side(solid),'#bdd9e7','#2a5570',True)
 pocket=mf.CrossSection([np.array(pts) for pts in params['pocket_contours']]);draw(ax,pocket,'#769db5','#2a5570')
 ax.set_aspect('equal');ax.set_xlim(0,36);ax.set_ylim(-19,11);ax.set_title(title);ax.set_xlabel('Length (mm)');ax.set_ylabel('Height (mm)');ax.grid(alpha=.15)
fig.suptitle('v21 · recess follows the support and curved hook boundary',fontsize=15)
fig.tight_layout();fig.savefig(OUT/'previews/recess.png',dpi=160);plt.close(fig)
