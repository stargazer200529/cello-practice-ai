import Link from "next/link";
import { BackendStatus } from "../components/BackendStatus";

export default function Home() {
  return <main><section className="hero"><p className="eyebrow">Cello Practice AI</p>
    <h1>Practice starts with a piece.</h1>
    <p className="summary">Create a temporary workspace from a MusicXML score to view its notation and metadata.</p>
    <Link className="primary-link" href="/pieces/new">Add a piece</Link>
    <p className="temporary-note">Pieces exist only in memory for now. Refreshing or restarting may clear the active piece.</p>
    <BackendStatus />
  </section></main>;
}
