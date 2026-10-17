"""Original Haipam hard-surface hulls, built from the user's ship reference sheets.

Geometry is generated independently; no proprietary game mesh is copied.
Coordinates: X starboard, Y up, +Z bow. Run from any directory.
"""
from pathlib import Path
import math, json, shutil, hashlib
import numpy as np
from PIL import Image
import pdx_binary as pdx

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/ships'
RUNTIME=ROOT/'mod/haipam/gfx/models/ships/haipam'
COLORS=[(105,126,76),(78,94,61),(53,57,50),(174,180,159),(244,218,66),(88,194,241)]

class Hull:
    def __init__(self): self.faces=[]
    def face(self,points,color=0): self.faces.append((points,color))
    def box(self,center,size,color=0):
        x,y,z=center; a,b,c=[n/2 for n in size]
        p=[(x+dx*a,y+dy*b,z+dz*c) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]: self.face([p[i] for i in ids],color)
    def cylinder(self,center,radius,height,color=0,n=12):
        x,y,z=center
        ring=[(x+radius*math.cos(i*math.tau/n),y-height/2,z+radius*math.sin(i*math.tau/n)) for i in range(n)]
        top=[(a,y+height/2,c) for a,b,c in ring]
        self.face(ring,color);self.face(list(reversed(top)),color)
        for i in range(n):j=(i+1)%n;self.face([ring[i],top[i],top[j],ring[j]],color)
    def gun(self,x,y,z,r=.3):
        self.cylinder((x,y,z),r,.16,1)
        self.box((x,y+.12,z+.04),(r*1.3,.19,r*1.4),0)
        for offset in [-.12,0,.12]:self.box((x+offset*r*2,y+.15,z+r*.95),(.055,.055,r*1.5),2)
    def subset(self,lo,hi):
        h=Hull();h.faces=[(p,c) for p,c in self.faces if lo<=sum(v[2] for v in p)/len(p)<hi];return h
    def obj(self,path):
        lines=['# Original Haipam hull; +Z forward, Y up','mtllib haipam_palette.mtl'];i=1
        for points,color in self.faces:
            lines.append('usemtl palette_'+str(color))
            for p in points:lines.append('v '+' '.join(f'{v:.6f}' for v in p))
            p=np.array(points,dtype=float);normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal)
            tangent=p[1]-p[0];tangent/=np.linalg.norm(tangent);bitangent=np.cross(normal,tangent)
            projected=np.array([(np.dot(q,tangent),np.dot(q,bitangent)) for q in p]);low=projected.min(0);span=np.maximum(projected.max(0)-low,.00001)
            for u,v in (projected-low)/span:
                lines.append(f'vt {((color%4)*128+12+u*104)/512:.6f} {1-((color//4)*128+12+v*104)/256:.6f}')
            for q in points:lines.append('vn '+' '.join(f'{v:.6f}' for v in normal))
            lines.append('f '+' '.join(f'{k}/{k}/{k}' for k in range(i,i+len(points))));i+=len(points)
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def design(kind):
    h=Hull()
    if kind=='heavy':
        # Long flat foredeck, stepped broad stern and paired gun sponsons.
        h.box((0,0,0),(2.6,.9,8.0))
        h.box((0,.58,-2.4),(3.3,.72,3.2));h.box((0,1.08,-2.9),(2.25,.4,2.0))
        for s in [-1,1]:
            h.box((s*2.0,-.05,-2.0),(1.3,.95,3.55));h.box((s*1.55,.33,-1.4),(.65,.5,3.8),1)
            for z in [-3.1,-2.25,-1.4]:h.gun(s*2,.48,z,.35)
            for z in [-2.8,-1.8,-.8,.2,1.2,2.2,3.2]:
                for y in [-.18,.18]:h.box((s*1.315,y,z),(.025,.055,.2),3)
        for z in [-3.35,-2.55,-1.75]:h.gun(0,1.39,z,.34)
        h.gun(0,.55,1.2,.33)
        h.box((0,1.55,-3.15),(1.25,.45,.62),1);h.box((0,1.56,-2.828),(1.12,.12,.025),4)
        for x in [-.45,.45]:h.box((x,1.95,-3.25),(.035,.65,.035),2)
        for x in [-.9,-.6,-.3,0,.3,.6,.9]:h.box((x,.47,2.6),(.06,.035,1.55),2)
        for x in [-1.18,1.18]:h.box((x,.47,2.5),(.025,.025,2.4),3)
        for s in [-1,1]:
            for z in [-3.4,-3.2,-3,-2.8,-2.6]:h.box((s*2.66,-.03,z),(.025,.48,.055),2)
        for x in [-2,0,2]:
            h.box((x,-.04,-3.81),(.65,.42,.1),2);h.box((x,-.04,-3.87),(.45,.25,.035),5)
        for x in [-.8,0,.8]:h.box((x,-.7,1.3),(.22,.7,1.2),2)
    elif kind=='medium':
        h.box((0,0,0),(1.7,.65,6));h.box((0,.45,-1.6),(2.2,.45,2.5));h.box((0,.85,-1.9),(1.2,.38,.8))
        for s in [-1,1]:
            h.box((s*1.4,0,-1.3),(.8,.65,2.3));
            for z in [-1.9,-1.0]:h.gun(s*1.4,.4,z,.23)
        for z in [-2,-1,1.0]:h.gun(0,.95 if z<0 else .42,z,.25)
        h.box((0,.9,-1.48),(.9,.1,.035),4)
        for x in [-.6,-.3,0,.3,.6]:h.box((x,.34,2),(.045,.025,1.2),2)
        for x in [-1.4,0,1.4]:h.box((x,0,-2.51 if x else -3.02),(.4,.25,.04),5)
    else:
        # Capture-net escort silhouette: compact stern, straight long forward beam.
        h.box((0,0,0),(.95,.42,3.4));h.box((0,.2,-.8),(1.5,.5,1.7));h.box((0,.57,-.65),(.65,.35,.55))
        for s in [-1,1]:h.box((s*.66,-.05,-.75),(.4,.4,1.35));h.gun(s*.64,.38,-.9,.16)
        h.gun(0,.29,.72,.16);h.box((0,.58,-.36),(.52,.085,.025),4)
        h.box((0,.36,1.28),(.09,.09,1.15),2)
        for x in [-.55,0,.55]:h.box((x,0,-1.69),(.24,.18,.04),5)
        h.box((0,.88,-.7),(.025,.35,.025),2)
    return h

def rasterize(im,faces):
    """Orthographic triangle z-buffer; render the actual mesh, including intersecting parts."""
    pixels=np.array(im);depth=np.full((im.height,im.width),-np.inf)
    for verts,color in faces:
        for j in range(1,len(verts)-1):
            tri=np.array([verts[0],verts[j],verts[j+1]],dtype=float)
            x0=max(0,int(math.floor(tri[:,0].min())));x1=min(im.width-1,int(math.ceil(tri[:,0].max())))
            y0=max(0,int(math.floor(tri[:,1].min())));y1=min(im.height-1,int(math.ceil(tri[:,1].max())))
            if x0>x1 or y0>y1:continue
            a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8:continue
            xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-v
            z=u*a[2]+v*b[2]+w*c[2];region=depth[y0:y1+1,x0:x1+1];mask=(u>=-.0001)&(v>=-.0001)&(w>=-.0001)&(z>=region)
            pixels[y0:y1+1,x0:x1+1][mask]=color;region[mask]=z[mask]
    im.paste(Image.fromarray(pixels))

def preview(designs):
    from PIL import ImageDraw,ImageFont
    im=Image.new('RGB',(1800,1000),'#121d27');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    yaw=.65;pitch=.55
    for i,(name,h) in enumerate(designs.items()):
        scale={'light':125,'medium':94,'heavy':77}[name];cx=300+600*i;cy=500
        def project(v):
            x,y,z=v;u=x*math.cos(yaw)+z*math.sin(yaw);q=-x*math.sin(yaw)+z*math.cos(yaw)
            return (cx+u*scale,cy+q*math.sin(pitch)*scale-y*math.cos(pitch)*scale),q*math.cos(pitch)+y*math.sin(pitch)
        ordered=[]
        for pts,c in h.faces:
            proj=[project(v) for v in pts];normal=np.cross(np.array(pts[1])-pts[0],np.array(pts[2])-pts[0]);ln=np.linalg.norm(normal)
            shade=.65+.35*abs(float(np.dot(normal/ln if ln else normal,np.array([.3,.9,.2]))))
            rgb=tuple(min(255,int(v*shade)) for v in COLORS[c]);ordered.append(([(q[0][0],q[0][1],q[1]) for q in proj],rgb))
        rasterize(im,ordered);d=ImageDraw.Draw(im)
        title={'light':'CAPTURE-NET / escort','medium':'HAIPAM / derived medium','heavy':'LONG-SPEAR D / battleship'}[name]
        d.text((cx-230,110),title,font=font,fill='white')
        d.text((cx-225,835),str(len(h.faces))+' editable hard-surface faces',font=small,fill='#bccbd2')
    d.text((330,940),'Original geometry preview / reference-based prototype / NOT an in-game screenshot',font=small,fill='#bccbd2')
    im.save(ART/'haipam_hulls_geometry.png')

def orthographic(designs):
    from PIL import ImageDraw,ImageFont
    im=Image.new('RGB',(1800,1100),'#18232c');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
    for i,(name,h) in enumerate(designs.items()):
        scale={'light':100,'medium':71,'heavy':54}[name];cx=300+i*600
        for mode,cy in [('TOP',330),('SIDE',820)]:
            faces=[]
            for pts,c in h.faces:
                if mode=='TOP':p=[(cx+x*scale,cy+z*scale) for x,y,z in pts];depth=sum(y for x,y,z in pts)/len(pts)
                else:p=[(cx+z*scale,cy-y*scale) for x,y,z in pts];depth=sum(x for x,y,z in pts)/len(pts)
                faces.append((depth,p,COLORS[c]))
            for dep,p,color in sorted(faces,key=lambda a:a[0]):d.polygon(p,fill=color,outline='#303a2c')
            d.text((cx-210,cy-245 if mode=='TOP' else cy+90),name.upper()+' / '+mode,font=font,fill='white')
    d.text((420,1055),'Actual editable geometry / source geometry axes / not an in-game screenshot',font=font,fill='#bccbd2')
    im.save(ART/'haipam_hulls_orthographic.png')

def textures():
    from PIL import ImageDraw
    diffuse=Image.new('RGBA',(512,256),(0,0,0,255));normal=Image.new('RGBA',(512,256),(128,128,0,128));spec=Image.new('RGBA',(512,256),(0,85,40,90))
    d=ImageDraw.Draw(diffuse);n=ImageDraw.Draw(normal);s=ImageDraw.Draw(spec)
    for i,rgb in enumerate(COLORS):
        x=(i%4)*128;y=(i//4)*128;d.rectangle((x,y,x+127,y+127),fill=rgb+(255,))
        if i in [0,1,2]:
            for v in [8,119]:d.line((x+v,y+7,x+v,y+120),fill=tuple(int(z*.82) for z in rgb)+(255,),width=2)
            d.line((x+7,y+8,x+120,y+8),fill=tuple(min(255,int(z*1.15)) for z in rgb)+(255,),width=2)
        if i>=4:n.rectangle((x,y,x+127,y+127),fill=(128,128,255,128));s.rectangle((x,y,x+127,y+127),fill=(0,100,20,150))
    for name,im in [('diffuse',diffuse),('normal',normal),('specular',spec)]:
        im.save(ART/f'haipam_hulls_{name}.png');im.save(RUNTIME/f'haipam_hulls_{name}.dds')

def locators(root,items):
    loc=root.add('locator')
    for name,point in items.items():loc.add(name,p=[float(point[0]*4),float(point[1]*4),float(-point[2]*4)],q=[0.0,0.0,0.0,1.0])

def mesh_export(h,path,locs=None,frame_parts=0):
    root=pdx.Node('File',{'pdxasset':[1,0]});obj=root.add('object');shape=obj.add('haipam_hull')
    if h.faces:
        positions=[];normals=[];tangents=[];uvs=[];indices=[]
        for points,color in h.faces:
            # PDX ship forward is -Z; reflect source Z and reverse the polygon.
            points=[np.array([x*4,y*4,-z*4],dtype=float) for x,y,z in reversed(points)]
            normal=np.cross(points[1]-points[0],points[2]-points[0]);length=float(np.linalg.norm(normal))
            if length<1e-9:continue
            normal/=length;tangent=(points[1]-points[0]);tangent/=np.linalg.norm(tangent);bitangent=np.cross(normal,tangent)
            projected=[(float(np.dot(p,tangent)),float(np.dot(p,bitangent))) for p in points]
            low=np.min(projected,axis=0);high=np.max(projected,axis=0);span=np.maximum(high-low,.00001)
            base=len(positions)//3
            for point,(u,v) in zip(points,projected):
                positions.extend(map(float,point));normals.extend(map(float,normal));tangents.extend([*map(float,tangent),1.0])
                uu=(u-low[0])/span[0];vv=(v-low[1])/span[1]
                uvs.extend([float(((color%4)*128+12+uu*104)/512),float(1-((color//4)*128+12+vv*104)/256)])
            for i in range(1,len(points)-1):indices.extend([base,base+i,base+i+1])
        mesh=shape.add('mesh',p=positions,n=normals,ta=tangents,u0=uvs,tri=indices)
        array=np.array(positions).reshape(-1,3);mesh.add('aabb',min=list(map(float,array.min(0))),max=list(map(float,array.max(0))))
        mesh.add('material',shader='PdxMeshShip',diff='haipam_hulls_diffuse.dds',n='haipam_hulls_normal.dds',spec='haipam_hulls_specular.dds')
    if frame_parts:
        skeleton=shape.add('skeleton');identity=[1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.]
        skeleton.add('root',ix=[0],tx=identity)
        for i in range(frame_parts):skeleton.add('part'+str(i+1),ix=[i+1],pa=[0],tx=identity)
    if locs:locators(root,locs)
    pdx.write(path,root)
    reread=pdx.read(path)
    def same(a,b):
        assert a.name==b.name and a.props.keys()==b.props.keys() and len(a.children)==len(b.children)
        for key,values in a.props.items():
            if isinstance(values,str):values=[values]
            if isinstance(values[0],str):assert b.props[key]==values
            else:assert np.allclose(values,b.props[key],rtol=1e-6,atol=1e-6)
        for aa,bb in zip(a.children,b.children):same(aa,bb)
    same(root,reread)
    return root

def runtime_export(designs):
    # Sections retain shared full-hull coordinates, attached to identity part bones.
    split={'light':[('core',-100,100)],'medium':[('bow',0,100),('stern',-100,0)],'heavy':[('bow',.7,100),('core',-1.1,.7),('stern',-100,-1.1)]}
    slotloc={
       'light_core':{'small_gun_01':(0,.4,.72),'small_gun_02':(-.64,.48,-.9),'small_gun_03':(.64,.48,-.9)},
       'medium_bow':{'medium_gun_01':(0,.6,1),'small_gun_01':(-.6,.36,1.8),'small_gun_02':(.6,.36,1.8)},
       'medium_stern':{'small_gun_01':(-1.4,.56,-1),'small_gun_02':(1.4,.56,-1)},
       'heavy_bow':{'large_gun_01':(0,.76,1.2)},
       'heavy_core':{'medium_gun_01':(-2,.68,-1.4),'medium_gun_02':(2,.68,-1.4),'medium_gun_03':(0,1.59,-1.75)},
       'heavy_stern':{'medium_gun_01':(0,1.59,-3.35)}}
    meshes=[];entities=[];stats={}
    for name,h in designs.items():
        frame='haipam_'+name+'_frame'
        locs={f'part{i+1}_locator':(0,0,0) for i in range(len(split[name]))}
        locs.update({'target_locator_1':(0,0,1),'target_locator_2':(0,0,-1),'engine_01':(0,0,{'light':-1.71,'medium':-3.04,'heavy':-3.9}[name]),'engine_02':(-.6,0,-1.5),'engine_03':(.6,0,-1.5)})
        mesh_export(Hull(),RUNTIME/(frame+'.mesh'),locs,len(split[name]));meshes.append(frame)
        scale={'light':6.5,'medium':7.5,'heavy':10.5}[name]
        entities.append(f'entity = {{ name = "haipam_{name}_entity" pdxmesh = "{frame}_mesh" scale = {scale} default_state = "idle" state = {{ name = "idle" }} state = {{ name = "moving" }} state = {{ name = "combat" }} game_data = {{ emissive_recolor_crunch = 0.0 }} }}')
        for part,lo,hi in split[name]:
            key=name+'_'+part;sub=h.subset(lo,hi);sub.obj(ART/(key+'.obj'));node_locs=dict(slotloc[key])
            for node,point in list(node_locs.items()):node_locs[node+'_muzzle']=(point[0],point[1],point[2]+.45)
            meshname='haipam_'+key;root=mesh_export(sub,RUNTIME/(meshname+'.mesh'),node_locs);meshes.append(meshname)
            meshnode=root.children[0].children[0].children[0];stats[key]={'vertices':len(meshnode.props['p'])//3,'triangles':len(meshnode.props['tri'])//3,'locators':node_locs}
            entities.append(f'entity = {{ name = "{meshname}_entity" pdxmesh = "{meshname}_mesh" default_state = "idle" state = {{ name = "idle" }} state = {{ name = "moving" }} game_data = {{ emissive_recolor_crunch = 0.0 }} }}')
    gfx=['objectTypes = {']
    for name in meshes:gfx.append(f'pdxmesh = {{ name = "{name}_mesh" file = "gfx/models/ships/haipam/{name}.mesh" scale = 1.0 meshsettings = {{ name = "haipam_hull" shader = "PdxMeshShip" }} }}')
    gfx.append('}');(RUNTIME/'haipam_ships.gfx').write_text('\n'.join(gfx)+'\n',encoding='utf-8');(RUNTIME/'haipam_ships.asset').write_text('\n'.join(entities)+'\n',encoding='utf-8')
    (ART/'model-validation.json').write_text(json.dumps({'source':'user reference sheet + original procedural geometry','sections':stats,'pdx_roundtrip':True,'engine_verified':False,'scale_material_firing_verified':False},indent=2),encoding='utf-8')
    return stats

def validate_generated(stats):
    expected={'light_core':{'small_gun_01','small_gun_02','small_gun_03'},'medium_bow':{'medium_gun_01','small_gun_01','small_gun_02'},'medium_stern':{'small_gun_01','small_gun_02'},'heavy_bow':{'large_gun_01'},'heavy_core':{'medium_gun_01','medium_gun_02','medium_gun_03'},'heavy_stern':{'medium_gun_01'}}
    triangles=0
    for name,required in expected.items():
        tree=pdx.read(RUNTIME/f'haipam_{name}.mesh');mesh=tree.children[0].children[0].children[0]
        p=np.array(mesh.props['p']).reshape(-1,3);n=np.array(mesh.props['n']).reshape(-1,3);ta=np.array(mesh.props['ta']).reshape(-1,4);uv=np.array(mesh.props['u0']).reshape(-1,2);tri=np.array(mesh.props['tri'])
        assert len(p)==len(n)==len(ta)==len(uv) and np.isfinite(p).all()
        assert np.allclose(np.linalg.norm(n,axis=1),1,atol=1e-5) and np.allclose(np.linalg.norm(ta[:,:3],axis=1),1,atol=1e-5)
        assert np.max(np.abs(np.sum(n*ta[:,:3],axis=1)))<1e-5
        assert tri.min()>=0 and tri.max()<len(p) and len(tri)%3==0 and uv.min()>=0 and uv.max()<=1
        locs={x.name for x in tree.children[1].children};assert required<=locs and all(x+'_muzzle' in locs for x in required)
        triangles+=len(tri)//3
    for name,count in [('light',1),('medium',2),('heavy',3)]:
        tree=pdx.read(RUNTIME/f'haipam_{name}_frame.mesh');sk=tree.children[0].children[0].children[0]
        assert {f'part{i+1}' for i in range(count)}<={n.name for n in sk.children}
        locs={n.name for n in tree.children[1].children};assert {'engine_01','engine_02','engine_03','target_locator_1','target_locator_2'}<=locs
    for name in ['diffuse','normal','specular']:
        p=RUNTIME/f'haipam_hulls_{name}.dds';assert p.read_bytes()[:4]==b'DDS ';assert Image.open(p).size==(512,256)
    report=json.loads((ART/'model-validation.json').read_text(encoding='utf-8'));report.update({'geometry_checks':{'section_count':6,'frame_count':3,'triangles':triangles,'unit_normals':True,'orthogonal_tangents':True,'uv_range':True,'required_locators':True,'dds_readable':True},'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RUNTIME.iterdir() if p.is_file()}})
    (ART/'model-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

def main():
    ART.mkdir(parents=True,exist_ok=True);RUNTIME.mkdir(parents=True,exist_ok=True)
    refs=ART/'reference';refs.mkdir(exist_ok=True)
    for src,name in [('TapNow_1771215521797_封面2_1.jpg','long_spear_cover.jpg'),('TapNow_1771215551985_长枪级三视图（缩小）_1.jpg','long_spear_orthographic.jpg')]:
        path=Path.home()/'Desktop'/src
        if path.exists():shutil.copy2(path,refs/name)
    (ART/'haipam_palette.mtl').write_text('\n'.join(f'newmtl palette_{i}\nKd 1 1 1\nKs 0.2 0.2 0.2\nNs 24\nmap_Kd haipam_hulls_diffuse.png' for i,rgb in enumerate(COLORS)),encoding='utf-8')
    designs={name:design(name) for name in ['light','medium','heavy']}
    for name,h in designs.items():h.obj(ART/(name+'_complete.obj'))
    preview(designs);orthographic(designs);textures();stats=runtime_export(designs);validate_generated(stats)
    print(json.dumps({'stage':'original_pdx_export','faces':{n:len(h.faces) for n,h in designs.items()},'sections':{n:s['triangles'] for n,s in stats.items()},'preview':str(ART/'haipam_hulls_geometry.png'),'engine_verified':False}))

if __name__=='__main__':main()
