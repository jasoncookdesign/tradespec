'use client';

import { useEffect, useState } from 'react';

import { getActiveTrades } from '../../lib/api';
import { ActiveTrade } from '../../lib/types';

export default function ActiveTradePage() {
  const [trades, setTrades] = useState<ActiveTrade[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    getActiveTrades()
      .then(setTrades)
      .catch(() => {
        setError('Start the API on localhost:8000 to load active-trade guidance.');
      });
  }, []);

  return (
    <section className="stack-lg">
      <div className="card stack-md">
        <p className="eyebrow">Secondary module</p>
        <h2>Active Trade Stabilizer</h2>
        <p>
          This screen is wired to the active-trades endpoint so the guidance layer can be
          extended in later steps.
        </p>
        {error ? <p className="notice">{error}</p> : null}
      </div>

      {trades.map((trade) => (
        <div className="card stack-md" key={trade.id}>
          <h3>{trade.trade_spec_id}</h3>
          <p>
            <strong>Guidance:</strong> {trade.guidance_status}
          </p>
          <p>{trade.guidance_message}</p>
          <p>
            <strong>P&amp;L:</strong> {trade.pnl_percent}%
          </p>
        </div>
      ))}
    </section>
  );
}
