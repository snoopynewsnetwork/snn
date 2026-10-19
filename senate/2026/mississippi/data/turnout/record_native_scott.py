"""Full original Scott embedded smaller upright form, transform scope explicit."""
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 g={p:geometry('scott',p,460,1381,[156,318],{'Ty Pinkins':(844,885),'Roger F. Wicker':(885,927)},rotation_override=0) for p in [2,3,4]}
 record('scott',[(2,['BEAT 4/BRANCH','Beat 1/Harperville','Beat 1/Hillsboro','Beat 1/North Forest','Beat 2/High Hill','Beat 2/Homewood','Beat 2/Lake','Beat 2/South Forest','Beat 2/Usry','Beat\n3/Cooperville/Springf','Beat 3/Eastwest\nMorton'],[79,355,367,438,131,55,103,376,33,41,322],[423,322,281,114,164,195,147,286,224,558,648],None),(3,['Beat 3/Northwest\nForest','Beat 3/Pulaski','Beat 4/Clifton','Beat 4/Contrell','Beat 4/Forkville','Beat 4/Ludlow','Beat 4/North Morton','Beat 5/Langs Mill','Beat 5/Northeast\nForest','Beat 5/Salem','Beat 5/Sebastopol'],[24,30,15,161,14,129,307,126,79,213,17],[101,253,71,84,211,266,204,394,324,228,393],None),(4,['Beat 5/Steele','TOTAL']+['']*9,[265,3680]+[None]*9,[231,6122]+[None]*9,2)],page_overrides=g);evidence('scott',[2,3,4])
if __name__=='__main__':main()
