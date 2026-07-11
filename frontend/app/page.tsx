import Link from "next/link";
import { BackendStatus } from "../components/BackendStatus";
import { MusicLibrary } from "../components/MusicLibrary";

export default function Home() {
  return <main className="workspace-main"><section className="workspace"><header className="workspace-header"><div>
    <p className="eyebrow">Cello Practice AI</p><h1>My Music</h1><p className="summary">Your locally stored MusicXML pieces.</p></div>
    <Link className="primary-link" href="/pieces/new">Add a piece</Link></header><MusicLibrary /><BackendStatus />
  </section></main>;
}
