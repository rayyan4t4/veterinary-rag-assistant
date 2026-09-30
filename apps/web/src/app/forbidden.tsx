import Link from "next/link";
export default function Forbidden(){return <main className="auth-page"><section className="auth-card"><h1>Access restricted</h1><p className="muted">This area requires a server-validated administrator role.</p><Link className="btn" href="/dashboard">Return to dashboard</Link></section></main>}
