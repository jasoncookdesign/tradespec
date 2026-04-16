'use client';

import { useState } from 'react';

import { calculatePositionSize, evaluateTicker, validateTrade } from '../../lib/api';
import { PositionSizingResult, TickerEvaluation, TradeValidationResult } from '../../lib/types';

export default function PreTradePage() {
  const [ticker, setTicker] = useState('MSFT');
  const [evaluation, setEvaluation] = useState<TickerEvaluation | null>(null);
  const [validation, setValidation] = useState<TradeValidationResult | null>(null);
  const [positionSizing, setPositionSizing] = useState<PositionSizingResult | null>(null);
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
  const [sizingForm, setSizingForm] = useState({
    account_size_dollars: '10000',
    risk_percent_per_trade: '1.0',
    intended_entry_price: '101',
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
    setPositionSizing(null);

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

  async function handleCalculatePositionSize() {
    setError('');

    const accountSize = Number(sizingForm.account_size_dollars);
    const riskPercent = Number(sizingForm.risk_percent_per_trade);
    const intendedEntryPrice = Number(sizingForm.intended_entry_price);

    if (
      Number.isNaN(accountSize) ||
      Number.isNaN(riskPercent) ||
      Number.isNaN(intendedEntryPrice) ||
      accountSize <= 0 ||
      riskPercent <= 0 ||
      intendedEntryPrice <= 0
    ) {
      setError('Enter a valid account size, risk percent, and intended entry price.');
      return;
    }

    try {
      const result = await calculatePositionSize({
        trade: {
          ticker: ticker.trim().toUpperCase() || 'MSFT',
          setup_type: tradeForm.setup_type as 'trend_pullback',
          entry_zone_min: Number(tradeForm.entry_zone_min),
          entry_zone_max: Number(tradeForm.entry_zone_max),
          stop_loss: Number(tradeForm.stop_loss),
          target_price: Number(tradeForm.target_price),
          time_horizon_days: Number(tradeForm.time_horizon_days),
          thesis: tradeForm.thesis,
          ticker_status: evaluation?.status ?? 'WAIT',
        },
        account_size_dollars: accountSize,
        risk_percent_per_trade: riskPercent,
        intended_entry_price: intendedEntryPrice,
      });
      setPositionSizing(result);
    } catch {
      setError('Position sizing is unavailable until the API is running.');
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

          {evaluation.status === 'WAIT' && evaluation.wait_plan ? (
            <div>
              <strong>Wait plan</strong>
              <ul className="vocabulary">
                <li>
                  Preferred entry zone: {evaluation.wait_plan.preferred_entry_zone.min_price} -{' '}
                  {evaluation.wait_plan.preferred_entry_zone.max_price}
                </li>
                <li>
                  Valid only when: {evaluation.wait_plan.becomes_valid_when}
                </li>
                <li>Re-check trigger: {evaluation.wait_plan.recheck_trigger}</li>
                <li>
                  Do not chase above: {evaluation.wait_plan.do_not_chase_above}
                </li>
                {evaluation.wait_plan.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          ) : null}
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

      <div className="card stack-md">
        <h3>Position sizing</h3>
        <p>
          Size the trade using account risk, an explicit intended entry price, and stop
          loss. Only approved trades can proceed to sizing.
        </p>
        <div className="grid twoColGrid">
          <label className="field">
            <span>Account size dollars</span>
            <input
              type="number"
              min="0"
              step="100"
              value={sizingForm.account_size_dollars}
              onChange={(event) =>
                setSizingForm((current) => ({
                  ...current,
                  account_size_dollars: event.target.value,
                }))
              }
            />
          </label>
          <label className="field">
            <span>Risk percent per trade</span>
            <input
              type="number"
              min="0"
              step="0.25"
              value={sizingForm.risk_percent_per_trade}
              onChange={(event) =>
                setSizingForm((current) => ({
                  ...current,
                  risk_percent_per_trade: event.target.value,
                }))
              }
            />
          </label>
          <label className="field">
            <span>Intended entry price</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={sizingForm.intended_entry_price}
              onChange={(event) =>
                setSizingForm((current) => ({
                  ...current,
                  intended_entry_price: event.target.value,
                }))
              }
            />
          </label>
        </div>
        <div className="buttonRow">
          <button
            type="button"
            onClick={handleCalculatePositionSize}
            disabled={!validation?.approved}
          >
            Calculate position size
          </button>
        </div>
      </div>

      {positionSizing ? (
        <div className="card stack-md">
          <h3>Position sizing result</h3>
          <p>
            <strong>Sizing status:</strong> {positionSizing.status}
          </p>
          <p>
            <strong>Ready to size:</strong>{' '}
            {positionSizing.approved_for_sizing ? 'Yes' : 'Not yet'}
          </p>
          <div className="grid twoColGrid">
            <p>
              <strong>Risk dollars:</strong> ${positionSizing.risk_dollars}
            </p>
            <p>
              <strong>Risk per share:</strong> ${positionSizing.risk_per_share}
            </p>
            <p>
              <strong>Suggested shares:</strong> {positionSizing.suggested_shares}
            </p>
            <p>
              <strong>Capital required:</strong> ${positionSizing.capital_required}
            </p>
            <p>
              <strong>Capital utilization:</strong> {positionSizing.capital_utilization_percent}%
            </p>
            <p>
              <strong>Entry used:</strong> ${positionSizing.entry_price_used}
            </p>
          </div>
          {positionSizing.notes.length > 0 ? (
            <div>
              <strong>Notes</strong>
              <ul className="vocabulary">
                {positionSizing.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {positionSizing.warnings.length > 0 ? (
            <div>
              <strong>Warnings</strong>
              <ul className="vocabulary">
                {positionSizing.warnings.map((warning) => (
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
