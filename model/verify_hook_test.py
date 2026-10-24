"""Verify the printable hook gauge from its saved STL and compare the mating profile."""
import math
import numpy as np
import trimesh
import manifold3d as mf
from verify_dimensions import axis_crossings


def solid(mesh):
    q=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),
                          np.asarray(mesh.faces,dtype=np.uint32)))
    assert q.status()==mf.Error.NoError
    return q


def check_hook_test(test_path,clip_path,parameters,dim,design_bounds):
    test=trimesh.load_mesh(test_path,process=True)
    clip=trimesh.load_mesh(clip_path,process=True)
    mm=parameters['measured'];ee=parameters['estimated']
    height=float(test.extents[2])
    assert abs(test.bounds[0,2])<1e-6
    assert abs(height-ee['coupon_width'])<.001
    contact=np.all(abs(test.triangles[:,:,2])<1e-6,axis=1)
    contact_area=float(test.area_faces[contact].sum())
    section_area=float(test.volume/height)
    assert abs(contact_area-section_area)<.001,('partial bed contact',contact_area,section_area)
    printable=solid(test)
    sections=[printable.slice(z) for z in [0.001,height/2,height-.001]]
    differences=[((s-sections[1])+(sections[1]-s)).area() for s in sections]
    assert max(differences)<.001,('gauge is not a constant side-printed profile',differences)
    # Undo the bed placement: X=x+xmin, Y=z+ymin, Z=-y+zmax.
    lo,hi=np.asarray(design_bounds)
    transform=np.array([[1,0,0,lo[0]],[0,0,1,lo[1]],[0,-1,0,hi[2]],[0,0,0,1]])
    restored=test.copy();restored.apply_transform(transform)
    cx,cz,ri,ro,half=dim
    region=mf.Manifold.cylinder(height,ri+.25,ri+.25,180).transform([
        [1,0,0,cx],[0,0,-1,height/2],[0,1,0,cz]])
    a=solid(restored)^region;b=solid(clip)^region
    mismatch=abs(((a-b)+(b-a)).volume())
    assert mismatch<.005,('gauge mating profile differs from complete clip',mismatch)
    direction=math.radians(ee['hook_opening_direction_degrees'])
    u=np.array([math.cos(direction),math.sin(direction)])
    v=np.array([-math.sin(direction),math.cos(direction)])
    center=np.array([cx,cz]);lip=math.sqrt(ri*ri-(mm['hook_mouth']/2)**2)
    measurements=[]
    for y in [-height/2+.1,0,height/2-.1]:
        ts=axis_crossings(restored,y,center,[0,1])
        diameter=float(ts[ts>0].min()-ts[ts<0].max())
        assert abs(diameter-mm['hook_cavity'])<.003
        ts=axis_crossings(restored,y,center+u*(lip+.0001),v)
        mouth=float(ts[ts>0].min()-ts[ts<0].max())
        assert mm['hook_mouth']-.003<=mouth<=mm['hook_mouth']+.13
        ts=axis_crossings(restored,y,center,u)
        projection=float(ts[ts<0].max()+ri)
        assert abs(projection-mm['hook_internal_rib_projection'])<.003
        ts=axis_crossings(restored,y,center+u*(-ri+projection/2),v)
        tooth_height=float(ts[ts>0].min()-ts[ts<0].max())
        assert abs(tooth_height-mm['hook_internal_rib_height'])<.003
        for offset in np.linspace(-mm['hook_mouth']/2+.05,mm['hook_mouth']/2-.05,17):
            ts=axis_crossings(restored,y,center+v*offset,u)
            assert not np.any(ts>lip+.003),('blocked hook test mouth',y,float(offset))
        measurements.append({'y_mm':y,'inside_diameter_mm':diameter,'mouth_mm':mouth,
                             'tooth_projection_mm':projection,'tooth_height_mm':tooth_height})
    return {
        'file':'stl/760867899_hook_fit_test.stl',
        'print_dimensions_mm':test.extents.tolist(),
        'print_height_mm':height,
        'flat_contact_area_mm2':contact_area,
        'full_profile_contacts_bed':True,
        'constant_profile_over_print_height':True,
        'maximum_section_difference_mm2':max(differences),
        'geometry_requires_supports':False,
        'mating_region_difference_from_complete_clip_mm3':mismatch,
        'mating_comparison_tolerance_mm3':.005,
        'section_measurements':measurements,
        'unobstructed_entry_rays_checked':51,
        'physical_fit_verified':False,
        'limitation':'A 4 mm-wide gauge checks the mating shape; it does not reproduce full-width stiffness or retention.'
    }
