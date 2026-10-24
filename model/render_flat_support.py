"""Preview the actual added support and the STL oriented onto its flat face."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from render_rounding import draw,side,load

ROOT=Path(__file__).resolve().parents[1]


def render(mesh,oriented,standard,p,q,parameters):
    current=load(ROOT/'stl/760867899_clip_flat_support.stl')
    old=load(ROOT/'stl/760867899_clip.stl')
    fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='white')
    draw(axes[0],side(current),'#b9d1df','#234a63',True)
    draw(axes[0],side(current)-side(old),'#e9ba88','#b5682a',True)
    draw(axes[0],side(old),'none','#234a63',True)
    axes[0].plot([p[0],q[0]],[p[1],q[1]],color='#28734d',lw=2.5)
    axes[0].set_title('Separate variant · added material in orange')
    axes[0].set_xlabel('Length · mm');axes[0].set_ylabel('Height · mm')
    axes[0].set_xlim(-2,37);axes[0].set_ylim(-19,12)
    axes[1].add_collection(PolyCollection(oriented.triangles[:,:,[0,2]],facecolors='#366582',edgecolors='none'))
    lo,hi=oriented.bounds
    axes[1].set_xlim(lo[0]-2,hi[0]+2);axes[1].set_ylim(-2,hi[2]+2)
    axes[1].axhline(0,color='#28734d',lw=2.5)
    axes[1].text((lo[0]+hi[0])/2,-1.4,'Flat support face on the print bed',ha='center',fontsize=10,color='#28734d')
    axes[1].set_title('Supplied print orientation · actual STL silhouette')
    axes[1].set_xlabel('Print X · mm');axes[1].set_ylabel('Print Z · mm')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle(parameters['revision']+' · rear-to-hook flat-support variant',fontsize=17)
    fig.text(.5,.02,'Green: continuous flat support plane · print supports and installation clearance still need checking',ha='center',fontsize=10,color='#555')
    fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(ROOT/'previews/flat_support_profile.png',dpi=170);plt.close(fig)
    from build import draw_3d
    fig=plt.figure(figsize=(11,6),facecolor='white')
    ax=fig.add_subplot(111,projection='3d');draw_3d(ax,oriented,23,-65)
    # A faint bed plane shows the supplied orientation without obscuring the part.
    xx,yy=np.meshgrid([lo[0]-1,hi[0]+1],[lo[1]-1,hi[1]+1])
    ax.plot_surface(xx,yy,np.zeros_like(xx),color='#8fc4a4',alpha=.18,shade=False)
    ax.set_title('v13 · flat-support variant on its supplied print face',fontsize=16,pad=15)
    fig.text(.5,.025,'Full part geometry · not sliced or physically printed',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(ROOT/'previews/flat_support_print.png',dpi=170);plt.close(fig)
