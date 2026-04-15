export default function PreTradePage() {
  return (
    <section className="card stack-md">
      <p className="eyebrow">Primary module</p>
      <h2>Pre-Trade Evaluation</h2>
      <p>
        This screen will collect ticker, entry zone, stop loss, target, and time horizon,
        then return a deterministic verdict of VALID, WAIT, or INVALID.
      </p>
    </section>
  );
}
