export interface PracticeRecording {
  id: string;
  pieceId: string;
  createdAt: string;
  durationMs: number;
  mimeType: string;
  blob: Blob;
  objectUrl: string;
}

export interface Piece {
  id: string;
  title: string | null;
  composer: string | null;
  partNames: string[];
  measureCount: number;
  timeSignatures: string[];
  keySignatures: string[];
  originalFilename: string;
  musicXML: string;
  practiceRecording: PracticeRecording | null;
}

export interface ScoreMetadataResponse {
  title: string | null;
  composer: string | null;
  part_names: string[];
  measure_count: number;
  time_signatures: string[];
  key_signatures: string[];
  musicxml: string;
}

export function createTemporaryPiece(
  metadata: ScoreMetadataResponse,
  originalFilename: string,
  musicXML: string,
): Piece {
  return {
    id: crypto.randomUUID(),
    title: metadata.title,
    composer: metadata.composer,
    partNames: metadata.part_names,
    measureCount: metadata.measure_count,
    timeSignatures: metadata.time_signatures,
    keySignatures: metadata.key_signatures,
    originalFilename,
    musicXML,
    practiceRecording: null,
  };
}
