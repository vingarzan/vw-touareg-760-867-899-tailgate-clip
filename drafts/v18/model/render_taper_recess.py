"""Render actual exported plan/end silhouettes and the recessed support."""
import sys,json
from pathlib import Path
import numpy as np
import trimesh
from render_rounding import load,draw,side,ROOT
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


def render():
    p=json.loads((ROOT/'model/parameters.json').read_text());m=p['measured'];e=p['estimated']
    mesh=trimesh.load_mesh(ROOT/'stl/760867899_clip.stl',process=True);solid=load(ROOT/'stl/760867899_clip.stl')
    fig,axes=plt.subplots(1,2,figsize=(11,8),facecolor='white')
    cs=solid.slice(m['base_wall']/2)
    # Swap XY to show peg end at bottom, as in the approved draft.
    draw(axes[0],cs.transform([[0,1,0],[1,0,0]]),'#b9d1df','#234a63')
    features=mesh.triangles[np.all(mesh.triangles[:,:,2]>m['base_wall']-.001,axis=1)]
    axes[0].add_collection(PolyCollection(features[:,:,[1,0]],facecolors='#597f98',edgecolors='none',alpha=.8))
    for x,w,label in [(0,14,'14 mm'),(10,27.6,'27.6 mm'),(34.3,26.2,'26.2 mm')]:
        axes[0].annotate('',xy=(-w/2,x),xytext=(w/2,x),arrowprops={'arrowstyle':'<->','color':'#28734d'})
        axes[0].text(0,x+.8,label,ha='center',color='#28734d',bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':1})
    axes[0].set_xlim(-17,17);axes[0].set_ylim(-2,38);axes[0].set_title('Mounting face · actual STL top view');axes[0].set_xlabel('Width · Y (mm)');axes[0].set_ylabel('From peg end · X (mm)')
    hook=mesh.triangles[np.all(mesh.triangles[:,:,2]<-.001,axis=1)]
    projection=hook[:,:,[1,2]].copy();projection[:,:,1]*=-1
    axes[1].add_collection(PolyCollection(projection,facecolors='#b9d1df',edgecolors='none'))
    for depth,w,label in [(6,20,'20 mm halfway target'),(13.2,17,'17 mm narrow end')]:
        axes[1].annotate('',xy=(-w/2,depth),xytext=(w/2,depth),arrowprops={'arrowstyle':'<->','color':'#28734d'})
        axes[1].text(0,depth+.8,label,ha='center',color='#28734d',bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':1})
    axes[1].set_xlim(-17,17);axes[1].set_ylim(20,-2);axes[1].set_title('Hook/support · actual STL end view');axes[1].set_xlabel('Width · Y (mm)');axes[1].set_ylabel('Depth below base (mm)')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle(p['revision']+' · measured taper profiles in the exported model',fontsize=16)
    fig.tight_layout(rect=(0,.03,1,.94));fig.savefig(ROOT/'previews/taper_actual.png',dpi=170);plt.close(fig)
    fig=plt.figure(figsize=(12,6),facecolor='white')
    ax=fig.add_subplot(121);draw(ax,side(solid),'#b9d1df','#234a63',True)
    # Recess footprint shown in the side view; the cut is shallow along Y.
    import manifold3d as mf
    pocket=mf.CrossSection([np.array([[15.8,-1.3],[28.2,-1.3],[21.8,-9.7]])])
    pocket=pocket.offset(-e['side_recess_corner_radius']).offset(e['side_recess_corner_radius'])
    draw(ax,pocket,'#789eb7','#355a72')
    ax.set_xlim(0,36);ax.set_ylim(-19,12);ax.set_aspect('equal');ax.grid(alpha=.15)
    ax.set_xlabel('Length · X (mm)');ax.set_ylabel('Height · Z (mm)');ax.set_title('Swept support · recess footprint highlighted')
    ax.annotate('0.6 mm side recess',xy=(22,-4.5),xytext=(4,-9),arrowprops={'arrowstyle':'->'},fontsize=11)
    ax3=fig.add_subplot(122,projection='3d')
    from build import draw_3d
    draw_3d(ax3,mesh,14,110);ax3.set_title('Actual exported surface · standard version')
    fig.suptitle(p['revision']+' · smoother hook-to-base sweep and rounded side recess',fontsize=16)
    fig.text(.5,.025,'Recess/profile dimensions are photo estimates · mating dimensions remain constrained by measurements',ha='center',fontsize=10,color='#555')
    fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(ROOT/'previews/support_recess.png',dpi=170);plt.close(fig)


if __name__=='__main__':render()
