"""Render actual hook and fin sections for reviewing v12 shape changes.
Usage: python model/render_rounding.py previous.stl
"""
import os,sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache'/'matplotlib'))
import numpy as np
import trimesh
import manifold3d as mf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch


def load(path):
    m=trimesh.load_mesh(path,process=True)
    q=mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
    assert q.status()==mf.Error.NoError
    return q


def draw(ax,cs,color,edge,reverse=False):
    points=[];codes=[]
    for a in cs.to_polygons():
        a=np.asarray(a).copy()
        if reverse:a[:,1]*=-1
        points.extend(a.tolist()+[a[0].tolist()])
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
    ax.add_patch(PathPatch(PlotPath(points,codes),facecolor=color,edgecolor=edge,lw=1.4))


def side(solid,y=0):
    return solid.transform([[1,0,0,0],[0,0,-1,0],[0,1,0,0]]).slice(y)


def render(old_path):
    p=json.loads((ROOT/'model/parameters.json').read_text());m=p['measured'];e=p['estimated']
    new=load(ROOT/'stl/760867899_clip.stl');old=load(old_path)
    fig,axes=plt.subplots(1,2,figsize=(11,6),facecolor='white')
    draw(axes[0],side(old),'none','#bf642c',True);draw(axes[0],side(new),'#b9d1df','#234a63',True)
    draw(axes[0],side(old),'none','#bf642c',True)
    axes[0].set_xlim(26.5,31);axes[0].set_ylim(-6,1)
    axes[0].set_title('Upper hook end · side section')
    axes[0].annotate('Continuous curved relief',xy=(29.4,-3.8),xytext=(26.7,-1.8),fontsize=10,arrowprops={'arrowstyle':'->'})
    axes[0].set_xlabel('Length · mm');axes[0].set_ylabel('Height · mm')
    draw(axes[1],new.slice(-15),'#b9d1df','#234a63');draw(axes[1],old.slice(-15),'none','#bf642c')
    axes[1].set_xlim(29.7,33.5);axes[1].set_ylim(7.8,13.7)
    axes[1].set_title('Rounded hook shoulder · horizontal section')
    axes[1].set_xlabel('Length · mm');axes[1].set_ylabel('Half-width · mm')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle('v12 · rounded hook end and shoulders',fontsize=16)
    fig.text(.5,.025,'Blue: current STL · orange outline: v11 · mounting base stays sharp',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(ROOT/'previews/rounded_hook.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,5.5),facecolor='white')
    c=m['guide_outside_width']/2-m['fin_thickness']/2;z0=m['base_wall'];k=math.tan(math.radians(e['fin_inward_lean_degrees']))
    for ax,(name,sign) in zip(axes[:2],[('right',-1),('left',1)]):
        # Undo the actual inward shear before slicing along the fin centre.
        restored=new.transform([[1,0,0,0],[0,1,sign*k,-sign*k*z0],[0,0,1,0]])
        draw(ax,side(restored,sign*c),'#b9d1df','#234a63',True)
        draw(ax,side(old,sign*c),'none','#bf642c',True)
        ax.set_xlim(17.6,28.6);ax.set_ylim(2,10.6);ax.set_aspect('equal')
        ax.set_title(name.capitalize()+' fin · R0.4 tip corners');ax.set_xlabel('Length · mm');ax.set_ylabel('Height · mm')
    start=e['peg_center_from_rear']+m['peg_base_diameter']/2+m['peg_to_fin_edge_gap_along_length']
    trans=[[0,1,0,0],[0,0,1,0],[1,0,0,0]]
    draw(axes[2],old.transform(trans).slice(start+2),'none','#bf642c')
    draw(axes[2],new.transform(trans).slice(start+2),'#b9d1df','#234a63')
    axes[2].set_xlim(-14,14);axes[2].set_ylim(2,11);axes[2].set_aspect('equal');axes[2].set_title('End section · 5° inward lean')
    axes[2].set_xlabel('Width · mm');axes[2].set_ylabel('Height · mm')
    for ax in axes:ax.grid(alpha=.15)
    fig.suptitle('v12 · rounded fin tips with a slight inward lean',fontsize=16)
    fig.text(.5,.025,'Tip shifts inward: right 0.66 mm · left 0.32 mm · roots and heights retained',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(ROOT/'previews/rounded_fins.png',dpi=170);plt.close(fig)


if __name__=='__main__':render(Path(sys.argv[1]))
