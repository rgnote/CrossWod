import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Home, Dumbbell, History, TrendingUp, User } from 'lucide-react';

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/workout', icon: Dumbbell, label: 'Workout' },
  { path: '/history', icon: History, label: 'History' },
  { path: '/progress', icon: TrendingUp, label: 'Progress' },
  { path: '/settings', icon: User, label: 'Profile' },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <main className="flex-1 overflow-y-auto safe-top">
        <Outlet />
      </main>

      <nav className="glass safe-bottom" style={{
        borderRadius: '24px 24px 0 0',
        borderBottom: 'none',
        padding: '12px 20px',
        paddingBottom: 'max(12px, env(safe-area-inset-bottom))',
      }}>
        <div className="flex justify-between items-center">
          {navItems.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path ||
              (path !== '/' && location.pathname.startsWith(path));

            return (
              <NavLink
                key={path}
                to={path}
                className="flex flex-col items-center gap-1"
                style={{ minWidth: '60px' }}
              >
                <div
                  className={`flex items-center justify-center transition-all duration-200 ${
                    isActive ? 'text-accent' : 'text-muted'
                  }`}
                  style={{
                    width: '44px',
                    height: '32px',
                    borderRadius: '16px',
                    background: isActive ? 'rgba(10, 132, 255, 0.15)' : 'transparent',
                  }}
                >
                  <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
                </div>
                <span
                  className={`text-xs font-medium ${
                    isActive ? 'text-accent' : 'text-muted'
                  }`}
                >
                  {label}
                </span>
              </NavLink>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
