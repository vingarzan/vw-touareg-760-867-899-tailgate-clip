"""v22: reverse latch wall lean, keep root and lip locations; patch only flat v21."""
import json,math,os
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Arc

def cs(pts):
 a=np.array(pts);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1))
 return mf.CrossSection([a if area>0 else a[::-1]])
def xz(pts,width,cy=0):return cs(pts).extrude(width).transform([[1,0,0,0],[0,0,-1,cy+width/2],[0,1,0,0]])
def load(path):
 m=trimesh.load_mesh(path,process=True)
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
p=json.loads((ROOT/'drafts/v21/source/parameters.json').read_text());m=p['measured'];e=p['estimated']
start=e['peg_center_from_rear']+m['peg_base_diameter']/2+m['peg_to_fin_edge_gap_along_length']+p['requested']['latch_shift_away_from_peg']
z0=m['base_wall'];top=e['latch_top_z']-e['latch_bar_thickness'];foot=start+e['latch_wall_foot_from_fin_start'];th=e['latch_wall_thickness_x'];ztop=top+.1
lean=(ztop-z0)/math.tan(math.radians(115))
# Locate the visible centreline at the exact mounting face; overlap below it.
def wallpts(dx):
 slope=dx/(ztop-z0)
 return [[foot-.15*slope,z0-.15],[foot+th-.15*slope,z0-.15],[foot+th+dx,ztop],[foot+dx,ztop]]
oldwall=wallpts(1.2);newwall=wallpts(lean)
bar=[[start+9.1,top],[start+10.5,top],[start+10.5,top-.3],[start+11.2,top+.3],[start+10.9,e['latch_top_z']],[start+9.1,e['latch_top_z']]]
# Short horizontal return preserves every point of the measured lip profile.
bridge=[[foot+lean,top-1.05],[start+9.3,top-1.05],[start+9.3,top+.15],[foot+lean,top+.15]]
t=np.linspace(0,1,48)[:,None]
# Root of each original reinforcement is fixed; its upper end follows the reversed wall.
p0=np.array([start+.9,z0+.15]);p1=np.array([start+5.3,z0+.15]);p2=np.array([foot+lean-2,top-.1]);p3=np.array([foot+lean+.6,top+.1])
curve=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
rib=np.vstack([[p0[0],z0-.15],curve,[p3[0],z0-.15]])
newlatch=xz(newwall,m['latch_width'])+xz(bar,m['latch_width'])+xz(bridge,m['latch_width'])
for y in [-5.4,0,5.4]:newlatch+=xz(rib,e['latch_rib_width'],y)
old=load(ROOT/'drafts/v21/stl/760867899_v21_flat_support.stl')
# Width-limited cut leaves side fins, base, hook and peg untouched.
cut=mf.Manifold.cube([12,15.02,10]).translate([start-.1,-7.51,z0+.01])
new=(old-cut)+newlatch
meshdata=new.to_mesh();mesh=trimesh.Trimesh(vertices=meshdata.vert_properties[:,:3],faces=meshdata.tri_verts,process=True)
mesh.update_faces(mesh.area_faces>1e-16);mesh.remove_unreferenced_vertices()
path=OUT/'stl/760867899_v22_flat_support.stl';mesh.export(path)
check=trimesh.load_mesh(path,process=True)
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
a=check.face_adjacency;components=connected_components(coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(check.faces),len(check.faces))),directed=False,return_labels=False)
print('mesh checks',check.is_watertight,check.is_winding_consistent,components,len(check.faces),flush=True)
assert check.is_watertight and check.is_winding_consistent and components==1
# Verify geometry outside the edited local region, and lip profile, by CSG difference.
protected=old-cut
print('Protected difference',((protected-new).volume()),flush=True)
assert ((protected-new).volume())<.15
lip=xz(bar,m['latch_width']);assert (lip-new).volume()<.002
report={'revision':'v22','wall_angle_degrees':115,'previous_wall_angle_degrees':math.degrees(math.atan2(ztop-z0,1.2)),'root_x_mm':foot,'wall_top_x_mm':foot+lean,'lip_unchanged':True,'watertight':bool(check.is_watertight),'consistent_winding':bool(check.is_winding_consistent),'connected_components':int(components),'physical_fit_verified':False,'return_under_lip_thickness_mm':1.2}
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
# Sections taken through the actual output STL solids, away from the reinforcement ribs.
def section(s,y):return s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).slice(-y)
def draw(ax,section,color,alpha=1,outline=False):
 for pts in section.to_polygons():ax.add_patch(Polygon(pts,closed=True,facecolor='none' if outline else color,edgecolor=color,linewidth=1.6,alpha=alpha))
fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='white')
for ax,title,s in [(axes[0],'v21 · current leg',old),(axes[1],'v22 · leg angled back',new)]:
 draw(ax,section(s,2.5),'#467f9f',.5)
 if s is new:draw(ax,section(old,2.5),'#d5873a',.85,True)
 ax.set_xlim(24,32.5);ax.set_ylim(1.7,8.2);ax.set_aspect('equal');ax.grid(alpha=.16);ax.set_title(title);ax.set_xlabel('← Back / peg             Front / hook →\nLength X (mm)');ax.set_ylabel('Height above underside (mm)')
 angle=report['previous_wall_angle_degrees'] if s is old else 115
 center=(foot+th/2,z0)
 ax.add_patch(Arc(center,3,3,theta1=0,theta2=angle,color='#8d3528',lw=1.6))
 ax.text(foot+.7,z0+.9,f'{angle:.0f}°',color='#8d3528',fontsize=12)
 ax.plot([center[0],center[0]+2],[z0,z0],color='#8d3528',lw=1)
 ax.scatter([center[0]],[z0],color='#235d3e',zorder=4)
 axes[1].annotate('Lip stays fixed',xy=(start+10.3,6.7),xytext=(25.2,7.65),arrowprops={'arrowstyle':'->'},fontsize=10)
axes[1].annotate('Short return\nunder the lip',xy=(28.2,5.4),xytext=(24.2,4.2),arrowprops={'arrowstyle':'->'},fontsize=10)
fig.suptitle('Latch comparison · root and top lip stay in place',fontsize=16)
fig.text(.5,.02,'Section through continuous wall, between ribs · orange outline: v21 · blue: actual revised STL',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.12,1,.94));fig.savefig(OUT/'previews/latch_comparison.png',dpi=175);plt.close(fig)
