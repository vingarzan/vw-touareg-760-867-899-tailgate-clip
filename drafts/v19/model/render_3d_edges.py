"""Show the edge fillet across the hook width, rather than another side view."""
import sys,json
from pathlib import Path
import numpy as np
import trimesh
from render_rounding import load,draw,ROOT
import matplotlib.pyplot as plt


def render(previous):
    settings=json.loads((ROOT/'model/parameters.json').read_text())
    revision=settings['revision'];radius=settings['estimated']['hook_edge_fillet_3d_radius']
    old=load(previous);current=load(ROOT/'stl/760867899_clip.stl')
    trans=[[0,1,0,0],[0,0,1,0],[1,0,0,0]]
    fig=plt.figure(figsize=(11,5.8),facecolor='white')
    ax=fig.add_subplot(121)
    draw(ax,current.transform(trans).slice(33.4),'#b9d1df','#234a63')
    draw(ax,old.transform(trans).slice(33.4),'none','#c46a2e')
    ax.set_xlim(8.05,8.8);ax.set_ylim(-13.3,-12.6);ax.set_aspect('equal');ax.grid(alpha=.18)
    ax.set_xlabel('Across width · Y (mm)');ax.set_ylabel('Height · Z (mm)')
    ax.set_title('End-on section · top-right tip corner')
    ax.annotate('3D fillet',xy=(8.60,-12.94),xytext=(8.34,-13.04),fontsize=11,arrowprops={'arrowstyle':'->'})
    ax3=fig.add_subplot(122,projection='3d')
    mesh=trimesh.load_mesh(ROOT/'stl/760867899_clip.stl',process=True)
    mesh.update_faces(mesh.triangles_center[:,0]>31.1);mesh.remove_unreferenced_vertices()
    from build import draw_3d
    draw_3d(ax3,mesh,28,38);ax3.set_box_aspect(mesh.extents.copy())
    lo,hi=mesh.bounds
    ax3.set_xlim(lo[0]-.2,hi[0]+.2);ax3.set_ylim(lo[1]-.2,hi[1]+.2);ax3.set_zlim(lo[2]-.2,hi[2]+.2)
    ax3.set_title('Actual hook-tip mesh · across-width edges',fontsize=12)
    fig.suptitle(revision+' · larger hook edge fillet',fontsize=17)
    fig.text(.5,.025,f'Blue: current STL · orange: previous R0.2 edge · new nominal R{radius:g} hook-side fillet',ha='center',fontsize=10,color='#555')
    fig.tight_layout(rect=(0,.14,1,.94));fig.savefig(ROOT/'previews/hook_3d_edges.png',dpi=180);plt.close(fig)


if __name__=='__main__':render(Path(sys.argv[1]))
