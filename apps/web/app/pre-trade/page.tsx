'use client';

import { useState } from 'react';

import { evaluateTicker, validateTrade } from '../../lib/api';
import { TickerEvaluation, TradeValidationResult } from '../../lib/types';

export default function PreTradePage() {
  const [ticker, setTicker] = useState('MSFT');
  const [evaluation, setEvaluation] = useState<TickerEvaluation | null>(null);
  const [validation, setValidation] = useState<TradeValidationResult | null>(null);
  const [error, setError] = useState('');
  const [tradeForm, setTradeForm] = useState({
    setup_type: 'trend_pullback',
    entry_zone_min: '100',
    entry_zone_max: '102',
    stop_loss: '95',
    target_price: '114',
    time_horizon_days: '10',
    thesis: 'Trend pullback into support with defined risk.',
  });

  async function handleEvaluateTicker() {
    setError('');

    try {
      const result = await evaluateTicker(ticker);
      setEvaluation(result);
      setTradeForm((current) => ({
        ...current,
        entry_zone_min: String(result.suggested_entry_zone.min_price),
        entry_zone_max: String(result.suggested_entry_zone.max_price),
      }));
    } catch {
      setError('Start the API on localhost:8000 to load the evaluation preview.');
    }
  }

  async function handleValidateTrade() {
    setError('');

    try {
      const result = await validateTrade({
        ticker: ticker.trim().toUpperCase() || 'MSFT',
        setup_type: tradeForm.setup_type as 'trend_pullback',
        entry_zone_min: Number(tradeForm.entry_zone_min),
        entry_zone_max: Number(tradeForm.entry_zone_max),
        stop_loss: Number(tradeForm.stop_loss),
        target_price: Number(tradeForm.target_price),
        time_horizon_days: Number(tradeForm.time_horizon_days),
        thesis: tradeForm.thesis,
        ticker_status: evaluation?.status ?? 'WAIT',
      });
      setValidation(result);
    } catch {
      setError('Trade validation preview is unavailable until the API is running.');
    }
  }

  const builderDisabled = evaluation?.status === 'INVALID';

  return (
    <section className="stack-lg">
      <div className="card stack-md">
        <p className="eyebrow">Primary module</p>
        <h2>Pre-Trade Evaluation</h2>
        <p>
          Evaluate the ticker first, then build a plan with entry zone, stop, target, and
          time horizon.
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

      <div className="card stack-md">
        <h3>Trade Builder</h3>
        <p>
          {evaluation?.status === 'INVALID'
            ? 'Ticker is INVALID, so trade entry is blocked.'
            : evaluation?.status === 'WAIT'
              ? 'Ticker is WAIT, so you can plan the trade but should not enter yet.'
              : 'Ticker is VALID, so the plan can be evaluated normally.'}
        </p>

        <div className="grid twoColGrid">
          <label className="field">
            <span>Setup type</span>
            <select
              value={tradeForm.setup_type}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, setup_type: event.target.value }))
              }
            >
              <option value="trend_pullback">trend_pullback</option>
            </select>
          </label>
          <label className="field">
            <span>Time horizon days</span>
            <input
              value={tradeForm.time_horizon_days}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, time_horizon_days: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Entry zone min</span>
            <input
              value={tradeForm.entry_zone_min}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, entry_zone_min: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Entry zone max</span>
            <input
              value={tradeForm.entry_zone_max}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, entry_zone_max: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Stop loss</span>
            <input
              value={tradeForm.stop_loss}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, stop_loss: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Target price</span>
            <input
              value={tradeForm.target_price}
              onChange={(event) =>
                setTradeForm((current) => ({ ...current, target_price: event.target.value }))
              }
            />
          </label>
        </div>

        <label className="field">
          <span>Thesis</span>
          <textarea
            rows={3}
            value={tradeForm.thesis}
            onChange={(event) =>
              setTradeForm((current) => ({ ...current, thesis: event.target.value }))
            }
          />
        </label>

        <div className="buttonRow">
          <button type="button" onClick={handleValidateTrade} disabled={builderDisabled}>
            Validate trade plan
          </button>
        </div>
      </div>

      {validation ? (
        <div className="card stack-md">
          <h3>Trade validation result</h3>
          <p>
            <strong>Approved:</strong> {validation.approved ? 'Yes' : 'Not yet'}
          </p>
          <p>
            <strong>Score:</strong> {validation.score}
          </p>
          <p>
            <strong>Status:</strong>{' '}
            <span className={`statusBadge status-${validation.status}`}>{validation.status}</span>
          </p>
          <ul className="vocabulary">
            {validation.checks.map((check) => (
              <li key={check.name}>
                <strong>{check.passed ? 'Pass' : 'Review'}:</strong> {check.message}
              </li>
            ))}
          </ul>
          {validation.reasons.length > 0 ? (
            <div>
              <strong>Reasons</strong>
              <ul className="vocabulary">
                {validation.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {validation.warnings.length > 0 ? (
            <div>
              <strong>Warnings</strong>
              <ul className="vocabulary">
                {validation.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
