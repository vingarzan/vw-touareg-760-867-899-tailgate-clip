"""Inspect the reinforced peg from sections of its exported fit-test STL."""
import math
import numpy as np
import trimesh
import manifold3d as mf
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch,Polygon


def patch_from_section(solid,transform):
    contours=solid.transform(transform).slice(0).to_polygons()
    points=[];codes=[]
    for contour in contours:
        a=np.asarray(contour).copy();a[:,1]*=-1
        points.extend(a.tolist()+[a[0].tolist()])
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
    return PathPatch(PlotPath(points,codes),facecolor='#b9d1df',edgecolor='#234a63',lw=1.4)


def render_peg_section(path,parameters,out_path):
    m=trimesh.load_mesh(path,process=True)
    solid=mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
    assert solid.status()==mf.Error.NoError
    e=parameters['estimated'];measured=parameters['measured']
    fig,axes=plt.subplots(1,2,figsize=(11,6),facecolor='white')
    c=math.sqrt(.5)
    axes[0].add_patch(patch_from_section(solid,[[c,c,0,-14*c],[0,0,-1,0],[-c,c,0,0]]))
    floor=e['peg_slot_root_z'];top=floor+e['peg_root_collar_height']
    r0=e['peg_root_inner_radius'];r1=e['peg_inner_diameter']/2
    for sign in [-1,1]:
        axes[0].add_patch(Polygon([[sign*r0,floor],[sign*r1,floor],[sign*r1,top]],
                                  facecolor='#d99763',edgecolor='#a55524',lw=1))
    axes[0].annotate('Added inner\nroot collar',xy=(1.6,floor+.3),xytext=(-4.4,1.1),
                     fontsize=11,color='#97481b',arrowprops={'arrowstyle':'->','color':'#97481b'})
    axes[0].set_xlim(-5,5);axes[0].set_ylim(0,9.2)
    axes[0].set_title('Section through two opposite legs',fontsize=12)
    axes[0].set_xlabel('Radial position · mm');axes[0].set_ylabel('Height · mm')
    # Section at X=3 mm from the peg centre reveals the rounded slot bottom.
    axes[1].add_patch(patch_from_section(solid,[[0,1,0,-7],[0,0,-1,0],[1,0,0,-10]]))
    radius=e['peg_slot_width']/2;z=e['peg_slot_round_center_z']
    a=np.linspace(math.pi,2*math.pi,80)
    axes[1].plot(radius*np.cos(a),z+radius*np.sin(a),color='#b35b27',lw=2)
    axes[1].annotate('Rounded slot end',xy=(0,z-radius),xytext=(-1.45,2.8),
                     fontsize=11,color='#97481b',arrowprops={'arrowstyle':'->','color':'#97481b'})
    axes[1].set_xlim(-1.7,1.7);axes[1].set_ylim(2.3,5.8)
    axes[1].set_title('Slot-root detail',fontsize=12)
    axes[1].set_xlabel('Across slot · mm');axes[1].set_ylabel('Height · mm')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle(f"{parameters['revision']} · actual peg fit-test STL sections",fontsize=16,y=.97)
    fig.text(.5,.075,'Outer peg dimensions retained: Ø 7.4 mm root · Ø 8.8 mm barb · 8.5 mm total height',ha='center',fontsize=11,color='#555')
    fig.text(.5,.035,'Added material is highlighted · physical strength and insertion force require a new test',ha='center',fontsize=10,color='#555')
    fig.tight_layout(rect=(0,.16,1,.93));fig.savefig(out_path,dpi=170);plt.close(fig)
