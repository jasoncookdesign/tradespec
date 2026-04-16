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
          Review the one primary action for the trade: hold, exit, or free the capital
          because the setup has expired.
        </p>
        {error ? <p className="notice">{error}</p> : null}
      </div>

      {trades.map((trade) => (
        <div className="card stack-md" key={trade.id}>
          <h3>{trade.trade_spec_id}</h3>
          <p className="guidanceMessage">
            <strong>{trade.guidance_status}:</strong> {trade.guidance_message}
          </p>
          <div className="grid twoColGrid">
            <p>
              <strong>P&amp;L:</strong> {trade.pnl_percent}%
            </p>
            <p>
              <strong>Thesis intact:</strong> {trade.thesis_intact ? 'Yes' : 'No'}
            </p>
            <p>
              <strong>Elapsed days:</strong> {trade.elapsed_days}
            </p>
            <p>
              <strong>Distance to stop:</strong> {trade.distance_to_stop_percent}%
            </p>
            <p>
              <strong>Distance to target:</strong> {trade.distance_to_target_percent}%
            </p>
          </div>
          <div>
            <strong>Expected behavior envelope</strong>
            <ul className="vocabulary">
              <li>
                Normal pullback range: {trade.normal_pullback_min_pct}% to{' '}
                {trade.normal_pullback_max_pct}%
              </li>
              <li>
                Expected time to move: {trade.expected_time_to_move_min_days} to{' '}
                {trade.expected_time_to_move_max_days} days
              </li>
            </ul>
          </div>
        </div>
      ))}
    </section>
  );
}
