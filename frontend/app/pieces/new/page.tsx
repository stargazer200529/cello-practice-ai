import Link from "next/link";
import { PieceUploadForm } from "../../../components/PieceUploadForm";

export default function NewPiecePage() {
  return <main><section className="hero"><Link href="/">← Home</Link>
    <p className="eyebrow page-eyebrow">New piece</p><h1>Upload a score</h1>
    <p className="summary">MusicXML is validated by the existing parser, then saved as a Piece in My Music.</p>
    <PieceUploadForm /><p className="temporary-note">No file or piece is permanently stored. Multi-piece library support is not implemented yet.</p>
  </section></main>;
}
