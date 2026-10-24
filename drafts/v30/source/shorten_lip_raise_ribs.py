"""Shorten only the forward lip by 1.5 mm and raise three support ribs to Z=7.2."""
from pathlib import Path
import os,json
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PP
from matplotlib.patches import PathPatch

def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def box(x0,x1,y0,y1,z0,z1):return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def xz(pts,w,y=0):
 a=np.array(pts);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1))
 return mf.CrossSection([a if area>0 else a[::-1]]).extrude(w).transform([[1,0,0,0],[0,0,-1,y+w/2],[0,1,0,0]])
oldbar=np.array([[29.2,5.9],[30.6,5.9],[30.6,5.6],[31.3,6.2],[31.,7.2],[29.2,7.2]])
newbar=oldbar-np.array([1.5,0]);bar=xz(newbar,15)
# Root position retained. Smooth cubic rise meets the top of the cap horizontally.
t=np.linspace(0,1,129)[:,None];p0=np.array([21,2.7]);p1=np.array([23.5,2.7]);p2=np.array([23.75,7.2]);p3=np.array([25.65,7.2])
curve=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
profile=np.vstack([[21,2.4],curve,[28.2,2.4]])
ribs=mf.Manifold.batch_boolean([xz(profile,.95,y) for y in [-5.4,0,5.4]],mf.OpType.Add)
# Front removal window is safely beyond the 115 degree leg and the ribs.
window=box(29.1,31.5,-7.51,7.51,5.55,7.3)
reports=[]
for layout in ['existing','right']:
 old=load(ROOT/'drafts/v29/stl'/f'760867899_v29_{layout}_flat_support.stl');new=(old-window)+bar+ribs
 raw=new.to_mesh();mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
 mesh.merge_vertices(digits_vertex=5);mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
 path=OUT/'stl'/f'760867899_v30_{layout}_flat_support.stl';mesh.export(path);check=trimesh.load_mesh(path,process=True)
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
 print(layout,check.is_watertight,check.is_winding_consistent,components,flush=True)
 assert check.is_watertight and check.is_winding_consistent and components==1
 # Existing lower leg cannot lose material; changed material stays at lip/supports.
 removed=old-new;assert abs((removed-window).volume())<.002
 allowed=window+box(20.99,28.21,-6,6,2.39,7.21)
 diff=((new-old)+(old-new))-allowed;assert abs(diff.volume())<.002
 # All three ribs are continuous up to the cap top, not merely to its underside.
 for y in [-5.4,0,5.4]:
  for z in np.linspace(2.6,7.19,80):
   # A point within the solid rib, moving from root to its cap attachment.
   xx=27.9-(z-2.6)*.49
   probe=box(xx-.025,xx+.025,y-.2,y+.2,z-.002,z+.002)
   assert (probe-new).volume()<1e-7,(y,z)
 reports.append({'layout':layout,'watertight':True,'consistent_winding':True,'components':int(components),'lip_projection_reduction_mm':1.5,'previous_front_tip_x_mm':31.3,'new_front_tip_x_mm':29.8,'lip_height_z_mm':7.2,'all_three_rib_top_z_mm':7.2,'leg_position_preserved':True,'three_ribs_continuous_to_top':True,'physical_fit_verified':False})
 if layout=='existing':before=old;after=new
(OUT/'checks.json').write_text(json.dumps(reports,indent=2)+'\n')
def side(s,y):return s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(-y)
def draw(ax,section,color,fill):
 pts=[];codes=[]
 for a in section.to_polygons():pts.extend(a.tolist()+[a[0].tolist()]);codes.extend([PP.MOVETO]+[PP.LINETO]*(len(a)-1)+[PP.CLOSEPOLY])
 ax.add_patch(PathPatch(PP(pts,codes),facecolor=color if fill else 'none',edgecolor=color,lw=1.4))
fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='white')
for ax,y,title in [(axes[0],2.5,'Between ribs · lip shortened, leg fixed'),(axes[1],0,'Through rib · support raised to full height')]:
 draw(ax,side(after,y),'#a5c8db',True);draw(ax,side(before,y),'#c17c33',False)
 ax.set_aspect('equal');ax.set_xlim(20,32);ax.set_ylim(1.9,8.6);ax.grid(alpha=.15);ax.set_title(title,fontsize=12);ax.set_xlabel('Length X (mm) · peg to left');ax.set_ylabel('Height Z (mm)')
axes[0].annotate('',xy=(29.8,8),xytext=(31.3,8),arrowprops={'arrowstyle':'<->','color':'#924d26'})
axes[0].text(30.55,8.15,'1.5 mm',ha='center',color='#924d26')
axes[1].annotate('Full-height\ncurved support',xy=(24.7,6.5),xytext=(21,7.6),arrowprops={'arrowstyle':'->'},fontsize=10)
fig.suptitle('v30 · shorter lip and full-height rear ribs',fontsize=16)
fig.text(.5,.025,'Blue: revised STL · orange: v29 outline · same change on both fin layouts',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(OUT/'previews/lip_ribs_comparison.png',dpi=175);plt.close(fig)
