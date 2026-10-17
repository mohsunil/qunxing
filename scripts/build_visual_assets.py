"""Export normal-proportion portrait PNGs and vector UI symbols to game textures.

Pillow is only needed to rebuild textures. Already-built textures ship in the Mod.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/haipam'
SOURCE=ROOT/'assets/source'

def save(im,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path)

def species_mark(size,color=(255,255,255,255)):
    # Engine flags tint white RGB. Preserve the image_gen source alpha exactly;
    # RGB normalization is an export requirement, not a redraw of the emblem.
    source=Image.open(ROOT/'assets/haipam-species-mark-transparent.png').convert('RGBA')
    mask=source.getchannel('A').resize((size,size),Image.Resampling.LANCZOS)
    result=Image.new('RGBA',(size,size),color)
    result.putalpha(mask)
    return result

def crest(draw,s,fill):
    def poly(points):draw.polygon([(x*s,y*s) for x,y in points],fill=fill)
    poly([(43,16),(85,16),(78,30),(50,30)])
    draw.ellipse((53*s,42*s,75*s,64*s),outline=fill,width=max(1,int(6*s)))
    poly([(58,76),(77,80),(68,103)])
    poly([(24,34),(30,63),(49,99),(43,75),(35,48)])
    poly([(104,34),(98,63),(79,99),(85,75),(93,48)])

def icon(kind,size):
    scale=4
    im=Image.new('RGBA',(size*scale,size*scale),(0,0,0,0));d=ImageDraw.Draw(im)
    q=size*scale/128
    gold=(229,194,101,255);green=(137,179,113,255);red=(227,63,60,255)
    if kind=='white':im.alpha_composite(species_mark(size*scale,gold))
    elif kind=='gray':
        for points in [[(58,54),(12,20),(20,58)],[(58,68),(8,76),(40,104)],[(70,54),(116,20),(108,58)],[(70,68),(120,76),(88,104)]]:
            d.polygon([(x*q,y*q) for x,y in points],fill=(190,217,186,200))
        d.rounded_rectangle((43*q,25*q,85*q,99*q),radius=8*q,fill=green)
        d.ellipse((53*q,48*q,75*q,70*q),fill=red)
    elif kind=='hatchery':
        d.ellipse((31*q,13*q,97*q,103*q),outline=green,width=int(7*q))
        for y in [41,65,87]:d.ellipse((55*q,(y-7)*q,73*q,(y+7)*q),fill=gold)
        d.rounded_rectangle((16*q,102*q,112*q,118*q),radius=4*q,fill=gold)
    elif kind=='reactor':
        d.rounded_rectangle((27*q,28*q,101*q,107*q),radius=10*q,outline=green,width=int(7*q))
        d.rectangle((42*q,12*q,86*q,28*q),fill=gold)
        d.rectangle((42*q,107*q,86*q,118*q),fill=gold)
        d.ellipse((46*q,48*q,82*q,84*q),fill=red)
    return im.resize((size,size),Image.Resampling.LANCZOS)

def build(library=None):
    SOURCE.mkdir(parents=True,exist_ok=True)
    originals={
        'white-general.png':'海帕姆_将军_无 (1).png',
        'gray-winged-soldier.png':'海帕姆_长生军_离子步枪（飞行）.png',
        'flag-reference.png':'海帕姆_火炮呼嚎官_海帕姆军旗.png',
    }
    if library:
        for dest,name in originals.items():shutil.copy2(library/name,SOURCE/dest)
    records=[]
    portraits=[('white','01','haipam-white-helmet-v3.png'),('gray','01','haipam-gray-helmet-folded-v3.png'),('white','02','haipam-white-governor-v1.png'),('gray','02','haipam-gray-worker-v1.png'),('white','emperor','haipam-emperor-no-feelers-v2.png'),('white','admiral','haipam-white-admiral-v1.png'),('white','scientist','haipam-white-scientist-v1.png'),('gray','space_worker','haipam-gray-space-worker-v1.png')]
    for key,variant,filename in portraits:
        src=ROOT/'assets/portraits'/filename
        if not src.exists(): raise FileNotFoundError('Normal-proportion source required; no chibi fallback: '+str(src))
        im=Image.open(src).convert('RGBA')
        # Engine 2D portrait box is 575x380. Preserve the complete figure and wings.
        factor=min(555/im.width,370/im.height)
        portrait=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(575,380),(0,0,0,0));canvas.alpha_composite(portrait,((575-portrait.width)//2,380-portrait.height))
        save(canvas,MOD/f'gfx/interface/portraits/haipam_{key}_{variant}.dds')
        save(canvas,ROOT/f'assets/previews/haipam_{key}_{variant}.png')
        records.append({'role':key+'_portrait_'+variant,'source_file':src.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':f'gfx/interface/portraits/haipam_{key}_{variant}.dds','size':[575,380],'method':'Built-in image_gen from user-provided role and biology references; aspect-preserving DDS export','helmet':variant in ['01','space_worker'],'wings':'folded' if key=='gray' else 'none','biological_reference':'user-references-20261016/gray-biology.png' if key=='gray' else 'user-references-20261016/emperor.png' if variant=='emperor' else 'user-references-20261016/white-face.png'})
    for size,folder in [(128,''),(256,'map'),(24,'small')]:
        save(species_mark(size),MOD/'flags/haipam'/folder/'haipam_royal_crest.dds')
    for key,kind,size in [('trait_haipam_white','white',29),('trait_haipam_gray','gray',29),('civic_haipam_royal_biology','white',29),('building_haipam_royal_hatchery','hatchery',78),('building_haipam_reactor','reactor',78)]:
        folder='buildings' if kind in ['hatchery','reactor'] else 'haipam'
        save(icon(kind,size),MOD/f'gfx/interface/icons/{folder}/{key}.dds')
        save(icon(kind,128),ROOT/f'assets/previews/{key}.png')
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><g fill="#e5c265"><path d="M43 16H85L78 30H50Z"/><path d="M58 76L77 80L68 103Z"/><path d="M24 34L30 63L49 99L43 75L35 48Z"/><path d="M104 34L98 63L79 99L85 75L93 48Z"/><circle cx="64" cy="53" r="8" fill="none" stroke="#e5c265" stroke-width="6"/></g></svg>'''
    # Previous simplified helmet crest SVG remains an unused historical source.
    for original,role in [('white-general.png','helmet_crest_reference_only'),('gray-winged-soldier.png','gray_helmet_reference_only'),('flag-reference.png','flag_palette_reference')]:
        records.append({'role':role,'source_file':originals[original],'source_sha256':hashlib.sha256((SOURCE/original).read_bytes()).hexdigest()})
    metadata={'portraits':'Eight adult-proportion role portraits from user-provided armor, emperor and distinct white/gray biological references; user requested larger heads.','emblem':'User-supplied species mark, image_gen black transparent extraction; white alpha-preserving engine tint-mask export. Previous helmet crest is no longer active.','flag_palette':'Blue/pale bands referenced from the local flag carrier art; mapped to available Stellaris swatches','ui_icons':'Species mark on white trait/civic, distinct original gray trait and building symbols; new building art follows in gameplay release','animated':False,'in_game_visual_acceptance':False,'sources':records,'generation_prompts':['assets/character-prompts-v033.json','assets/character-prompts-v033-b.json','assets/species-mark-prompt.json']}
    (ROOT/'assets/visual-assets.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'normal_proportion_portraits':8,'flag_sizes':3,'custom_ui_icons':5,'portrait_generation':'built-in image_gen from user-provided character and biology references','game_visual_validation':False}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',type=Path);args=p.parse_args();build(args.library)
