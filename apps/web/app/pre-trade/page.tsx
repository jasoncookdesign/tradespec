'use client';

import { useState } from 'react';

import { evaluateTicker, validateTrade } from '../../lib/api';
import { TickerEvaluation, TradeValidationResult } from '../../lib/types';

const sampleTrade = {
  ticker: 'MSFT',
  setup_type: 'breakout' as const,
  entry_zone_min: 100,
  entry_zone_max: 102,
  stop_loss: 96,
  target_price: 112,
  time_horizon_days: 10,
  thesis: 'Continuation after a clean breakout with defined risk.',
};

export default function PreTradePage() {
  const [ticker, setTicker] = useState('MSFT');
  const [evaluation, setEvaluation] = useState<TickerEvaluation | null>(null);
  const [validation, setValidation] = useState<TradeValidationResult | null>(null);
  const [error, setError] = useState('');

  async function handleEvaluateTicker() {
    setError('');

    try {
      const result = await evaluateTicker(ticker);
      setEvaluation(result);
    } catch {
      setError('Start the API on localhost:8000 to load the evaluation preview.');
    }
  }

  async function handleValidateTrade() {
    setError('');

    try {
      const result = await validateTrade({
        ...sampleTrade,
        ticker: ticker.trim().toUpperCase() || sampleTrade.ticker,
      });
      setValidation(result);
    } catch {
      setError('Trade validation preview is unavailable until the API is running.');
    }
  }

  return (
    <section className="stack-lg">
      <div className="card stack-md">
        <p className="eyebrow">Primary module</p>
        <h2>Pre-Trade Evaluation</h2>
        <p>
          Use the typed API contracts to preview both ticker evaluation and trade
          validation responses.
        </p>

        <div className="formRow">
          <label className="field">
            <span>Ticker</span>
            <input value={ticker} onChange={(event) => setTicker(event.target.value)} />
          </label>
          <div className="buttonRow">
            <button type="button" onClick={handleEvaluateTicker}>
              Evaluate ticker
            </button>
            <button className="secondaryButton" type="button" onClick={handleValidateTrade}>
              Validate sample trade
            </button>
          </div>
        </div>

        {error ? <p className="notice">{error}</p> : null}
      </div>

      {evaluation ? (
        <div className="card stack-md">
          <h3>Evaluation result</h3>
          <p>
            <strong>Status:</strong>{' '}
            <span className={`statusBadge status-${evaluation.status}`}>{evaluation.status}</span>
          </p>
          <p>{evaluation.trend_summary}</p>
          <p>{evaluation.momentum_summary}</p>
          <p>{evaluation.structure_summary}</p>
          <p>{evaluation.volatility_summary}</p>
          <p>
            <strong>Suggested entry zone:</strong> {evaluation.suggested_entry_zone.min_price} -{' '}
            {evaluation.suggested_entry_zone.max_price}
          </p>
          <p>
            <strong>Support zone:</strong> {evaluation.suggested_support_zone.min_price} -{' '}
            {evaluation.suggested_support_zone.max_price}
          </p>
          <ul className="vocabulary">
            {evaluation.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {validation ? (
        <div className="card stack-md">
          <h3>Trade validation result</h3>
          <p>
            <strong>Approved:</strong> {validation.approved ? 'Yes' : 'Not yet'}
          </p>
          <p>
            <strong>Score:</strong> {validation.score}
          </p>
          <ul className="vocabulary">
            {validation.checks.map((check) => (
              <li key={check.name}>
                <strong>{check.passed ? 'Pass' : 'Review'}:</strong> {check.message}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
