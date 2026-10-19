"""Original, unaltered cell crops for independent visual repair; no typed votes."""
import json,argparse
from PIL import Image,ImageDraw
from sources import OUT,save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--extension',action='store_true');ap.add_argument('--checkpoint');args=ap.parse_args();prefix=f'replay-{args.checkpoint}' if args.checkpoint else 'replay-extension' if args.extension else 'replay';x=json.loads((OUT/(f'replay-{args.checkpoint}-comparison.json' if args.checkpoint else 'replay-extension-comparison.json' if args.extension else 'reviewed-replay-comparison.json')).read_text());cards=[];pointers=[]
    for i,r in enumerate(x['disagreements']):
        directory=OUT/'extracts/reviewed-replay'/r['source_id'];im=Image.open(directory/f'p{r["page"]:04d}-original.png');box=r['candidate_bounds'];hb=r['header_bounds'];cell=im.crop((box[0]-4,box[1]-4,box[2]+4,box[3]+4));header=im.crop(tuple(hb)).rotate(270,expand=True)
        card=Image.new('RGB',(570,270),'white');d=ImageDraw.Draw(card);d.text((8,8),f'{i+1}. {r["source_id"]}',fill='black');d.text((8,27),f'page {r["page"]}, printed column {r["source_column"]}; {r["candidate"]}',fill='black')
        header.thumbnail((530,60));card.paste(header,(8,50));cell=cell.resize((cell.width*3,cell.height*3));cell.thumbnail((540,150));card.paste(cell,(8,115));cards.append(card)
        pointers.append({k:r[k] for k in ['source_id','page','source_column','candidate','header_bounds','candidate_bounds']} | dict(review_card=i+1))
    for j in range(0,len(cards),10):
        subset=cards[j:j+10];atlas=Image.new('RGB',(1140,270*((len(subset)+1)//2)),'#eeeeee')
        for k,c in enumerate(subset):atlas.paste(c,((k%2)*570,(k//2)*270))
        path=OUT/'qa'/f'{prefix}-original-disagreements-{j//10+1}.png';atlas.save(path)
    save(OUT/'source'/f'{prefix}-original-disagreement-pointers.json',pointers)
    print(len(cards),'original-only cells; no comparison votes printed')
if __name__=='__main__':main()
