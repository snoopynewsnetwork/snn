// Original-image OCR aid. Output is raw Apple Vision observations, never votes.
import Foundation
import Vision

guard CommandLine.arguments.count == 2 else { fatalError("usage: vision_ocr_turnout image.png") }
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
let handler = VNImageRequestHandler(url: url, options: [:])
try handler.perform([request])
let records: [[String: Any]] = (request.results ?? []).map { observation in
    let r = observation.boundingBox
    return [
        "text": observation.topCandidates(1).first?.string ?? "",
        "confidence": observation.topCandidates(1).first?.confidence ?? 0,
        "x": r.origin.x, "y": r.origin.y,
        "width": r.width, "height": r.height
    ]
}
let data = try JSONSerialization.data(withJSONObject: records, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
