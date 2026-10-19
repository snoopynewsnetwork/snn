// Offline original-raster OCR. Preserve all observations and token positions.
import Foundation
import Vision
import ImageIO
struct Word: Codable { let text:String; let box:[Double]; let confidence:Float }
struct Result: Codable { let path:String; let observations:[Word]; let words:[Word]; let error:String? }
for path in CommandLine.arguments.dropFirst() {
 do {
  let req=VNRecognizeTextRequest(); req.recognitionLevel = .accurate
  req.usesLanguageCorrection=false; req.recognitionLanguages=["en-US"]
  let handler=VNImageRequestHandler(url:URL(fileURLWithPath:path),options:[:]);try handler.perform([req])
  var observations=[Word]();var words=[Word]()
  for obs in req.results ?? [] {
   guard let cand=obs.topCandidates(1).first else {continue}
   let b=obs.boundingBox;observations.append(Word(text:cand.string,box:[b.minX,b.minY,b.maxX,b.maxY],confidence:cand.confidence))
   let s=cand.string;var cursor=s.startIndex
   for token in s.split(whereSeparator:{$0.isWhitespace}) {
    guard let r=s.range(of:String(token),range:cursor..<s.endIndex) else {continue};cursor=r.upperBound
    if let z=try? cand.boundingBox(for:r) { let b=z.boundingBox;words.append(Word(text:String(token),box:[b.minX,b.minY,b.maxX,b.maxY],confidence:cand.confidence)) }
   }
  }
  let r=Result(path:path,observations:observations,words:words,error:nil);let data=try JSONEncoder().encode(r);print(String(data:data,encoding:.utf8)! )
 } catch { let r=Result(path:path,observations:[],words:[],error:String(describing:error));let data=try! JSONEncoder().encode(r);print(String(data:data,encoding:.utf8)! ) }
}
