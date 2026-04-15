import { render, screen } from '@testing-library/react';

import HomePage from './page';

describe('HomePage', () => {
  it('renders the core trade decision vocabulary', () => {
    render(<HomePage />);

    expect(screen.getByText(/Rules first\. AI second\./i)).toBeInTheDocument();
    expect(screen.getByText(/setup passes the rule engine\./i)).toBeInTheDocument();
    expect(screen.getByText(/setup is promising but incomplete\./i)).toBeInTheDocument();
    expect(screen.getByText(/setup fails hard constraints\./i)).toBeInTheDocument();
  });

  it('renders the main workflow entry points', () => {
    render(<HomePage />);

    expect(screen.getByRole('link', { name: /Pre-Trade Gate/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Active Trade Stabilizer/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Trade Journal/i })).toBeInTheDocument();
  });
});
