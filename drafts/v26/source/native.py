import sys,json,math,time
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
V=A.Vector
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'parameters.json').read_text());m=p['measured'];e=p['estimated'];cx,cz,ri,ro,half=p['native_dimensions'];w=m['body_width'];end=p['requested']['base_front_x'];front=18.1+e['frame_end_from_fin_start']

def line(a,b):return Part.makeLine(a,b)
def wire_poly(points):return Part.makePolygon(points+[points[0]])
def xzface(points,y=None):
 if y is None:y=-w/2
 return Part.Face(wire_poly([V(x,y,z) for x,z in points]))
def extrude_xz(points,width=None):
 if width is None:width=w
 return xzface(points,-width/2).extrude(V(0,width,0))
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def spline(points,periodic=False,final=None,initial=None):
 c=Part.BSplineCurve()
 if final is None and initial is None:c.interpolate(Points=points,PeriodicFlag=periodic,Tolerance=1e-7)
 else:c.interpolate(Points=points,InitialTangent=initial if initial is not None else points[1]-points[0],FinalTangent=final if final is not None else points[-1]-points[-2],Tolerance=1e-7)
 return c.toShape()
def circlepoint(c,r,deg,y):return V(c[0]+r*math.cos(math.radians(deg)),y,c[1]+r*math.sin(math.radians(deg)))
def arcedge(c,r,a,b,y):return Part.Arc(circlepoint(c,r,a,y),circlepoint(c,r,(a+b)/2,y),circlepoint(c,r,b,y)).toShape()

def ring():
 start=e['hook_opening_direction_degrees']+half;finish=e['hook_opening_direction_degrees']-half+360;t=math.radians(finish);u=(math.cos(t),math.sin(t));n=(-u[1],u[0]);r=e['hook_free_tip_outer_radius'];s=e['hook_free_tip_inner_radius']
 ao=math.sqrt(ro*ro-2*ro*r);ai=math.sqrt(ri*ri+2*ri*s)
 co=(cx+ao*u[0]-r*n[0],cz+ao*u[1]-r*n[1]);ci=(cx+ai*u[0]-s*n[0],cz+ai*u[1]-s*n[1])
 ta=math.degrees(math.atan2(co[1]-cz,co[0]-cx))%360;tb=math.degrees(math.atan2(ci[1]-cz,ci[0]-cx))%360;y=-w/2
 oa=arcedge((cx,cz),ro,start,ta,y);of=arcedge(co,r,ta,finish+90,y);inf=arcedge(ci,s,finish+90,tb+180,y);ia=arcedge((cx,cz),ri,tb,start,y)
 a=circlepoint(co,r,finish+90,y);b=circlepoint(ci,s,finish+90,y)
 return Part.Face(Part.Wire([oa,of,line(a,b),inf,ia,line(circlepoint((cx,cz),ri,start,y),circlepoint((cx,cz),ro,start,y))])).extrude(V(0,w,0))

def tangent(flat):
 px=0 if flat else e['back_link_start_x'];pz=0;dx=px-cx;dz=pz-cz;d2=dx*dx+dz*dz;fac=ro*math.sqrt(d2-ro*ro)/d2
 choices=[(cx+ro*ro/d2*dx+sign*fac*(-dz),cz+ro*ro/d2*dz+sign*fac*dx) for sign in [-1,1]]
 return (px,pz),min(choices)

def plan_mask():
 pts=p['base_rear_samples']+p['base_front_samples'][1:]
 lower=[V(x,-y,-30) for x,y in pts];upper=[V(x,y,-30) for x,y in pts[::-1]]
 return Part.Face(Part.Wire([spline(lower),line(lower[-1],upper[0]),spline(upper),line(upper[-1],lower[0])])).extrude(V(0,0,60))

def taper(offset=0,sign=1):
 vals=[(y-offset,z) for y,z in p['hook_taper_samples']]
 right=[V(-2,sign*y,z) for y,z in vals];left=[V(-2,-sign*y,z) for y,z in vals[::-1]]
 lo=V(-2,sign*vals[-1][0],-30);lo2=V(-2,-sign*vals[-1][0],-30)
 face=Part.Face(Part.Wire([spline(right,final=V(0,0,-1)),line(right[-1],lo),line(lo,lo2),line(lo2,left[0]),spline(left,initial=V(0,0,1)),line(left[-1],right[0])]))
 return face.extrude(V(42,0,0))

def entry():
 a=math.radians(e['hook_opening_direction_degrees']);u=(math.cos(a),math.sin(a));v=(-u[1],u[0]);h=m['hook_mouth']/2;l=math.sqrt(ri*ri-h*h)-.0001
 pts=[(cx+u[0]*x+v[0]*z,cz+u[1]*x+v[1]*z) for x,z in [(l,-h),(40,-h),(40,h),(l,h)]]
 return extrude_xz(pts,40)

def relief():
 a=math.radians(e['hook_opening_direction_degrees']);u=(math.cos(a),math.sin(a));v=(-u[1],u[0]);h=m['hook_mouth']/2;l=math.sqrt(ri*ri-h*h)-.0001
 q=V(front,-20,0);start=V(cx+u[0]*l+v[0]*h,-20,cz+u[1]*l+v[1]*h)
 c1=start+V(u[0]*e['hook_upper_blend_start_handle'],0,u[1]*e['hook_upper_blend_start_handle']);c2=q-V(0,0,e['hook_upper_blend_end_handle'])
 curve=Part.BezierCurve();curve.setPoles([start,c1,c2,q]);edge=curve.toShape()
 other=[q,V(front+4,-20,0),V(front+4,-20,-30),V(start.x,-20,-30),start]
 return Part.Face(Part.Wire([edge]+[line(a,b) for a,b in zip(other,other[1:])])).extrude(V(0,40,0))

def back(flat):
 a,q=tangent(flat)
 if flat:return extrude_xz([a,(front,0),(cx,cz),q])
 dx=q[0]-a[0];dz=q[1]-a[1];length=math.hypot(dx,dz);ux=dx/length;uz=dz/length;beta=-math.atan2(uz,ux);r=e['back_root_blend_radius'];dist=r*math.tan(beta/2);av=V(a[0]-dist,-w/2,0);bv=V(a[0]+ux*dist,-w/2,uz*dist)
 arc=arcedge((av.x,-r),r,90-math.degrees(beta),90,-w/2)
 verts=[av,V(front,-w/2,.2),V(cx,-w/2,cz),V(q[0],-w/2,q[1]),bv]
 return Part.Face(Part.Wire([line(a,b) for a,b in zip(verts,verts[1:])]+[arc])).extrude(V(0,w,0))

def pocket_mask():
 curves=[]
 for pts in p['pocket_contours']:
  points=[V(x,-20,z) for x,z in pts]
  curves.append(Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,40,0)))
 return curves[0]

def build(flat):
 started=time.time();label='flat' if flat else 'standard';print('Native build',label,flush=True)
 host=box(0,end,-w/2,w/2,0,m['base_wall']).fuse(back(flat)).fuse(box(cx-1.5,front,-w/2,w/2,cz+ri-.2,.1))
 cyl=Part.makeCylinder(ri+.01,40,V(cx,-20,cz),V(0,1,0))
 host=host.cut(cyl).cut(entry()).cut(relief())
 body=host.fuse(ring())
 a=math.radians(e['hook_opening_direction_degrees']);u=(math.cos(a),math.sin(a));v=(-u[1],u[0]);h=m['hook_internal_rib_height']/2
 tooth=[(cx+u[0]*x+v[0]*z,cz+u[1]*x+v[1]*z) for x,z in [(-ri-.3,-h),(-ri+1.4,-h),(-ri+1.4,h),(-ri-.3,h)]]
 body=body.fuse(extrude_xz(tooth)).common(plan_mask()).common(taper().fuse(box(-2,40,-20,20,0,20))).removeSplitter()
 body.exportBrep(str(ROOT/(label+'_unfilleted.brep')))
 assert body.isValid();print('Body faces',len(body.Faces),'edges',len(body.Edges),'seconds',time.time()-started,flush=True)
 candidates=[ed for ed in body.Edges if ed.CenterOfMass.z<-.7 and abs(ed.CenterOfMass.y)>7.9 and ed.Length>.1]
 print('Outer fillet edges',len(candidates),flush=True)
 # Fillet the free-tip chain on both sides first, then the long support edges.
 tip=[ed for ed in body.Edges if ed.CenterOfMass.x>32.8 and ed.CenterOfMass.x<33.5 and abs(ed.CenterOfMass.y)>8.4 and ed.CenterOfMass.z<-12 and ed.Curve.__class__.__name__=='Line']
 for sign in [1]:
  tip=[ed for ed in body.Edges if 32.8<ed.CenterOfMass.x<33.5 and sign*ed.CenterOfMass.y>8.4 and ed.CenterOfMass.z<-12 and ed.Curve.__class__.__name__=='Line']
  for radius in [.4,.3,.2,.1]:
   try:
    result=body.makeFillet(radius,tip)
    if result.isValid():body=result;print('Tip fillet',sign,radius,flush=True);break
   except Exception:pass
  else:raise RuntimeError('Tip fillet failed for side '+str(sign))
 for predicate,radii in [(lambda c,L: 14<c.x<18 and -8<c.z<-4 and L>10,[.4,.3,.2,.1]),(lambda c,L:c.x>28 and c.z> -5 and c.z<-.7 and L>1,[.1,.05])]:
  selected=[ed for ed in body.Edges if ed.CenterOfMass.y>8 and predicate(ed.CenterOfMass,ed.Length)]
  for radius in radii:
   try:
    result=body.makeFillet(radius,selected)
    if result.isValid():body=result;print('Support fillet',radius,len(selected),flush=True);break
   except Exception:pass
  else:
   try:
    result=body.makeChamfer(.3,selected)
    if not result.isValid():raise RuntimeError('invalid chamfer')
    body=result;print('Clean support chamfer',flush=True)
   except Exception:print('Support edge kept at native contour',flush=True)
 # Treat the long exposed side edges separately so a difficult junction cannot
 # invalidate fillets on unrelated shoulders. Preserve the flat printing plane.
 targets=[ed.CenterOfMass for ed in body.Edges if ed.CenterOfMass.y>8 and ed.CenterOfMass.z<-.7 and ed.Length>2]
 treatments=[]
 for target in targets:
  selected=min(body.Edges,key=lambda ed:(ed.CenterOfMass-target).Length)
  if (selected.CenterOfMass-target).Length>.05:continue
  for radius in [.4,.25,.15]:
   try:
    result=body.makeFillet(radius,[selected])
    if result.isValid():
     body=result;treatments.append(radius);break
   except Exception:pass
 print('Individual edge fillets',treatments,flush=True)
 # Contour-derived recess follows the actual section, including its curved bore boundary.
 vals=[V(-2,y-e['side_recess_depth'],z) for y,z in p['hook_taper_samples']]
 band=Part.Face(Part.Wire([spline(vals),line(vals[-1],V(-2,20,-12)),line(V(-2,20,-12),V(-2,20,0)),line(V(-2,20,0),vals[0])])).extrude(V(42,0,0))
 pm=pocket_mask();cutter=band.common(pm)
 body=body.cut(cutter)
 assert body.isValid(), 'invalid pocket cut'
 newedges=[]
 for ed in body.Edges:
  c=ed.valueAt((ed.FirstParameter+ed.LastParameter)/2)
  if c.y>7.5 and -10.6<c.z<-1.1 and pm.isInside(V(c.x,0,c.z),.03,True):newedges.append(ed)
 print('Pocket-only fillet edges',len(newedges),flush=True)
 def outside_y(z):
  vals=p['hook_taper_samples']
  for (ya,za),(yb,zb) in zip(vals,vals[1:]):
   if zb<=z<=za:return ya+(yb-ya)*(z-za)/(zb-za)
  return vals[-1][0]
 for which in ['floor','rim']:
  selected=[]
  for ed in body.Edges:
   c=ed.valueAt((ed.FirstParameter+ed.LastParameter)/2)
   if not(c.y>7.5 and -10.6<c.z<-1.1 and pm.isInside(V(c.x,0,c.z),.03,True)):continue
   floor_edge=c.y<outside_y(c.z)-.3
   if floor_edge==(which=='floor'):selected.append(ed)
  for radius in [.2,.15,.1]:
   try:
    result=body.makeFillet(radius,selected)
    if result.isValid():body=result;print('Pocket '+which+' fillet',radius,len(selected),flush=True);break
   except Exception:pass
  else:
   try:
    result=body.makeChamfer(.1,selected)
    if not result.isValid():raise RuntimeError('invalid chamfer')
    body=result;print('Pocket '+which+' bevel',flush=True)
   except Exception:print('Pocket '+which+' kept smooth contour boundary',flush=True)
 # Mirror the good half to ensure identical fillets on both lateral sides.
 halfbody=body.common(box(-2,40,0,20,-30,20))
 body=halfbody.fuse(halfbody.mirror(V(0,0,0),V(0,1,0))).removeSplitter()
 print('Finished',label,'seconds',time.time()-started,'valid',body.isValid(),flush=True)
 body.exportStep(str(ROOT/(label+'.step')))
 mesh=MeshPart.meshFromShape(Shape=body,LinearDeflection=.008,AngularDeflection=.1,Relative=False);mesh.write(str(ROOT/(label+'_body.stl')))
 (ROOT/(label+'_native.json')).write_text(json.dumps({'additional_edge_fillet_radii_mm':treatments,'tip_fillet_radius_mm':.4,'pocket_contour_border_mm':1.1,'pocket_depth_mm':.6,'native_valid':body.isValid(),'solids':len(body.Solids),'volume_mm3':body.Volume,'seconds':time.time()-started},indent=2))

for flat in [True]:build(flat)
