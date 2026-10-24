from pathlib import Path
import json,numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());p['revision']='v26'
m=trimesh.load_mesh(ROOT/'drafts/v25/stl/760867899_v25_existing_flat_support.stl',process=True)
s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
profile=s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(0)
# Offset the actual FLAT-backed silhouette, not the standard support profile.
window=mf.CrossSection([np.array([[0,-10.5],[29.2,-10.5],[29.2,-1.2],[0,-1.2]])])
pocket=(profile.offset(-1.1)^window).offset(-.6).offset(.6).simplify(.01)
p['pocket_contours']=[a.tolist() for a in pocket.to_polygons()]
(HERE/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
print('Flat-back recess bounds',pocket.bounds())
