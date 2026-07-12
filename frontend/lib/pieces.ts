import { Piece, PieceResponse, pieceFromResponse } from "../models/piece";
import { apiUrl, checked } from "./api";

export async function listPieces(): Promise<Piece[]> {
  const response = await checked(await fetch(`${apiUrl}/pieces`, { cache: "no-store" }));
  return ((await response.json()) as PieceResponse[]).map((piece) => pieceFromResponse(piece));
}
export async function getPiece(id: string): Promise<Piece> {
  const response = await checked(await fetch(`${apiUrl}/pieces/${id}`, { cache: "no-store" }));
  return pieceFromResponse((await response.json()) as PieceResponse);
}
export async function createPiece(file: File): Promise<Piece> {
  const data = new FormData(); data.append("file", file);
  const response = await checked(await fetch(`${apiUrl}/pieces`, { method: "POST", body: data }));
  return pieceFromResponse((await response.json()) as PieceResponse);
}
export async function getPieceMusicXML(id: string) {
  return (await checked(await fetch(`${apiUrl}/pieces/${id}/musicxml`, { cache: "no-store" }))).text();
}
export async function deletePiece(id: string) {
  await checked(await fetch(`${apiUrl}/pieces/${id}`, { method: "DELETE" }));
}
