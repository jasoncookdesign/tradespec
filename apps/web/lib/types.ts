export type EvaluationStatus = 'VALID' | 'WAIT' | 'INVALID';
export type AssetType = 'stock' | 'etf';
export type SetupType = 'breakout' | 'pullback' | 'reversal' | 'trend-continuation';

export interface PriceZone {
  min_price: number;
  max_price: number;
}

export interface TickerEvaluation {
  ticker: string;
  asset_type: AssetType;
  trend_summary: string;
  momentum_summary: string;
  structure_summary: string;
  volatility_summary: string;
  status: EvaluationStatus;
  reasons: string[];
  suggested_entry_zone: PriceZone;
  suggested_support_zone: PriceZone;
  generated_at: string;
}

export interface TradeSpecInput {
  ticker: string;
  setup_type: SetupType;
  entry_zone_min: number;
  entry_zone_max: number;
  stop_loss: number;
  target_price: number;
  time_horizon_days: number;
  thesis: string;
}

export interface TradeValidationCheck {
  name: string;
  passed: boolean;
  message: string;
}

export interface TradeValidationResult {
  approved: boolean;
  score: number;
  status: EvaluationStatus;
  checks: TradeValidationCheck[];
  reasons: string[];
  warnings: string[];
}

export type GuidanceStatus = 'ON_PLAN' | 'CAUTION' | 'REVIEW_EXIT';

export interface ActiveTrade {
  id: string;
  trade_spec_id: string;
  entry_price_actual: number;
  entered_at: string;
  current_price: number;
  pnl_percent: number;
  distance_to_stop_percent: number;
  distance_to_target_percent: number;
  expected_drawdown_min_percent: number;
  expected_drawdown_max_percent: number;
  expected_time_to_move_min_days: number;
  expected_time_to_move_max_days: number;
  guidance_status: GuidanceStatus;
  guidance_message: string;
}

export interface JournalEntryCreate {
  trade_spec_id: string;
  exit_price: number;
  outcome_summary: string;
  lesson_summary: string;
}

export interface JournalEntry extends JournalEntryCreate {
  id: string;
  exited_at: string;
  ai_observation: string;
  created_at: string;
}
