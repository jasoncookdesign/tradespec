'use client';

import { useEffect, useState } from 'react';

import { createJournalEntry, getJournalEntries } from '../../lib/api';
import { JournalEntry } from '../../lib/types';

export default function JournalPage() {
  const [tradeSpecId, setTradeSpecId] = useState('trade-msft-001');
  const [exitPrice, setExitPrice] = useState('111.5');
  const [outcome, setOutcome] = useState('Closed into planned strength.');
  const [lesson, setLesson] = useState('Following the plan reduced emotional decision-making.');
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    getJournalEntries()
      .then(setEntries)
      .catch(() => {
        setError('Start the API on localhost:8000 to load journal entries.');
      });
  }, []);

  async function handleCreateEntry() {
    setError('');

    const parsedExitPrice = Number.parseFloat(exitPrice);
    if (!tradeSpecId.trim() || Number.isNaN(parsedExitPrice) || parsedExitPrice <= 0) {
      setError('Enter a trade ID and a valid positive exit price.');
      return;
    }

    try {
      const result = await createJournalEntry({
        trade_spec_id: tradeSpecId.trim(),
        exit_price: parsedExitPrice,
        outcome_summary: outcome,
        lesson_summary: lesson,
      });
      setEntries((current) => [result, ...current]);
    } catch {
      setError('Start the API on localhost:8000 to create a journal preview.');
    }
  }

  return (
    <section className="stack-lg">
      <div className="card stack-md">
        <p className="eyebrow">Tertiary module</p>
        <h2>Trade Journal</h2>
        <p>
          Record the outcome, note the lesson, and review the AI observation as
          advisory-only guidance.
        </p>

        <label className="field">
          <span>Trade spec ID</span>
          <input value={tradeSpecId} onChange={(event) => setTradeSpecId(event.target.value)} />
        </label>

        <label className="field">
          <span>Exit price</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={exitPrice}
            onChange={(event) => setExitPrice(event.target.value)}
          />
        </label>

        <label className="field">
          <span>Outcome summary</span>
          <textarea rows={3} value={outcome} onChange={(event) => setOutcome(event.target.value)} />
        </label>

        <label className="field">
          <span>Lesson summary</span>
          <textarea rows={3} value={lesson} onChange={(event) => setLesson(event.target.value)} />
        </label>

        <div className="buttonRow">
          <button type="button" onClick={handleCreateEntry}>
            Save journal entry
          </button>
        </div>

        {error ? <p className="notice">{error}</p> : null}
      </div>

      <div className="card stack-md">
        <h3>Journal history</h3>
        {entries.length === 0 ? <p>No journal entries yet.</p> : null}
        {entries.map((entry) => (
          <div className="stack-sm" key={entry.id}>
            <p>
              <strong>{entry.trade_spec_id}</strong> — {entry.outcome_summary}
            </p>
            <p>{entry.lesson_summary}</p>
            <p className="advisoryCallout">
              <strong>AI advisory:</strong> {entry.ai_observation}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
