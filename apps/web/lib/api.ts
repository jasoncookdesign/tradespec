import {
  ActiveTrade,
  JournalEntry,
  JournalEntryCreate,
  PositionSizingRequest,
  PositionSizingResult,
  TickerEvaluation,
  TradeSpecInput,
  TradeValidationResult,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function evaluateTicker(ticker: string): Promise<TickerEvaluation> {
  return apiRequest<TickerEvaluation>('/evaluate-ticker', {
    method: 'POST',
    body: JSON.stringify({ ticker }),
  });
}

export function validateTrade(payload: TradeSpecInput): Promise<TradeValidationResult> {
  return apiRequest<TradeValidationResult>('/validate-trade', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function calculatePositionSize(
  payload: PositionSizingRequest,
): Promise<PositionSizingResult> {
  return apiRequest<PositionSizingResult>('/position-size', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getActiveTrades(): Promise<ActiveTrade[]> {
  return apiRequest<ActiveTrade[]>('/active-trades');
}

export function getJournalEntries(): Promise<JournalEntry[]> {
  return apiRequest<JournalEntry[]>('/journal-entries');
}

export function createJournalEntry(payload: JournalEntryCreate): Promise<JournalEntry> {
  return apiRequest<JournalEntry>('/journal-entry', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
