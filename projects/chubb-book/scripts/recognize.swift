// Local, offline recognition. No scans leave this computer.
import Foundation
import Vision
import NaturalLanguage

for path in CommandLine.arguments.dropFirst() {
    do {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesCPUOnly = true
        request.recognitionLanguages = ["en-AU", "en-US"]
        request.usesLanguageCorrection = true
        let faces = VNDetectFaceRectanglesRequest()
        faces.usesCPUOnly = true
        try VNImageRequestHandler(url: URL(fileURLWithPath: path)).perform([request, faces])
        let lines: [[String: Any]] = (request.results ?? []).compactMap { observation in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            let b = observation.boundingBox
            return ["text": candidate.string, "confidence": candidate.confidence,
                    "box": [b.minX, 1-b.maxY, b.width, b.height]]
        }
        let text = lines.compactMap { $0["text"] as? String }.joined(separator: "\n")
        let tagger = NLTagger(tagSchemes: [.nameType])
        tagger.string = text
        var names = Set<String>()
        if !text.isEmpty {
            tagger.enumerateTags(in: text.startIndex..<text.endIndex, unit: .word, scheme: .nameType, options: [.omitWhitespace, .omitPunctuation, .joinNames]) { tag, range in
                if tag == .personalName { names.insert(String(text[range])) }
                return true
            }
        }
        let boxes = (faces.results ?? []).map { b -> [Double] in
            let r = b.boundingBox
            return [r.minX, 1-r.maxY, r.width, r.height]
        }
        let result: [String: Any] = ["file": path, "engine": "Apple Vision accurate / NaturalLanguage", "text": text, "lines": lines, "candidate_names": names.sorted(), "face_candidates": boxes]
        let data = try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
        print(String(data: data, encoding: .utf8)!)
        fflush(stdout)
    } catch {
        fputs("Recognition failed for \(path): \(error)\n", stderr)
        exit(1)
    }
}
