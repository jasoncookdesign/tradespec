'use client';

import { useState } from 'react';

import { createJournalEntry } from '../../lib/api';
import { JournalEntry } from '../../lib/types';

export default function JournalPage() {
  const [outcome, setOutcome] = useState('Closed into planned strength.');
  const [lesson, setLesson] = useState('Following the plan reduced emotional decision-making.');
  const [entry, setEntry] = useState<JournalEntry | null>(null);
  const [error, setError] = useState('');

  async function handleCreateEntry() {
    setError('');

    try {
      const result = await createJournalEntry({
        trade_spec_id: 'trade-msft-001',
        exit_price: 111.5,
        outcome_summary: outcome,
        lesson_summary: lesson,
      });
      setEntry(result);
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
          This screen posts a journal draft through the new typed API contract and shows
          the advisory observation.
        </p>

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
            Save journal preview
          </button>
        </div>

        {error ? <p className="notice">{error}</p> : null}
      </div>

      {entry ? (
        <div className="card stack-md">
          <h3>Journal result</h3>
          <p>{entry.outcome_summary}</p>
          <p>
            <strong>AI observation:</strong> {entry.ai_observation}
          </p>
        </div>
      ) : null}
    </section>
  );
}
