import sys,json,numpy as np,trimesh,manifold3d as mf
from pathlib import Path
sys.path.insert(0,'model')
from build import hook_profile
from shape_profiles import base_halfwidth,hook_halfwidth
p=json.load(open('model/parameters.json'));p['revision']='v21'
_,dim=hook_profile();p['native_dimensions']=list(dim)
x=np.unique(np.r_[np.linspace(10,34.3,41),17.15]);p['base_front_samples']=[[float(t),float(base_halfwidth(t,p))] for t in x]
a=np.linspace(0,np.pi/2,41);p['base_rear_samples']=[[float(10*(1-np.cos(t))),float(7+6.8*np.sin(t))] for t in a]
d=np.linspace(0,12,41);p['hook_taper_samples']=[[float(hook_halfwidth(t,p)),float(-t)] for t in d]
mesh=trimesh.load_mesh('../../outputs/model/v19-draft/760867899_v19_draft.stl',process=True)
solid=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
cs=solid.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(0)
clip=mf.CrossSection([np.array([[10,-10.5],[29.2,-10.5],[29.2,-1.2],[10,-1.2]])])
pocket=(cs.offset(-1.1)^clip).offset(-.6).offset(.6).simplify(.01)
p['pocket_contours']=[a.tolist() for a in pocket.to_polygons()]
Path('work-native/parameters.json').write_text(json.dumps(p,indent=2)+'\n')
print('Pocket outline points',[len(a) for a in p['pocket_contours']])
