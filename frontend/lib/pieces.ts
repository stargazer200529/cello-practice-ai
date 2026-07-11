import { Piece, PieceResponse, pieceFromResponse } from "../models/piece";

export const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function checked(response: Response) {
  if (response.ok) return response;
  let message = "The request could not be completed.";
  try { const body = await response.json(); if (typeof body.detail === "string") message = body.detail; } catch {}
  throw new Error(message);
}

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
