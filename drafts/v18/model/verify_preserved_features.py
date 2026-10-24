"""Compare sharp features with a previous exported revision.
Usage: python model/verify_preserved_features.py previous_clip.stl
"""
import sys,json
from pathlib import Path
import manifold3d as mf
from render_rounding import load,ROOT


def verify(previous):
    old=load(previous);new=load(ROOT/'stl/760867899_clip.stl')
    regions={
        'sharp_mounting_base':([-1,-14,.0001],[32,28,2.5498]),
        'unchanged_peg':([0,-6,2.5501],[11,12,7]),
        'unchanged_retaining_clip':([18,-7.6,2.5501],[13,15.2,7])}
    report={'revision':'v12','comparison_revision':'v11','feature_differences_mm3':{}}
    for name,(origin,size) in regions.items():
        mask=mf.Manifold.cube(size).translate(origin);a=old^mask;b=new^mask
        difference=abs(((a-b)+(b-a)).volume())
        assert difference<.002,(name,difference)
        report['feature_differences_mm3'][name]=difference
    old_peg=previous.parent/'760867899_peg_fit_test.stl'
    report['peg_fit_test_byte_identical']=(old_peg.read_bytes()==(ROOT/'stl/760867899_peg_fit_test.stl').read_bytes())
    assert report['peg_fit_test_byte_identical']
    report['physical_fit_verified']=False
    (ROOT/'validation/v12_preserved_features.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':verify(Path(sys.argv[1]))
