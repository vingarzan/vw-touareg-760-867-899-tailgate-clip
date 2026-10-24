"""Verify edge relief in the other axis using actual Y/Z sections."""
import trimesh
import numpy as np
from verify_dimensions import axis_crossings


def verify_width_edges(path):
    mesh=trimesh.load_mesh(path,process=True)
    results=[]
    for sign in [-1,1]:
        rows=[]
        for y in [0,8.44,8.50,8.57,8.64]:
            zs=axis_crossings(mesh,sign*y,[33.4,0],[0,1])
            assert len(zs)==2,('tip section missing',sign,y,zs)
            rows.append({'y_mm':sign*y,'upper_z_mm':float(zs.max()),'lower_z_mm':float(zs.min())})
        drop=rows[0]['upper_z_mm']-rows[-1]['upper_z_mm']
        assert drop>.1,('width edge is still sharp',sign,drop)
        assert rows[-2]['upper_z_mm']>rows[-1]['upper_z_mm']
        assert rows[-2]['lower_z_mm']<rows[-1]['lower_z_mm']
        results.append({'side':sign,'upper_corner_relief_mm':drop,'sections':rows})
    return results
