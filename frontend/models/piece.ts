export interface PracticeRecording {
  id: string; pieceId: string; createdAt: string; durationMs: number;
  mimeType: string; blob: Blob; objectUrl: string;
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
  createdAt: string;
  updatedAt: string;
  practiceRecording: PracticeRecording | null;
}

export interface PieceResponse {
  id: string; title: string | null; composer: string | null;
  part_names: string[]; measure_count: number; time_signatures: string[];
  key_signatures: string[]; original_filename: string; created_at: string; updated_at: string;
}

export function pieceFromResponse(value: PieceResponse, recording: PracticeRecording | null = null): Piece {
  return { id: value.id, title: value.title, composer: value.composer, partNames: value.part_names,
    measureCount: value.measure_count, timeSignatures: value.time_signatures,
    keySignatures: value.key_signatures, originalFilename: value.original_filename,
    createdAt: value.created_at, updatedAt: value.updated_at, practiceRecording: recording };
}
