"""Close-up comparison of the rounded hook free tip against the prior envelope."""
import math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from render_rounding import load,draw,side
ROOT=Path(__file__).resolve().parents[1]


def render_tip(parameters):
    m=parameters['measured'];e=parameters['estimated']
    ri=m['hook_cavity']/2;ro=m['hook_drop_from_mounting_surface']-m['hook_base_to_nearest_inside']-ri
    theta=math.radians(e['hook_opening_direction_degrees'])-math.asin(m['hook_mouth']/(2*ri))
    c=np.array([m['length']-ro*math.cos(theta),m['base_wall']-m['hook_drop_from_mounting_surface']+ro])
    u=np.array([math.cos(theta),math.sin(theta)]);v=np.array([-math.sin(theta),math.cos(theta)])
    fig,ax=plt.subplots(figsize=(8,6.5),facecolor='white')
    draw(ax,side(load(ROOT/'stl/760867899_clip.stl')),'#b9d1df','#234a63',True)
    # Previous radial cap (sharp envelope) for an explicit before/after outline.
    sharp=np.array([c+ri*u,c+ro*u]);ax.plot(sharp[:,0],sharp[:,1],color='#bf642c',lw=1.5,ls='--')
    for label,R,r,sign,offset in [('Outside R0.6',ro,e['hook_free_tip_outer_radius'],-1,[.1,1.4]),('Inside R0.25',ri,e['hook_free_tip_inner_radius'],1,[-1.0,.8])]:
        a=math.sqrt(R*R+sign*2*R*r);center=c+a*u-r*v
        arcpoint=center+r*np.array([math.cos(theta+math.pi/2-.3),math.sin(theta+math.pi/2-.3)])
        ax.annotate(label,xy=arcpoint,xytext=center+offset,fontsize=12,color='#28734d',arrowprops={'arrowstyle':'->','color':'#28734d'})
    ax.set_xlim(31.1,34.9);ax.set_ylim(-14.7,-10.2);ax.set_aspect('equal');ax.grid(alpha=.15)
    ax.set_xlabel('Length · mm');ax.set_ylabel('Height · mm')
    ax.set_title(parameters['revision']+' · rounded hook free tip\nBoth standard and flat-support versions',fontsize=15)
    fig.text(.5,.02,'Actual STL section · dashed orange: previous sharp end face',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(ROOT/'previews/rounded_tip.png',dpi=170);plt.close(fig)
