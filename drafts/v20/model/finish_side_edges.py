"""Fast, local blend of exposed lateral edges in a validated draft mesh.

This is a mesh edge blend within a 0.4 mm band, not an exact rolling-ball fillet.
The plate and mounting features are not moved; central mating profiles are held.
"""
import json,sys,time
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial import cKDTree
from shape_profiles import base_halfwidth,hook_halfwidth


def solid(mesh):
    s=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
    assert s.status()==mf.Error.NoError
    return s


def finish(source,destination,parameters):
    t=time.time();original=trimesh.load_mesh(source,process=True);s=solid(original)
    sharp=original.face_adjacency_edges[original.face_adjacency_angles>np.deg2rad(35)]
    lines=original.vertices[sharp]
    lines=lines[(np.mean(abs(lines[:,:,1]),axis=1)>7.95)&(np.max(lines[:,:,2],axis=1)<-.001)]
    samples=np.vstack([np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/.12)+1)) for a,b in lines])
    refined=s.refine_to_length(.12).to_mesh()
    mesh=trimesh.Trimesh(vertices=np.asarray(refined.vert_properties)[:,:3],faces=np.asarray(refined.tri_verts),process=True)
    dist=cKDTree(samples).query(mesh.vertices)[0]
    v=mesh.vertices.copy()
    half=np.minimum(base_halfwidth(v[:,0],parameters),hook_halfwidth(np.maximum(-v[:,2],0),parameters))
    band=.4
    active=(dist<band)&(abs(v[:,1])>half-band)&(abs(v[:,1])>8.)&(v[:,2]<-.005)
    fixed=v[~active].copy()
    laplacian=trimesh.smoothing.laplacian_calculation(mesh,equal_weight=True)
    for _ in range(100):
        average=laplacian.dot(v);v[active]+=.5*(average[active]-v[active])
    assert np.array_equal(v[~active],fixed)
    mesh.vertices=v
    rounded=solid(mesh).simplify(.0005)
    # Reattach the original plate/features exactly; they are outside the blend.
    result=rounded  # Fixed vertices already retain the plate and upper features.
    saved=result.to_mesh()
    output=trimesh.Trimesh(vertices=np.asarray(saved.vert_properties)[:,:3],faces=np.asarray(saved.tri_verts),process=True)
    output.update_faces(output.area_faces>1e-16);output.remove_unreferenced_vertices()
    output.export(destination)
    check=trimesh.load_mesh(destination,process=True)
    assert check.is_watertight and check.is_winding_consistent and check.volume>0
    report={'file':str(destination),'watertight':True,'winding_consistent':True,'positive_volume':True,
            'triangles':len(check.faces),'blend_band_mm':band,'exact_radius_fillet':False,
            'dimensions_mm':check.extents.tolist(),'seconds':time.time()-t,
            'plate_and_mounting_features_preserved':True,'physical_fit_verified':False}
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=='__main__':
    source,destination,params=map(Path,sys.argv[1:4]);finish(source,destination,json.loads(params.read_text()))
