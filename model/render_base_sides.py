"""Compare actual base-height sections of two exported STL revisions.

Usage: python model/render_base_sides.py old.stl new.stl preview.png
"""
import sys
import os
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as mf
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache'/'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch


def section(path):
    m=trimesh.load_mesh(path,process=True)
    solid=mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
    assert solid.status()==mf.Error.NoError
    return solid.slice(1.25)


def draw(ax,cs,color,edge):
    points=[];codes=[]
    for a in cs.to_polygons():
        a=np.asarray(a)[:,[1,0]]
        points.extend(a.tolist()+[a[0].tolist()])
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
    ax.add_patch(PathPatch(PlotPath(points,codes),facecolor=color,edgecolor=edge,lw=1.3))


def render(old_path,new_path,out):
    old=section(old_path);new=section(new_path);removed=old-new
    fig,axes=plt.subplots(2,1,figsize=(11,7.2),facecolor='white')
    for ax,cs,title,width in zip(axes,[old,new],['v10 · tabs highlighted in orange','v11 · crossbar flush with base sides'],[27.6,26.3]):
        draw(ax,cs,'#b9d1df','#234a63')
        if cs is old:draw(ax,removed,'#e89b55','#b35b27')
        for y in [-13.15,13.15]:ax.axvline(y,color='#2d7050',ls='--',lw=1)
        ax.annotate('',xy=(-width/2,29.15),xytext=(width/2,29.15),arrowprops={'arrowstyle':'<->','color':'#234a63'})
        ax.text(0,29.3,f'{width:.1f} mm',ha='center',fontsize=11,bbox={'facecolor':'white','edgecolor':'none','pad':1})
        ax.text(0,25,'Mounting base',ha='center',fontsize=11,color='#234a63')
        ax.set_xlim(-15,15);ax.set_ylim(23,31.5);ax.set_aspect('equal');ax.grid(alpha=.12)
        ax.set_title(title,fontsize=13);ax.set_xlabel('Width · mm');ax.set_ylabel('Toward hook · mm')
    fig.suptitle('Hook-end base sides · actual STL sections at mid-wall height',fontsize=15,y=.98)
    fig.text(.5,.028,'Removed 0.65 mm per side · dashed lines mark the 26.3 mm base width',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(out,dpi=170);plt.close(fig)
    print('Removed section area:',removed.area(),'mm²')


if __name__=='__main__':render(*map(Path,sys.argv[1:4]))
