import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useStore } from '../store/useStore';
import {
  LayoutDashboard, Sun, Moon, Menu, X, Radar, ChevronRight,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ParticleBackground from './ParticleBackground';

const NAV = [
  { name: 'Junction Dashboard', path: '/', icon: LayoutDashboard, sub: 'Junction flow & timings' },
];

export default function Layout({ children }) {
  const { theme, toggleTheme, systemStatus } = useStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.body.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  return (
    <div className="min-h-screen flex text-slate-900 dark:text-slate-200 font-sans relative overflow-hidden bg-gradient-to-br from-[#f4f7fb] via-[#ffffff] to-[#fff5f0] dark:from-[#080b14] dark:via-[#0c111c] dark:to-[#1a0f0a] transition-colors duration-500">

      {/* ── Background system ─────────────────────────────────── */}
      <ParticleBackground />

      {/* ── Desktop Sidebar ───────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-64 fixed inset-y-0 left-0 z-30
        bg-white/60 dark:bg-dark-900/70 backdrop-blur-2xl
        border-r border-slate-200/60 dark:border-white/[0.05]
        shadow-[1px_0_0_0_rgba(0,0,0,0.04)] dark:shadow-[1px_0_0_0_rgba(255,255,255,0.03)]">

         {/* Logo */}
        <div className="flex items-center gap-3 px-5 h-[68px] border-b border-slate-200/60 dark:border-white/[0.05] shrink-0">
          <motion.div
            whileHover={{ scale: 1.08, rotate: 5 }}
            whileTap={{ scale: 0.94 }}
            className="relative w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
            style={{ background: 'linear-gradient(135deg,#ff9f1c 0%,#ff3b30 100%)', boxShadow: '0 4px 16px rgba(255,159,28,0.3)' }}
          >
            <Radar size={18} className="text-white fill-white/20" />
            <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
          </motion.div>
          <div>
            <h1 className="font-display font-bold text-base text-slate-900 dark:text-white leading-none tracking-tight">BLR TrafficAI</h1>
            <span className="text-[10px] font-semibold tracking-[0.12em] text-amber-500 uppercase block mt-0.5">Control Center</span>
          </div>
        </div>

        {/* Nav label */}
        <div className="px-5 pt-6 pb-2">
          <span className="text-[10px] font-semibold tracking-[0.15em] text-slate-400/70 dark:text-dark-600 uppercase">Control Panel</span>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 pb-4 space-y-1 overflow-y-auto">
          {NAV.map(({ name, path, icon: Icon, sub }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3.5 py-3 rounded-xl transition-all duration-200 relative group ${
                  active
                    ? 'text-amber-600 dark:text-white'
                    : 'text-slate-500 dark:text-dark-400 hover:text-slate-800 dark:hover:text-dark-100'
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="sidebar-pill"
                    className="absolute inset-0 rounded-xl nav-active-glow"
                    style={{
                      background: 'linear-gradient(135deg, rgba(249,115,22,0.08) 0%, rgba(249,115,22,0.04) 100%)',
                      border: '1px solid rgba(249,115,22,0.15)',
                    }}
                    transition={{ ease: [0.16, 1, 0.3, 1], duration: 0.5 }}
                  />
                )}
                {!active && (
                  <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200
                    bg-slate-100/60 dark:bg-dark-800/40" />
                )}

                <div className={`relative z-10 w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all duration-200 ${
                  active
                    ? 'bg-amber-500/15 dark:bg-amber-500/20 text-amber-500'
                    : 'bg-slate-100/80 dark:bg-dark-800/60 text-slate-400 dark:text-dark-500 group-hover:bg-slate-200/60 dark:group-hover:bg-dark-700/60 group-hover:text-amber-500'
                }`}>
                  <Icon size={15} />
                </div>

                <div className="relative z-10 flex-1 min-w-0">
                  <p className={`text-sm font-semibold leading-none ${active ? 'text-slate-900 dark:text-white' : ''}`}>{name}</p>
                  <p className="text-[11px] text-slate-400 dark:text-dark-600 mt-0.5 truncate">{sub}</p>
                </div>

                {active && <ChevronRight size={13} className="relative z-10 text-amber-500 shrink-0" />}
              </Link>
            );
          })}
        </nav>

        {/* Status + theme */}
        <div className="p-3 border-t border-slate-200/60 dark:border-white/[0.05] space-y-2 shrink-0">
          {/* System status */}
          <div className={`px-3.5 py-3 rounded-xl border transition-all ${
            systemStatus === 'ACTIVE'
              ? 'bg-amber-500/5 border-amber-500/15'
              : 'bg-rose-500/5 border-rose-500/15'
          }`}>
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-1.5 h-1.5 rounded-full block ${
                systemStatus === 'ACTIVE' 
                  ? 'bg-amber-400 shadow-[0_0_6px_#ff9f1c] animate-pulse' 
                  : 'bg-rose-400 shadow-[0_0_6px_#ff3b3b]'
              }`} />
              <span className={`text-[10px] font-semibold uppercase tracking-wider ${
                systemStatus === 'ACTIVE' ? 'text-amber-400' : 'text-rose-400'
              }`}>{systemStatus === 'ACTIVE' ? 'Live' : 'Offline'}</span>
            </div>
            <p className="text-xs font-medium text-slate-600 dark:text-dark-300">
              {systemStatus === 'ACTIVE' ? 'Junction controller active' : 'Backend connection failed'}
            </p>
          </div>

          {/* Theme toggle */}
          <div className="flex items-center justify-between px-3.5 py-2.5 rounded-xl
            bg-slate-100/60 dark:bg-dark-800/50 border border-slate-200/50 dark:border-dark-700/40">
            <span className="text-xs font-semibold text-slate-500 dark:text-dark-400">Appearance</span>
            <motion.button
              whileHover={{ scale: 1.08, rotate: 8 }} whileTap={{ scale: 0.92, rotate: -8 }}
              onClick={toggleTheme}
              className="p-1.5 rounded-lg bg-white dark:bg-dark-700 border border-slate-200/70 dark:border-dark-600/60
                text-amber-500 shadow-sm hover:shadow-glow-sm transition-all"
            >
              <AnimatePresence mode="wait" initial={false}>
                <motion.div key={theme}
                  initial={{ opacity: 0, rotate: -90, scale: 0.7 }}
                  animate={{ opacity: 1, rotate: 0, scale: 1 }}
                  exit={{ opacity: 0, rotate: 90, scale: 0.7 }}
                  transition={{ duration: 0.18 }}>
                  {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
                </motion.div>
              </AnimatePresence>
            </motion.button>
          </div>
        </div>

        {/* Version */}
        <div className="px-5 pb-4 pt-1">
          <p className="text-[10px] font-mono text-slate-300/50 dark:text-dark-700">v1.0.0 · BLR Control Hub</p>
        </div>
      </aside>

      {/* ── Mobile header ──────────────────────────────────────── */}
      <div className="md:hidden fixed top-0 inset-x-0 h-14 flex items-center justify-between px-4 z-40
        bg-white/80 dark:bg-dark-900/80 backdrop-blur-xl
        border-b border-slate-200/60 dark:border-white/[0.05]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg,#ff9f1c,#ff3b30)', boxShadow: '0 3px 12px rgba(255,159,28,0.3)' }}>
            <Radar size={14} className="text-white fill-white/20" />
          </div>
          <span className="font-display font-bold text-base text-slate-900 dark:text-white">BLR TrafficAI</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-500 dark:text-dark-400 hover:bg-slate-100 dark:hover:bg-dark-800 transition-colors">
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          <button onClick={() => setMobileOpen(v => !v)}
            className="p-2 rounded-lg text-slate-600 dark:text-dark-300 hover:bg-slate-100 dark:hover:bg-dark-800 transition-colors">
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* ── Mobile drawer ──────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div key="backdrop"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden" />
            <motion.nav key="drawer"
              initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="fixed top-0 bottom-0 left-0 w-72 z-50 md:hidden flex flex-col
                bg-white/95 dark:bg-dark-900/95 backdrop-blur-2xl
                border-r border-slate-200/60 dark:border-white/[0.05] shadow-2xl">

              <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200/60 dark:border-white/[0.05]">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg,#ff9f1c,#ff3b30)', boxShadow: '0 4px 14px rgba(255,159,28,0.3)' }}>
                    <Radar size={16} className="text-white fill-white/20" />
                  </div>
                  <div>
                    <p className="font-display font-bold text-slate-900 dark:text-white text-base leading-none">BLR TrafficAI</p>
                    <p className="text-[10px] text-amber-500 font-semibold tracking-wider uppercase mt-0.5">Control Center</p>
                  </div>
                </div>
                <button onClick={() => setMobileOpen(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-dark-800 transition-colors">
                  <X size={17} />
                </button>
              </div>

              <div className="flex-1 p-4 space-y-1">
                {NAV.map(({ name, path, icon: Icon }) => {
                  const active = location.pathname === path;
                  return (
                    <Link key={path} to={path}
                      className={`flex items-center gap-3.5 px-4 py-3.5 rounded-xl font-semibold text-sm transition-all duration-200 relative ${
                        active
                          ? 'text-slate-900 dark:text-white'
                          : 'text-slate-500 dark:text-dark-400 hover:text-slate-800 dark:hover:text-dark-100 hover:bg-slate-100/50 dark:hover:bg-dark-800/50'
                      }`}>
                      {active && (
                        <motion.div layoutId="mobile-pill"
                          className="absolute inset-0 rounded-xl"
                          style={{ background:'rgba(249,115,22,0.08)', border:'1px solid rgba(249,115,22,0.15)' }}
                          transition={{ type:'spring', stiffness:380, damping:32 }} />
                      )}
                      <Icon size={18} className={`relative z-10 ${active ? 'text-amber-500' : ''}`} />
                      <span className="relative z-10">{name}</span>
                    </Link>
                  );
                })}
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>

      {/* ── Main content ───────────────────────────────────────── */}
      <main className="flex-1 md:pl-64 pt-14 md:pt-0 min-h-screen flex flex-col z-10 relative">
        <div className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-7 md:py-9">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 14, scale: 0.995 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="w-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
