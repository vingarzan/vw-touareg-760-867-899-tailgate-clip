import sys,json,math
from pathlib import Path
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'model'))
from verify_dimensions import axis_crossings
p=json.loads((ROOT/'work-native/parameters.json').read_text());cx,cz,ri,ro,_=p['native_dimensions'];out=ROOT/'drafts/v21'
checks=json.loads((out/'checks.json').read_text())
for r,suf in zip(checks,['','_flat_support']):
 mesh=trimesh.load_mesh(out/'stl'/f'760867899_v21{suf}.stl')
 hit=axis_crossings(mesh,0,np.array([cx,cz]),np.array([0,1]));pos=hit[hit>0];neg=hit[hit<0];bore=pos.min()-neg.max();assert abs(bore-9.7)<.02
 r['central_hook_bore_mm']=float(bore)
 if suf:
  dx=-cx;dz=-cz;d2=dx*dx+dz*dz;fac=ro*math.sqrt(d2-ro*ro)/d2
  q=min([(cx+ro*ro/d2*dx+s*fac*(-dz),cz+ro*ro/d2*dz+s*fac*dx) for s in [-1,1]])
  normal=np.array([-q[1],0,q[0]]);normal/=np.linalg.norm(normal)
  distances=mesh.vertices@normal
  assert distances.min()>-.015
  contact=mesh.area_faces[np.max(abs(mesh.triangles@normal),axis=1)<.015].sum();assert contact>300
  r['flat_face_contact_mm2']=float(contact);r['support_plane_min_mm']=float(distances.min())
print(json.dumps(checks,indent=2));(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
