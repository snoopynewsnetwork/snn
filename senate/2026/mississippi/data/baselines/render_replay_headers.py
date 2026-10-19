"""Original expanded header crops; no typed peer label shown in review cards."""
import json,argparse
from PIL import Image,ImageDraw
from sources import OUT
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--extension',action='store_true');ap.add_argument('--checkpoint');args=ap.parse_args();prefix=f'replay-{args.checkpoint}' if args.checkpoint else 'replay-extension' if args.extension else 'replay';rows=json.loads((OUT/(f'replay-{args.checkpoint}-label-comparison.json' if args.checkpoint else 'replay-extension-label-comparison.json' if args.extension else 'reviewed-replay-label-comparison.json')).read_text())['disagreements'];cards=[]
    for i,r in enumerate(rows):
        im=Image.open(OUT/'extracts/reviewed-replay'/r['source_id']/f'p{r["page"]:04d}-original.png');b=r['header_bounds'];crop=im.crop((b[0]-3,b[1]-12,b[2]+3,b[3]+12)).rotate(270,expand=True);crop=crop.resize((crop.width*2,crop.height*2));crop.thumbnail((380,155))
        card=Image.new('RGB',(400,200),'white');d=ImageDraw.Draw(card);d.text((6,5),f'{i+1}. {r["source_id"].replace("sos-2024-county-","")}; p{r["page"]} c{r["source_column"]}',fill='black');card.paste(crop,(8,28));cards.append(card)
    for j in range(0,len(cards),20):
        sub=cards[j:j+20];atlas=Image.new('RGB',(1600,200*((len(sub)+3)//4)),'#eeeeee')
        for k,c in enumerate(sub):atlas.paste(c,((k%4)*400,(k//4)*200))
        atlas.save(OUT/'qa'/f'{prefix}-original-headers-{j//20+1}.png')
    print(len(cards),'original-header cards')
if __name__=='__main__':main()
