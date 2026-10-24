"""Render a dimensioned section of the exported STL, not a separate sketch."""
import math
import numpy as np
import manifold3d as mf
import trimesh
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt


def render_section(stl_path, parameters, out_path):
    m=trimesh.load_mesh(stl_path,process=True)
    # Reconstruct the saved mesh and slice through its actual middle plane.
    solid=mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),
                              np.asarray(m.faces,dtype=np.uint32)))
    assert solid.status()==mf.Error.NoError
    contours=solid.transform([[1,0,0,0],[0,0,-1,0],[0,1,0,0]]).slice(0).to_polygons()
    points=[]; codes=[]
    for contour in contours:
        a=np.asarray(contour).copy();a[:,1]*=-1
        points.extend(a.tolist()+[a[0].tolist()])
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(a)-1)+[PlotPath.CLOSEPOLY])
    mm=parameters['measured'];ee=parameters['estimated']
    ri=mm['hook_cavity']/2;ro=mm['hook_drop_from_mounting_surface']-mm['hook_base_to_nearest_inside']-ri
    direction=math.radians(ee['hook_opening_direction_degrees'])
    half=math.asin(mm['hook_mouth']/(2*ri))
    cx=mm['length']-ro*math.cos(direction-half)
    bottom=float(m.bounds[0,2]);cz=bottom+ro
    u=np.array([math.cos(direction),math.sin(direction)])
    v=np.array([-math.sin(direction),math.cos(direction)])
    def point(a,b):return np.array([cx,cz])+u*a+v*b
    root=-ri;tip=root+mm['hook_internal_rib_projection']
    fig,ax=plt.subplots(figsize=(8,8),facecolor='white')
    ax.add_patch(PathPatch(PlotPath(points,codes),facecolor='#b9d1df',edgecolor='#234a63',lw=1.5))
    # Highlight the actual tooth's exposed edges.
    h=mm['hook_internal_rib_height']/2
    edge=np.array([point(root,-h),point(tip,-h),point(tip,h),point(root,h)])
    ax.plot(edge[:,0],edge[:,1],color='#bf5e23',lw=2)
    ax.annotate('',xy=point(root,h+1.0),xytext=point(tip,h+1.0),
                arrowprops={'arrowstyle':'<->','color':'#bf5e23'})
    ax.text(*point((root+tip)/2,h+1.4),'1.4 mm',ha='center',rotation=math.degrees(direction),fontsize=10,color='#a14c1a')
    ax.annotate('',xy=point(tip+.55,-h),xytext=point(tip+.55,h),
                arrowprops={'arrowstyle':'<->','color':'#bf5e23'})
    ax.text(*point(tip+1.0,0),'1.4 mm',va='center',rotation=math.degrees(direction)-90,fontsize=10,color='#a14c1a')
    diameter=np.array([point(root-.3,0),point(ri+.8,0)])
    ax.plot(diameter[:,0],diameter[:,1],color='#888',lw=.7,ls=':')
    lip=np.array([cx,cz])+u*math.sqrt(ri*ri-(mm['hook_mouth']/2)**2)
    from verify_dimensions import axis_crossings
    ts=axis_crossings(m,0,lip,v)
    high=float(ts[ts>0].min());low=float(ts[ts<0].max())
    p=lip+v*high;q=lip+v*low
    ax.annotate('',xy=p,xytext=q,arrowprops={'arrowstyle':'<->','color':'#a14c1a','lw':1.5})
    label=lip+u*.8
    ax.text(*label,f'{high-low:.2f} mm open',rotation=-60,ha='left',va='center',fontsize=11,color='#a14c1a',
            bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
    zface=mm['base_wall'];dx=mm['length']+2.5
    ax.hlines([zface,bottom],dx-.7,dx+.7,color='#555',lw=.9)
    ax.annotate('',xy=(dx,bottom),xytext=(dx,zface),arrowprops={'arrowstyle':'<->','color':'#555'})
    ax.text(dx+.4,(bottom+zface)/2,'20 mm from mounting face',rotation=90,ha='left',va='center',fontsize=11)
    ax.hlines(zface,cx-ro-3.0,dx,colors='#555',linestyles=':',lw=1)
    ax.text(cx-ro-2.8,zface+.35,'Flat mounting face',fontsize=10,color='#555')
    gap_x=cx-5.5
    ax.annotate('',xy=(gap_x,cz+ri),xytext=(gap_x,zface),
                arrowprops={'arrowstyle':'<->','color':'#2d7050','lw':1.5})
    ax.hlines(cz+ri,gap_x-.5,cx,colors='#2d7050',linestyles=':',lw=.8)
    ax.text(gap_x-.35,(zface+cz+ri)/2,'7.7 mm to nearest inside',rotation=90,
            va='center',ha='right',fontsize=10,color='#2d7050',
            bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':2})
    ax.annotate('Solid link to base',xy=(25.0,-3.6),xytext=(23.0,-1.1),
                fontsize=11,color='#234a63',
                arrowprops={'arrowstyle':'->','color':'#234a63'})
    ax.scatter([cx],[cz],s=12,color='#555')
    ax.text(cx,cz-ri*.72,f"Ø {mm['hook_cavity']:.1f} mm",ha='center',
            va='center',fontsize=11,color='#234a63',
            bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
    ax.set_xlim(cx-ro-3.5,dx+2);ax.set_ylim(bottom-1.5,zface+1.5)
    ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_xlabel('X · mm');ax.set_ylabel('Z · mm')
    ax.set_title(f"{parameters['revision']} · actual STL centre section\n1.4 × 1.4 mm tooth opposite the opening",fontsize=15,pad=16)
    fig.text(.5,.02,'Geometry preview only · physical fit remains untested',ha='center',fontsize=10,color='#555')
    fig.tight_layout(rect=(0,.035,1,1));fig.savefig(out_path,dpi=170);plt.close(fig)
