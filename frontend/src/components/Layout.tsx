import type { ReactNode } from 'react';
import type { PageView } from '../types';
import Sidebar from './Sidebar';

interface Props {
  children: ReactNode;
  activePage: PageView;
  onNavigate: (page: PageView) => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export default function Layout({
  children, activePage, onNavigate, theme, onToggleTheme
}: Props) {
  return (
    <div className="layout">
      <Sidebar
        active={activePage}
        onNavigate={onNavigate}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
