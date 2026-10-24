"""Export and check the separate rear-to-hook flat-support print variant."""
import copy,math,json
from pathlib import Path
import numpy as np
import trimesh
from verify_dimensions import check_export
from verify_hook_test import check_hook_test,solid

ROOT=Path(__file__).resolve().parents[1]


def export_variant(parameters,build,as_mesh,save):
    variant,_,dim=build(flat_support=True)
    mesh=as_mesh(variant)
    design=save(mesh,'760867899_clip_flat_support.stl')
    e=parameters['estimated'];cx,cz,ri,ro,_=dim
    p=np.array([e['flat_support_rear_x'],e['flat_support_rear_z']]);c=np.array([cx,cz])
    w=p-c;d2=float(w@w);perp=np.array([-w[1],w[0]])
    q=min([c+ro*ro/d2*w+sign*ro*math.sqrt(d2-ro*ro)/d2*perp for sign in [-1,1]],key=lambda a:a[0])
    angle=math.atan2(q[1]-p[1],q[0]-p[0])
    oriented=mesh.copy();oriented.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,1,0]))
    oriented.apply_translation(-oriented.bounds[0])
    ready=save(oriented,'760867899_clip_on_flat_support.stl')
    actual=trimesh.load_mesh(ROOT/'stl/760867899_clip_on_flat_support.stl',process=True)
    contact=np.all(abs(actual.triangles[:,:,2])<.00001,axis=1)
    contact_area=float(actual.area_faces[contact].sum())
    assert contact_area>300,('flat face has insufficient contact area',contact_area)
    assert abs(actual.bounds[0,2])<.00001
    assert abs(design['volume_mm3']-ready['volume_mm3'])<.01
    normal=np.array([-math.sin(angle),0,math.cos(angle)])
    signed=(mesh.vertices-np.array([p[0],0,p[1]]))@normal
    assert signed.min()>-.00001,('geometry extends below support face',signed.min())
    # Verify this variant using its own rear-support datum, not the standard slope.
    settings=copy.deepcopy(parameters)
    settings['estimated']['back_link_start_x']=p[0]
    settings['estimated']['back_link_top_z']=p[1]
    settings['construction']['flat_support_variant']=True
    dimensions=check_export(ROOT/'stl/760867899_clip_flat_support.stl',settings)
    standard=trimesh.load_mesh(ROOT/'stl/760867899_clip.stl',process=True)
    standard_solid=solid(standard);variant_solid=solid(mesh)
    removed=abs((standard_solid-variant_solid).volume())
    assert removed<.002,('variant unexpectedly removes standard features',removed)
    # All changes must lie on the underside of the base; no alterations to fins/peg/latch.
    import manifold3d as mf
    above=mf.Manifold.cube([40,40,20]).translate([-1,-20,parameters['measured']['base_wall']-.0001])
    a=standard_solid^above;b=variant_solid^above
    difference=abs(((a-b)+(b-a)).volume())
    assert difference<.002,('upper features changed',difference)
    _,coupon,_=build()
    coupon_design=as_mesh(coupon)
    mating=check_hook_test(ROOT/'stl/760867899_hook_fit_test.stl',ROOT/'stl/760867899_clip_flat_support.stl',parameters,dim,coupon_design.bounds)
    result={'revision':parameters['revision'],'files':[design,ready],
            'support_plane_rear_xz_mm':p.tolist(),'support_plane_tangent_xz_mm':q.tolist(),
            'rotation_about_y_degrees':math.degrees(angle),'bed_contact_area_mm2':contact_area,
            'entire_model_above_support_plane':True,'standard_material_removed_mm3':removed,
            'upper_features_difference_mm3':difference,
            'added_volume_mm3':variant_solid.volume()-standard_solid.volume(),
            'exported_stl_sections':dimensions,'hook_gauge_mating_checks':mating,
            'slicer_toolpaths_verified':False,'physical_fit_verified':False}
    (ROOT/'validation/flat_support_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    from render_flat_support import render
    render(mesh,actual,standard,p,q,parameters)
    return result
