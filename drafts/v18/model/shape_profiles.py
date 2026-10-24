"""Approved width profiles; all dimensions in millimetres."""
import numpy as np
from scipy.interpolate import PchipInterpolator


def base_halfwidth(x,p):
    m=p['measured'];q=np.asarray(x,dtype=float)
    rear=m['base_max_width_from_peg_end'];end=p['requested']['base_front_x']
    curve=PchipInterpolator([rear,end/2,end],[m['body_width']/2,13.75,m['base_clip_end_width']/2],extrapolate=False)
    clipped=np.clip(q,rear,end)
    result=curve(clipped)
    rear_curve=m['base_peg_end_width']/2+(m['body_width']-m['base_peg_end_width'])/2*np.sqrt(np.maximum(0,1-(1-np.clip(q,0,rear)/rear)**2))
    return np.where(q<rear,rear_curve,result)


def hook_halfwidth(depth,p):
    m=p['measured'];e=p['estimated'];d=np.asarray(depth,dtype=float)
    end=e['hook_depth_taper_end']
    return PchipInterpolator([0,end/2,end],[m['base_clip_end_width']/2,m['hook_halfway_width']/2,m['hook_lip_width']/2])(np.clip(d,0,end))
