export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="wordmark" href="/" aria-label="SwasthyaAI home">SwasthyaAI</a>
        <span className="demo-label">Local demo</span>
      </header>

      <main>
        <section className="intro" aria-labelledby="page-title">
          <p className="section-label">Care coordination</p>
          <h1 id="page-title">A clearer next step for care.</h1>
          <p className="intro-copy">
            Find the right kind of support, keep important details together, and
            know when to seek urgent help.
          </p>
        </section>

        <section className="care-path" aria-labelledby="care-path-title">
          <h2 id="care-path-title">Your care path</h2>
          <ol className="path-steps">
            <li><span className="step-number">01</span><span>Share what is needed</span></li>
            <li><span className="step-number">02</span><span>Review suitable care</span></li>
            <li><span className="step-number">03</span><span>Choose what happens next</span></li>
          </ol>
        </section>

        <section className="workspace" aria-labelledby="workspace-title">
          <div>
            <p className="section-label">Workspace</p>
            <h2 id="workspace-title">Care support</h2>
            <p>Your care conversations and appointments will appear here.</p>
          </div>
          <p className="empty-state">No care activity yet</p>
        </section>

        <aside className="safety-note" aria-label="Important safety information">
          This demo does not provide a medical diagnosis or emergency service.
          If someone may be in immediate danger in India, call 112.
        </aside>
      </main>
    </div>
  );
}
