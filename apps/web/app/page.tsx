import Link from 'next/link';

const workflowCards = [
  {
    href: '/pre-trade',
    title: 'Pre-Trade Gate',
    description: 'Evaluate whether a setup is VALID, WAIT, or INVALID before entering.',
  },
  {
    href: '/active-trade',
    title: 'Active Trade Stabilizer',
    description: 'Keep your plan intact once the trade is open.',
  },
  {
    href: '/journal',
    title: 'Trade Journal',
    description: 'Capture outcomes and reflect on repeat mistakes and strengths.',
  },
];

export default function HomePage() {
  return (
    <section className="stack-lg">
      <div className="hero card">
        <p className="eyebrow">Disciplined trading workflow</p>
        <h2>Rules first. AI second.</h2>
        <p>
          TradeSpec is a personal decision assistant for swing trading U.S. large-cap stocks
          and liquid ETFs. The deterministic rule engine remains authoritative.
        </p>
      </div>

      <div className="grid">
        {workflowCards.map((card) => (
          <Link className="card linkCard" href={card.href} key={card.href}>
            <h3>{card.title}</h3>
            <p>{card.description}</p>
          </Link>
        ))}
      </div>

      <div className="card">
        <h3>MVP vocabulary</h3>
        <ul className="vocabulary">
          <li><strong>VALID</strong>: setup passes the rule engine.</li>
          <li><strong>WAIT</strong>: setup is promising but incomplete.</li>
          <li><strong>INVALID</strong>: setup fails hard constraints.</li>
          <li><strong>Entry zone</strong>: acceptable opening price range.</li>
          <li><strong>Stop loss</strong>: invalidation level.</li>
          <li><strong>Target</strong>: expected profit objective.</li>
          <li><strong>Time horizon</strong>: planned holding window.</li>
          <li><strong>Expected behavior envelope</strong>: normal post-entry action.</li>
        </ul>
      </div>
    </section>
  );
}
