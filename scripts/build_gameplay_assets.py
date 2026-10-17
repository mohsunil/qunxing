"""Export selected original PNGs and native UI glyphs into game asset formats.

Pillow is a rebuild dependency only. All final DDS files ship in the source.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
BUILDINGS={
 'royal_hatchery':'royal-hatchery-v1.png', 'reactor':'reaction-vat-v1.png',
 'royal_hall':'royal-hall-v1.png','royal_design_bureau':'royal-design-bureau-v1.png',
 'graviton_temple':'graviton-temple-v1.png','postal_hub':'postal-hub-v1.png',
}
def save(im,path):path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
def fit(im,size,pad=3):
    result=Image.new('RGBA',size,(0,0,0,0));im=im.copy();im.thumbnail((size[0]-2*pad,size[1]-2*pad),Image.Resampling.LANCZOS)
    result.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return result
def glyph(kind,color=(225,192,112,255)):
    im=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(im)
    if kind=='fleet':
        for x,y in [(48,150),(128,78),(208,150)]:
            d.polygon([(x,y-38),(x-28,y+30),(x,y+18),(x+28,y+30)],fill=color)
        d.line([(48,184),(128,214),(208,184)],fill=color,width=12)
    elif kind=='axis':
        d.rounded_rectangle((32,90,175,170),12,outline=color,width=12)
        d.rectangle((165,112,235,147),fill=color)
        for x in [60,94,128]:d.line((x,78,x,180),fill=color,width=10)
    elif kind=='genes':
        d.line([(65,25),(185,83),(65,146),(185,230)],fill=color,width=13)
        d.line([(185,25),(65,83),(185,146),(65,230)],fill=color,width=13)
        for y in [53,114,181]:d.line((85,y,170,y),fill=color,width=9)
    return im
def build():
    records=[];images={};sprites=[]
    for key,filename in BUILDINGS.items():
        src=ROOT/'assets/buildings'/filename;im=Image.open(src).convert('RGBA');images[key]=im
        out='gfx/interface/icons/buildings/building_haipam_'+key+'.dds'
        save(fit(im,(78,78)),MOD/out);save(fit(im,(256,256)),ROOT/f'assets/previews/building_haipam_{key}.png')
        records.append({'building':key,'source':src.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':out})
    mappings={'royal_biology':'royal_hatchery','royal_governance':'royal_hall','royal_design':'royal_design_bureau','postal_fleets':'postal_hub','graviton_cult':'graviton_temple','dual_helix':'genes','planetary_arsenal':'fleet','fleetization':'fleet','axial_small':'axis','axial_medium':'axis','axial_heavy':'axis'}
    for key,source in mappings.items():
        im=images[source] if source in images else glyph(source)
        save(fit(im,(128,128)),MOD/f'gfx/interface/icons/technologies/tech_haipam_{key}.dds')
    for name,source in [('royal_hall','royal_hall'),('hatchery','royal_hatchery'),('ling','graviton_temple'),('postal','postal_hub'),('arsenal','royal_design_bureau')]:
        # A building information card, not a claimed scene illustration.
        card=Image.new('RGBA',(450,150),(23,33,47,255));card.alpha_composite(fit(images[source],(450,150),4))
        path=f'gfx/event_pictures/haipam_{name}.dds';save(card,MOD/path)
        sprites.append(f'spriteType = {{ name = "GFX_haipam_evt_{name}" texturefile = "{path}" }}')
    save(fit(images['graviton_temple'],(29,29)),MOD/'gfx/interface/icons/haipam/trait_haipam_ling.dds')
    save(fit(images['graviton_temple'],(64,64)),MOD/'gfx/interface/icons/haipam/army_haipam_ling.dds')
    save(fit(glyph('axis'),(64,64)),MOD/'gfx/interface/icons/haipam/haipam_axis.dds')
    sprites.extend([
      'spriteType = { name = "GFX_army_type_haipam_ling" texturefile = "gfx/interface/icons/haipam/army_haipam_ling.dds" }',
      'spriteType = { name = "GFX_haipam_axial_plasma" texturefile = "gfx/interface/icons/haipam/haipam_axis.dds" }',
      'spriteType = { name = "GFX_haipam_royal_continuity" texturefile = "gfx/interface/icons/haipam/civic_haipam_royal_biology.dds" }',
    ])
    (MOD/'interface/haipam_gameplay_icons.gfx').write_text('spriteTypes = {\n '+'\n '.join(sprites)+'\n}\n',encoding='utf-8')
    (ROOT/'assets/gameplay-assets.json').write_text(json.dumps({'tool':'built-in image_gen for building PNGs; code-native UI glyphs and mechanical format export','concept_art_not_verified_canon':True,'building_icons':records,'event_pictures':'Building information cards, not full illustrated scenes','runtime_verified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'building_icons':len(BUILDINGS),'technology_icons':len(mappings),'event_cards':5,'runtime_verified':False}))
if __name__=='__main__':build()
