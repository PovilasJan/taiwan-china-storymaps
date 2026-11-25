"""Build the Lithuanian StoryMaps import document and original figures from audited data.

Run from the repository root: python scripts/build.py
"""
from pathlib import Path
import json, math, re
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'assets'
DOCS = ROOT/'documents'
DATA = ROOT/'data'
for directory in (ASSETS,DOCS): directory.mkdir(exist_ok=True)
DOMAINS = ['Ekonomika','Švietimas ir technologijos','Sveikata ir demografija','Ekologija']
COLORS = ['#426E9C','#A2632E','#477C7B','#63804C']

def font(size, bold=False):
    candidates = [Path('C:/Windows/Fonts')/('arialbd.ttf' if bold else 'arial.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for f in candidates:
        if f.exists(): return ImageFont.truetype(str(f),size)
    return ImageFont.load_default(size=size)

def fmt(value):
    if value is None: return 'Nėra'
    if isinstance(value,str): return value
    if value == int(value): return f'{int(value):,}'.replace(',','\u00a0')
    return f'{value:,.2f}'.rstrip('0').rstrip('.').replace(',','\u00a0').replace('.',',')

def wrapdraw(draw, xy, text, width, fnt, fill='#263238', spacing=10, anchor='la'):
    text=text.replace('₂','2')
    x,y=xy
    lines=[]
    for para in text.split('\n'):
        line=''
        for word in para.split():
            candidate=(line+' '+word).strip()
            if draw.textlength(candidate,font=fnt)>width and line:
                lines.append(line); line=word
            else: line=candidate
        lines.append(line)
    for line in lines:
        draw.text((x,y),line,font=fnt,fill=fill,anchor=anchor)
        y += fnt.size+spacing
    return y

def wheel(rows,country,filename):
    w,h=2200,2400
    img=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(img)
    title='Taivanas' if country=='taiwan' else 'Žemyninė Kinija'
    d.text((1100,95),title,font=font(75,True),fill='#172D3E',anchor='mm')
    scored=sum(r['scores'][country] is not None for r in rows)
    d.text((1100,185),f'Darnių ratų profilis  •  įvertinta {scored} iš 28 kriterijų',font=font(38),fill='#54616B',anchor='mm')
    cx,cy=1100,1130; inner=180; outer=770; step=(outer-inner)/9
    for idx,row in enumerate(rows):
        start=-90+idx*360/28; end=start+360/28
        value=row['scores'][country]
        color=COLORS[DOMAINS.index(row['domain'])]
        for level in range(1,10):
            lo=inner+(level-1)*step; hi=inner+level*step
            pts=[]
            for j in range(9):
                a=math.radians(start+.35+(end-start-.7)*j/8)
                pts.append((cx+hi*math.cos(a),cy+hi*math.sin(a)))
            for j in range(8,-1,-1):
                a=math.radians(start+.35+(end-start-.7)*j/8)
                pts.append((cx+lo*math.cos(a),cy+lo*math.sin(a)))
            fill=color if value is not None and level<=value else ('#E6E8EB' if value is None else '#FFFFFF')
            d.polygon(pts,fill=fill,outline='#CAD0D6',width=2)
        a=math.radians((start+end)/2)
        x=cx+(outer+105)*math.cos(a); y=cy+(outer+105)*math.sin(a)
        d.text((x,y-20),row['id'],font=font(40,True),fill='#263238',anchor='mm')
        score_label='N/V' if value is None else str(value)
        d.text((x,y+30),score_label,font=font(34),fill='#687480',anchor='mm')
    d.text((cx,cy-30),'1–9',font=font(62,True),fill='#172D3E',anchor='mm')
    d.text((cx,cy+42),'balai',font=font(37),fill='#54616B',anchor='mm')
    y=2110
    for i,domain in enumerate(DOMAINS):
        x=100+(i%2)*1100; yy=y+(i//2)*65
        d.rectangle((x,yy-15,x+30,yy+15),fill=COLORS[i])
        d.text((x+50,yy),domain,font=font(33),fill='#263238',anchor='lm')
    d.text((1100,2290),'1 = prasčiausias imties intervalas; 9 = geriausias.',font=font(32),fill='#54616B',anchor='mm')
    d.text((1100,2340),'Kriterijų kodai, duomenys ir atskaitos ribos pateikti lentelėse.',font=font(30),fill='#54616B',anchor='mm')
    img.save(ASSETS/filename)

def add_link(p,text,url):
    r_id=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    el=OxmlElement('w:hyperlink');el.set(qn('r:id'),r_id)
    run=OxmlElement('w:r'); props=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'315B7C');props.append(c);run.append(props)
    t=OxmlElement('w:t');t.text=text;run.append(t);el.append(run);p._p.append(el)

def add_text(doc,text,style=None):
    if style in ['Title','Heading 1','Heading 2','Heading 3']:
        text=re.sub(r'[^\w\s]',' ',text)
        text=re.sub(r'\s+',' ',text).strip()
    p=doc.add_paragraph(style=style)
    # Preserve readable links without leaking Markdown punctuation into Word.
    chunks=re.split(r'(https?://\S+)',text)
    for chunk in chunks:
        if chunk.startswith(('http://','https://')): add_link(p,'Atverti šaltinį',chunk)
        else: p.add_run(chunk.replace('**',''))
    return p

def table(doc,headers,records,widths):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    for column,width in zip(t.columns,widths):column.width=Inches(width)
    table_width=t._tbl.tblPr.find(qn('w:tblW'))
    table_width.set(qn('w:type'),'dxa');table_width.set(qn('w:w'),str(round(sum(widths)*1440)))
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
    t._tbl.tblPr.append(borders)
    for cell,header,width in zip(t.rows[0].cells,headers,widths):
        cell.width=Inches(width);cell.text=header
        tcPr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDF2');tcPr.append(shade)
        for run in cell.paragraphs[0].runs:run.bold=True
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for record in records:
        cells=t.add_row().cells
        for i,(cell,text,width) in enumerate(zip(cells,record,widths)):
            cell.width=Inches(width);cell.text=str(text);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(5)
                if i>0:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:run.font.size=Pt(9.5)
            tcPr=cell._tc.get_or_add_tcPr();marg=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                tag=OxmlElement('w:'+side);tag.set(qn('w:w'),'85');tag.set(qn('w:type'),'dxa');marg.append(tag)
            tcPr.append(marg)
        trPr=t.rows[-1]._tr.get_or_add_trPr();trPr.append(OxmlElement('w:cantSplit'))
    return t

def picture(doc,name,caption,width=6.65):
    if 'darnus-ratas' in name:width=5.8
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    pic=p.add_run().add_picture(str(ASSETS/name),width=Inches(width))
    pic._inline.docPr.set('descr',caption)
    p.paragraph_format.keep_with_next=True
    p=add_text(doc,caption,'Caption')
    p.paragraph_format.space_after=Pt(10)

def locator():
    data=json.loads((DATA/'map-context.geojson').read_text(encoding='utf-8'))
    im=Image.new('RGB',(2200,1480),'white');d=ImageDraw.Draw(im)
    d.text((100,80),'Taivanas ir žemyninė Kinija Rytų Azijoje',font=font(60,True),fill='#172D3E')
    x0,y0,x1,y1=90,210,2110,1300
    d.rectangle((x0,y0,x1,y1),fill='#EDF3F5')
    def merc(lat):return math.log(math.tan(math.pi/4+math.radians(lat)/2))
    bottom,top=merc(15),merc(55)
    def xy(lon,lat):return (x0+(lon-70)/75*(x1-x0),y1-(merc(max(-85,min(85,lat)))-bottom)/(top-bottom)*(y1-y0))
    overlay=Image.new('RGB',(x1-x0,y1-y0),'#EDF3F5');od=ImageDraw.Draw(overlay)
    for f in data['features']:
        key=f['properties'].get('ADM0_A3')
        col='#426E9C' if key=='CHN' else '#C18246' if key=='TWN' else '#DDE3E3'
        geo=f['geometry'];polys=geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]
        for poly in polys:
            pts=[(xy(lon,lat)[0]-x0,xy(lon,lat)[1]-y0) for lon,lat in poly[0]]
            od.polygon(pts,fill=col,outline='white',width=2)
    im.paste(overlay,(x0,y0));d=ImageDraw.Draw(im)
    d.text(xy(103,35),'ŽEMYNINĖ KINIJA',font=font(48,True),fill='white',anchor='mm')
    tx,ty=xy(121,23.7);lx,ly=xy(131,29)
    d.line((tx,ty,lx-18,ly+35),fill='#80552D',width=4)
    d.ellipse((tx-7,ty-7,tx+7,ty+7),fill='#80552D')
    d.text((lx,ly),'TAIVANAS',font=font(45,True),fill='#80552D',anchor='mm')
    d.text((100,1350),'Made with Natural Earth  •  1:110 mln. mastelio geografinės orientacijos schema',font=font(28),fill='#54616B')
    d.text((100,1400),'Statistikoje Honkongas ir Makao nepridedami prie nagrinėjamos žemyninės Kinijos.',font=font(28),fill='#54616B')
    im.save(ASSETS/'rytu-azijos-zemelapis.png')

def comparison(rows):
    by={r['id']:r for r in rows}
    panels=[('H1','Tikėtina gyvenimo trukmė gimus',90),('ENV1','Teritorinės CO₂ emisijos gyventojui',15),('ENV3','Atsinaujinanti elektra',40),('ENV5','Elektros emisijų intensyvumas',800)]
    im=Image.new('RGB',(2200,1460),'white');d=ImageDraw.Draw(im)
    d.text((100,60),'2023 metų rodiklių palyginimas',font=font(62,True),fill='#172D3E')
    for i,(code,title,limit) in enumerate(panels):
        r=by[code];x=100+(i%2)*1090;y=240+(i//2)*510
        wrapdraw(d,(x,y),title,940,font(38,True))
        d.text((x,y+100),r['unit'].replace('₂','2')+'  •  '+code,font=font(28),fill='#54616B')
        for j,country in enumerate(['taiwan','china']):
            yy=y+190+j*105;val=r[country]['value'];col='#426E9C' if country=='taiwan' else '#C18246'
            d.text((x,yy),('Taivanas' if country=='taiwan' else 'Kinija'),font=font(29),fill='#263238')
            d.rectangle((x+200,yy,x+200+val/limit*550,yy+45),fill=col)
            d.text((x+770,yy+22),fmt(val),font=font(34,True),fill='#263238',anchor='lm')
        d.line((x+200,y+370,x+750,y+370),fill='#C4CCD2',width=2)
        d.text((x+200,y+390),'0',font=font(25),fill='#54616B',anchor='mm')
        d.text((x+750,y+390),str(limit),font=font(25),fill='#54616B',anchor='mm')
    d.text((100,1345),'Šaltiniai: MOHW, NHC, Global Carbon Budget, Ember ir OWID; rodiklių apibrėžtys pateiktos duomenų lentelėje.',font=font(27),fill='#54616B')
    d.text((100,1400),'Stulpeliai prasideda nuo nulio. Tai faktinių reikšmių, o ne bendro darnumo reitingo palyginimas.',font=font(27),fill='#54616B')
    im.save(ASSETS/'keturiu-rodikliu-palyginimas.png')

def methodology(rows):
    text='''# Skaičiavimo metodika

Naudojamas vartotojo pasirinktas užduoties pristatymo metodas: atskaitos reikšmių diapazonas padalijamas į devynis **vienodo pločio intervalus**. Tai nėra šalių padalijimas į devynias vienodo dydžio reitingo grupes.

## Formulė

Kiekvieno kriterijaus intervalų plotis `h = (max − min) / 9`. Kai didesnė reikšmė laikoma palankesne pasirinkto kriterijaus prasme, normalizuota reikšmė yra `z = (x − min) / (max − min)`. Kai mažesnė reikšmė palankesnė, `z = (max − x) / (max − min)`.

Balas yra `min(9, max(1, ceil(9 × z)))`. Taip vidinė riba patenka į žemesnį intervalą, o pats minimumas ir maksimumas patenka į 1 arba 9 balą, priklausomai nuo krypties. Pavyzdžiui, kai min=10, max=100 ir didesnė reikšmė palankesnė, 10 bei 20 duoda 1, 20,01 duoda 2, o 100 duoda 9. Skaičiuojama iš išsaugoto skaitinio tikslumo; dokumento lentelėse reikšmės apvalinamos tik rodymui.

Abiem nagrinėjamoms teritorijoms konkretaus kriterijaus ribos vienodos. Nė vienas balas nėra ranka priskirtas pagal norimą rezultatą. Skaičiavimus galima atkurti `python scripts/score.py`.

## Etalonai

- WDI: to paties rodiklio ir metų šalys bei teritorijos su duomenimis, be regioninių agregatų; pridėta Taivano nacionalinė reikšmė. Nacionalinių apklausų ir modeliuotų įverčių palyginimai orientaciniai.
- PWT 11.0: atskiros ekonomikos su tikrais to metų duomenimis. PGP darbo našumo ir vartojimo rodikliams taikomas paties šaltinio `i_outlier=Regular` filtras. Darbo pajamų dalis nėra PGP kainų perskaičiavimas, todėl tam kriterijui šis kainų išskirčių filtras netaikomas.
- Švietimas: nurodytų lyginamųjų lentelių bendrų metų imtys. Atmestos kitų metų ar nesuderinamos aprėpties eilutės. EDU03 Kinijos reikšmė pridėta iš tų pačių metų nacionalinio šaltinio; mokytojų apskaitos skirtumai išlieka.
- Energija ir CO2: to metų OWID serijos įrašai su trijų raidžių ISO kodais ir faktinėmis reikšmėmis; regioniniai agregatai atmesti. Imtyse yra ir priklausomų teritorijų.
- H5, H6 ir ENV6: devynios Rytų ir Pietryčių Azijos ekonomikos — Taivanas, Kinija, Japonija, Pietų Korėja, Singapūras, Tailandas, Vietnamas, Malaizija ir Mianmaras. Tai tikslinė mokomoji palyginimo imtis, ne reprezentatyvus viso regiono ar pasaulio reitingas.

`data/indicators.json` saugomi visi panaudoti imčių nariai, šaltinių URL, metai, ribos ir formulės. Mažoms IHME imtims nurodytos viešai diagramose rodomos suapvalintos faktinės reikšmės; pilnas riboto platinimo pirminis duomenų rinkinys neperpublikuotas.

## Visos ribos ir rezultatai

Rodyklė aukštyn reiškia, kad didesnė reikšmė gauna didesnį balą; rodyklė žemyn reiškia apverstą skalę. Lentelės ribos suapvalintos rodymui. Skaičiavimas naudoja visą JSON tikslumą.

| Kodas | Kriterijus | Kryptis | Metai | Imties n | Min. | Maks. | Taivano balas | Kinijos balas |
|---|---|:---:|---|---:|---:|---:|---:|---:|
'''
    for r in rows:
        b=r['benchmark'];arrow='↑' if r['direction']=='higher' else '↓'
        text+=f"| {r['id']} | {r['indicator']} | {arrow} | {b['year']} | {b['n']} | {fmt(b['min'])} | {fmt(b['max'])} | {r['scores']['taiwan']} | {r['scores']['china']} |\n"
    text+='''
## Kaip interpretuoti profilį

1. Balas nusako vietą **intervale pasirinktoje imtyje**, o ne absoliučią socialinę ar ekologinę normą. Didelių etalono išskirčių paveikti intervalai gali daug ekonomikų sutelkti į tą patį balą.
2. Atskirų kriterijų etalonai ir metai skiriasi. Negalima iš ratų ploto apskaičiuoti vienos „darnesnės šalies“ ar oficialaus DVT reitingo. H6 Taivano 1 balas reiškia didžiausią vėžio mirtingumo reikšmę tik pasirinktoje devynių ekonomikų imtyje.
3. Darbo našumas, BVP ir vartojimas susiję. Vaikų mirtingumo rodikliai persidengia. Energetikos ir emisijų rodikliai bei oro taršos ir ligų naštos rodikliai taip pat susiję. Dėl to bendras arba sričių balų vidurkis neskaičiuojamas.
4. Darbo pajamų dalis BVP matuoja darbo ir kapitalo pajamų santykį. Tai nėra Gini indeksas, atlyginimų mediana ar nelygybė tarp namų ūkių. Vartojimo kriterijus apima namų ūkius ir valdžią.
5. Mirtingumo nuo vėžio, širdies ir kraujagyslių ligų bei oro taršai priskiriami rodikliai standartizuoti pagal amžių ir modeliuoti. Nenaudojama taisyklė, kad vyresnė gyventojų struktūra savaime blogesnė. Modelių neapibrėžtumo intervalai šioje paprastoje skalėje nepavaizduoti.
6. Paveikslėliai yra pasirinktos metodikos mokomasis rezultatas, o ne oficialus valdžios, UNDP ar kitų duomenų teikėjų įvertinimas. Politikos efektyvumo priežastiniam vertinimui reikėtų papildomų tyrimų.
'''
    (DOCS/'metodika.md').write_text(text,encoding='utf-8')

def main():
    bundle=json.loads((DATA/'indicators.json').read_text(encoding='utf-8'))
    rows=bundle['indicators']
    assert len(rows)==28
    assert len({r['id'] for r in rows})==28
    for domain in DOMAINS:assert len([r for r in rows if r['domain']==domain])==7
    for r in rows:
        for country in ['taiwan','china']:
            assert r[country]['value'] is not None, r['id']
            assert r[country]['source'].startswith('https://'),r['id']
            score=r['scores'][country]
            assert score is None or (isinstance(score,int) and 1<=score<=9)
            if score is not None: assert r.get('benchmark') and r['benchmark']['max']>r['benchmark']['min']
    wheel(rows,'taiwan','taivano-darnus-ratas.png')
    wheel(rows,'china','kinijos-darnus-ratas.png')
    locator()
    comparison(rows)
    methodology(rows)
    story=(DOCS/'pasakojimas.md').read_text(encoding='utf-8')
    doc=Document();sec=doc.sections[0]
    for border in doc.styles.element.xpath('.//w:pBdr'):border.getparent().remove(border)
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.7);sec.left_margin=Inches(.8);sec.right_margin=Inches(.8)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
        st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
        st.font.size=Pt(11 if name=='Normal' else (25 if name=='Title' else 16 if name=='Heading 1' else 13 if name=='Heading 2' else 10))
        st.paragraph_format.space_after=Pt(7)
    doc.styles['Normal'].paragraph_format.line_spacing=1.12
    for name in ['Heading 1','Heading 2','Heading 3']:doc.styles[name].paragraph_format.space_before=Pt(13)
    doc.core_properties.author='DSR grupės darbas';doc.core_properties.last_modified_by='DSR grupės darbas'
    doc.core_properties.title='Taivano ir Kinijos darnios raidos palyginimas'
    for line in story.splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('# '):add_text(doc,line[2:],'Title')
        elif line.startswith('## '):add_text(doc,line[3:],'Heading 1')
        elif line.startswith('### '):add_text(doc,line[4:],'Heading 2')
        elif line.startswith('- '):add_text(doc,line[2:],'List Bullet')
        elif line.startswith('[[TABLE:'):
            domain=line.removeprefix('[[TABLE:').removesuffix(']]')
            selected=[r for r in rows if r['domain']==domain]
            records=[]
            for r in selected:
                vals=[]
                for country in ['taiwan','china']:
                    c=r[country];vals.append(f"{fmt(c['value'])}\n{c['year']}")
                records.append([r['id']+' '+r['indicator']+'\n'+r['unit'],*vals])
            table(doc,['Rodiklis ir matavimo vienetas','Taivanas\nReikšmė ir metai','Kinija\nReikšmė ir metai'],records,[3.7,1.6,1.6])
        elif line.startswith('[[IMAGE:'):
            name,caption=line.removeprefix('[[IMAGE:').removesuffix(']]').split('|',1)
            picture(doc,name,caption)
        else:add_text(doc,line)
    doc.add_page_break();add_text(doc,'Rodiklių šaltiniai ir vertinimo ribos','Heading 1')
    for r in rows:
        add_text(doc,r['id']+' '+r['indicator'],'Heading 2')
        p=doc.add_paragraph();p.add_run(f"Taivanas {r['taiwan']['year']}: ");add_link(p,r['taiwan'].get('source_title','Pirminis šaltinis'),r['taiwan']['source'])
        p=doc.add_paragraph();p.add_run(f"Kinija {r['china']['year']}: ");add_link(p,r['china'].get('source_title','Pirminis šaltinis'),r['china']['source'])
        add_text(doc,r['note'])
        for country,label in [('taiwan','Taivanas'),('china','Kinija')]:
            c=r[country]
            extra=[]
            if c.get('formula'):extra.append('Skaičiavimas: '+c['formula']+'.')
            if c.get('definition'):extra.append(c['definition'])
            if c.get('locator'):extra.append('Vieta šaltinyje: '+c['locator']+'.')
            if extra:add_text(doc,label+'. '+' '.join(extra))
        if r.get('source_citation'):add_text(doc,'Duomenų kilmė: '+r['source_citation'])
        if r.get('benchmark'):
            b=r['benchmark'];scope=b['scope'].rstrip('.; ');p=add_text(doc,f"Atskaita: {scope}; {b['year']}; n = {b['n']}; min. {fmt(b['min'])}; maks. {fmt(b['max'])}. ")
            add_link(p,'Atskaitos duomenys',b['source'])
            if b.get('notes'):
                notes=b['notes']
                add_text(doc,'Etalono atranka: '+(' '.join(notes) if isinstance(notes,list) else str(notes)))
            add_text(doc,f"Balai: Taivanas {fmt(r['scores']['taiwan'])}; Kinija {fmt(r['scores']['china'])}. {r['score_note']}")
        else:add_text(doc,'Balai neskiriami. '+r['score_note'])
    footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    path=DOCS/'taivanas-kinija-storymaps.docx';doc.save(path)
    # Produce a readable Markdown version alongside the DOCX source.
    readable=story
    for domain in DOMAINS:
        selected=[r for r in rows if r['domain']==domain]
        lines=['| Kodas ir rodiklis | Vienetas | Taivanas | Metai | Kinija | Metai |','|---|---|---:|---|---:|---|']
        for r in selected:
            lines.append(f"| {r['id']} {r['indicator']} | {r['unit']} | {fmt(r['taiwan']['value'])} | {r['taiwan']['year']} | {fmt(r['china']['value'])} | {r['china']['year']} |")
        readable=readable.replace('[[TABLE:'+domain+']]','\n'.join(lines))
    readable=re.sub(r'\[\[IMAGE:([^|]+)\|([^\]]+)\]\]',lambda m:'!['+m[2]+'](../assets/'+m[1]+')',readable)
    readable+='\n\n## Rodiklių šaltiniai\n\n'
    for r in rows:
        readable+=f"**{r['id']} {r['indicator']}.** [Taivano šaltinis]({r['taiwan']['source']}); [Kinijos šaltinis]({r['china']['source']}). {r['note']}\n\n"
    (DOCS/'pasakojimas-perziurai.md').write_text(readable.rstrip()+'\n',encoding='utf-8')
    summary={'indicators':len(rows),'scores_taiwan':sum(r['scores']['taiwan'] is not None for r in rows),'scores_china':sum(r['scores']['china'] is not None for r in rows),'docx':path.name}
    (DATA/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
