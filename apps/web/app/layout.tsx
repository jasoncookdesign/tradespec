import Link from 'next/link';
import './globals.css';

export const metadata = {
  title: 'TradeSpec',
  description: 'Personal swing-trading advisor for disciplined decision-making.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="header">
            <div>
              <p className="eyebrow">TradeSpec</p>
              <h1 className="brand">Personal Swing-Trade Advisor</h1>
            </div>
            <nav className="nav">
              <Link href="/">Home</Link>
              <Link href="/pre-trade">Pre-Trade</Link>
              <Link href="/active-trade">Active Trade</Link>
              <Link href="/journal">Journal</Link>
            </nav>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
