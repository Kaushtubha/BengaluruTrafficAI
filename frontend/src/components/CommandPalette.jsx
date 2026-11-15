import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';
import {
  Search, LayoutDashboard, BarChart2, Navigation,
  AlertTriangle, Check, Moon, Sun, RefreshCw, Copy,
  Keyboard, X, Zap, ArrowRight, ShieldCheck
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function CommandPalette({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const {
    theme,
    toggleTheme,
    simulateEmergency,
    fetchTrafficData,
    trafficData,
    signalData
  } = useStore();

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const actions = [
    {
      id: 'nav-dashboard',
      title: 'Go to Junction Dashboard',
      subtitle: 'View live junction radar, vehicle counters, and active signal times',
      category: 'Navigation',
      icon: LayoutDashboard,
      shortcut: 'G D',
      perform: () => { navigate('/'); onClose(); }
    },
    {
      id: 'nav-analytics',
      title: 'Go to Analytics & Violations',
      subtitle: 'Analyze red-light jumps, speeding patterns, and radar charts',
      category: 'Navigation',
      icon: BarChart2,
      shortcut: 'G A',
      perform: () => { navigate('/analytics'); onClose(); }
    },
    {
      id: 'nav-driver',
      title: 'Go to Driver Advisory Portal',
      subtitle: 'Check corridor approach guidelines, GPS distance, and delays',
      category: 'Navigation',
      icon: Navigation,
      shortcut: 'G P',
      perform: () => { navigate('/driver'); onClose(); }
    },
    {
      id: 'emergency-north',
      title: 'Simulate Emergency: North Lane',
      subtitle: 'Grant 60s max green override for approaching emergency vehicle',
      category: 'Emergency Preemption',
      icon: AlertTriangle,
      badge: 'Override',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      perform: async () => {
        await simulateEmergency('North');
        toast.success('Priority preemption granted to North Lane (60s green)');
        onClose();
      }
    },
    {
      id: 'emergency-south',
      title: 'Simulate Emergency: South Lane',
      subtitle: 'Grant 60s max green override for approaching emergency vehicle',
      category: 'Emergency Preemption',
      icon: AlertTriangle,
      badge: 'Override',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      perform: async () => {
        await simulateEmergency('South');
        toast.success('Priority preemption granted to South Lane (60s green)');
        onClose();
      }
    },
    {
      id: 'emergency-east',
      title: 'Simulate Emergency: East Lane',
      subtitle: 'Grant 60s max green override for approaching emergency vehicle',
      category: 'Emergency Preemption',
      icon: AlertTriangle,
      badge: 'Override',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      perform: async () => {
        await simulateEmergency('East');
        toast.success('Priority preemption granted to East Lane (60s green)');
        onClose();
      }
    },
    {
      id: 'emergency-west',
      title: 'Simulate Emergency: West Lane',
      subtitle: 'Grant 60s max green override for approaching emergency vehicle',
      category: 'Emergency Preemption',
      icon: AlertTriangle,
      badge: 'Override',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      perform: async () => {
        await simulateEmergency('West');
        toast.success('Priority preemption granted to West Lane (60s green)');
        onClose();
      }
    },
    {
      id: 'emergency-clear',
      title: 'Clear Emergency Overrides',
      subtitle: 'Restore normal proportional queue-based signal allocation',
      category: 'Emergency Preemption',
      icon: ShieldCheck,
      badge: 'Reset',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      perform: async () => {
        await simulateEmergency(null);
        toast.success('Emergency overrides cleared. Normal schedule restored.');
        onClose();
      }
    },
    {
      id: 'action-refresh',
      title: 'Synchronize Junction Data',
      subtitle: 'Poll latest vehicle queues and signal plans immediately',
      category: 'System',
      icon: RefreshCw,
      shortcut: 'R',
      perform: async () => {
        await fetchTrafficData();
        toast.success('Junction data synchronized');
        onClose();
      }
    },
    {
      id: 'action-theme',
      title: `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Appearance`,
      subtitle: `Currently using ${theme} color scheme`,
      category: 'System',
      icon: theme === 'dark' ? Sun : Moon,
      shortcut: 'T',
      perform: () => {
        toggleTheme();
        onClose();
      }
    },
    {
      id: 'action-copy',
      title: 'Copy Junction Telemetry Report',
      subtitle: 'Copy JSON snapshot of current counts, signals, and violations',
      category: 'System',
      icon: Copy,
      perform: () => {
        const snapshot = {
          junction: trafficData.junction,
          timestamp: new Date().toISOString(),
          active_lane: trafficData.active_lane,
          congestion_level: trafficData.congestion_level,
          vehicle_counts: trafficData.vehicle_counts,
          signal_plan: signalData,
        };
        navigator.clipboard?.writeText(JSON.stringify(snapshot, null, 2));
        toast.success('Telemetry snapshot copied to clipboard!');
        onClose();
      }
    }
  ];

  const filtered = actions.filter(action => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return (
      action.title.toLowerCase().includes(q) ||
      action.subtitle.toLowerCase().includes(q) ||
      action.category.toLowerCase().includes(q)
    );
  });

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(idx => (idx + 1) % (filtered.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(idx => (idx - 1 + (filtered.length || 1)) % (filtered.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        filtered[selectedIndex].perform();
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-md"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -8 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-xl rounded-2xl bg-white/95 dark:bg-[#0f1523]/95 backdrop-blur-2xl border border-slate-200 dark:border-white/10 shadow-2xl overflow-hidden z-10"
          >
            {/* Search Input Bar */}
            <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-200 dark:border-white/10">
              <Search size={18} className="text-amber-500 shrink-0" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSelectedIndex(0);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Type a command or search actions..."
                className="flex-1 bg-transparent text-sm font-medium text-slate-800 dark:text-slate-100 placeholder-slate-400 outline-none"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X size={14} />
                </button>
              )}
              <kbd className="hidden sm:inline-flex items-center gap-0.5 px-2 py-0.5 text-[10px] font-mono font-bold text-slate-400 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-md">
                ESC
              </kbd>
            </div>

            {/* Results List */}
            <div className="max-h-80 overflow-y-auto p-2 space-y-1">
              {filtered.length === 0 ? (
                <div className="py-10 text-center text-xs text-slate-400">
                  No actions found matching "{query}"
                </div>
              ) : (
                filtered.map((action, idx) => {
                  const Icon = action.icon;
                  const isSelected = idx === selectedIndex;
                  return (
                    <button
                      key={action.id}
                      onClick={action.perform}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-150 ${
                        isSelected
                          ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/60 dark:hover:bg-white/5 border border-transparent'
                      }`}
                    >
                      <div className={`p-2 rounded-lg shrink-0 ${
                        isSelected
                          ? 'bg-amber-500/20 text-amber-500'
                          : 'bg-slate-100 dark:bg-white/5 text-slate-400'
                      }`}>
                        <Icon size={16} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-xs font-semibold truncate leading-snug">
                            {action.title}
                          </p>
                          {action.badge && (
                            <span className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded border ${action.badgeColor}`}>
                              {action.badge}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 dark:text-slate-500 truncate mt-0.5">
                          {action.subtitle}
                        </p>
                      </div>

                      {action.shortcut ? (
                        <kbd className="hidden sm:inline-flex px-1.5 py-0.5 text-[10px] font-mono font-bold text-slate-400 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded">
                          {action.shortcut}
                        </kbd>
                      ) : (
                        <ArrowRight size={13} className={`shrink-0 opacity-0 transition-opacity ${isSelected ? 'opacity-100 text-amber-500' : ''}`} />
                      )}
                    </button>
                  );
                })
              )}
            </div>

            {/* Footer with key hints */}
            <div className="px-4 py-2.5 border-t border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-black/20 flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <kbd className="px-1 py-0.2 rounded bg-slate-200 dark:bg-white/10 text-[9px]">↑</kbd>
                  <kbd className="px-1 py-0.2 rounded bg-slate-200 dark:bg-white/10 text-[9px]">↓</kbd> navigate
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.2 rounded bg-slate-200 dark:bg-white/10 text-[9px]">↵</kbd> select
                </span>
              </div>
              <span className="text-[10px] text-slate-400">Ctrl+K or ⌘K</span>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

