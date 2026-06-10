import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import {
  Clock, TrendingUp, Sparkles, Layers, Activity,
  ArrowUpRight, AlertCircle, RefreshCw, Milestone,
  Navigation, CarFront
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  CartesianGrid
} from 'recharts';
import { motion, useSpring } from 'framer-motion';
import toast from 'react-hot-toast';

/* ─── Animated number ───────────────────── */
function AnimatedCounter({ value, prefix = '', suffix = '' }) {
  const spring = useSpring(0, { bounce: 0, duration: 1400 });
  const [display, setDisplay] = useState(0);
  
  useEffect(() => {
    spring.set(value);
  }, [value, spring]);

  useEffect(() => {
    return spring.onChange(v => setDisplay(Math.floor(v)));
  }, [spring]);

  return <span>{prefix}{display.toLocaleString('en-US')}{suffix}</span>;
}

/* ─── Custom Tooltip ────────────────────── */
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card px-4 py-3 rounded-xl text-xs shadow-glass-dark border border-white/10">
      <p className="text-slate-400 mb-1 font-medium">{label}</p>
      <p className="font-bold text-emerald-400 text-sm">
        {payload[0].value} vehicles
      </p>
    </div>
  );
}

/* ─── Motion variants ───────────────────── */
const stagger = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const rise    = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { ease: [0.16, 1, 0.3, 1], duration: 0.6 } } };

/* ─────────────────────────────────────────── */
export default function Dashboard() {
  const { trafficData, signalData, history, systemStatus, fetchTrafficData } = useStore();
  const [refreshing, setRefreshing] = useState(false);
  const [time, setTime] = useState(new Date());

  // Digital Clock ticking
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll traffic API every 3 seconds
  useEffect(() => {
    const interval = setInterval(fetchTrafficData, 3000);
    fetchTrafficData(); // Initial load
    return () => clearInterval(interval);
  }, []);

  const getGreeting = () => {
    const hour = time.getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchTrafficData();
    setRefreshing(false);
    toast.success('Junction data synchronized');
  };

  // Safe variables mapping
  const vehicleCounts = trafficData.vehicle_counts || { North: 0, South: 0, East: 0, West: 0 };
  const greenTimes = signalData.green_times || { North: 0, South: 0, East: 0, West: 0 };
  const maxCount = Math.max(...Object.values(vehicleCounts)) || 1;

  // Chart data from Zustand history stream
  const chartData = history.map(h => ({
    time: h.time,
    vehicles: h.vehicles,
  }));

  return (
    <div className="space-y-7 pb-12">
      {/* ── Header ────────────────────────────────────── */}
      <motion.div 
        initial={{ opacity: 0, y: -12 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row sm:items-start justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-emerald-500">
              <Sparkles size={13} className="animate-pulse" />
            </span>
            <span className="text-[11px] font-bold tracking-[0.15em] text-emerald-400 uppercase text-glow">
              Junction Operations
            </span>
            <span className="w-1 h-1 rounded-full bg-slate-700 mx-1"></span>
            <span className="text-[11px] font-mono font-medium text-slate-400">
              {time.toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
          <h2 className="text-gradient-hero font-display font-extrabold text-3xl sm:text-4xl tracking-tight leading-none">
            {getGreeting()}, Operator.
          </h2>
          <p className="text-slate-400 text-sm mt-2 font-sans max-w-lg">
            Monitor real-time vehicle flow, adaptive signal configurations, and red light jumping violations at Silk Board, Bengaluru.
          </p>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div className="relative group">
            <motion.button 
              whileHover={{ scale: 1.05 }} 
              whileTap={{ scale: 0.95 }}
              onClick={handleRefresh}
              className="btn-ghost p-2.5 !px-2.5"
            >
              <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
            </motion.button>
            <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 px-2 py-1 bg-slate-800 text-white text-[10px] font-bold uppercase tracking-wider rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-xl z-50">
              Sync Data
            </div>
          </div>
          
          <div className={`status-badge border transition-all ${
            systemStatus === 'ACTIVE' 
              ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400' 
              : 'bg-rose-500/5 border-rose-500/20 text-rose-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              systemStatus === 'ACTIVE' 
                ? 'bg-emerald-400 shadow-[0_0_10px_#00ff88] animate-pulse' 
                : 'bg-rose-400 shadow-[0_0_10px_#ff3b3b]'
            }`} />
            <span className="font-mono text-xs font-semibold tracking-wider">{systemStatus}</span>
          </div>
        </div>
      </motion.div>

      {/* ── Stats cards ───────────────────────────────── */}
      <motion.div 
        variants={stagger} 
        initial="hidden" 
        animate="show"
        className="grid grid-cols-2 lg:grid-cols-5 gap-4"
      >
        {[
          {
            label: 'Total Vehicles', icon: CarFront,
            value: trafficData.total_vehicles || 0,
            sub: 'Active count now',
            accent: 'from-emerald-500/5 to-transparent',
            iconColor: 'text-emerald-400',
            iconBg: 'bg-emerald-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(0,255,136,0.15)] hover:border-emerald-500/30',
          },
          {
            label: 'Active Lane', icon: Navigation,
            value: trafficData.active_lane || '--',
            isText: true,
            sub: 'Highest traffic volume',
            accent: 'from-sky-500/5 to-transparent',
            iconColor: 'text-sky-400',
            iconBg: 'bg-sky-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(0,191,255,0.15)] hover:border-sky-500/30',
          },
          {
            label: 'North Lane', icon: Milestone,
            value: vehicleCounts.North,
            sub: 'Vehicles inflow',
            accent: 'from-indigo-500/5 to-transparent',
            iconColor: 'text-indigo-400',
            iconBg: 'bg-indigo-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(99,102,241,0.15)] hover:border-indigo-500/30',
          },
          {
            label: 'South Lane', icon: Milestone,
            value: vehicleCounts.South,
            sub: 'Vehicles inflow',
            accent: 'from-violet-500/5 to-transparent',
            iconColor: 'text-violet-400',
            iconBg: 'bg-violet-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(139,92,246,0.15)] hover:border-violet-500/30',
          },
          {
            label: 'Violations', icon: AlertCircle,
            value: trafficData.violations || 0,
            sub: 'Red Light Jumps',
            accent: 'from-rose-500/5 to-transparent',
            iconColor: 'text-rose-400',
            iconBg: 'bg-rose-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(255,59,59,0.15)] hover:border-rose-500/30',
            textColor: 'text-rose-400 text-glow-red',
          },
        ].map(({ label, icon: Icon, value, isText, sub, accent, iconColor, iconBg, glow, textColor = 'text-white' }) => (
          <motion.div 
            key={label} 
            variants={rise}
            whileHover={{ y: -6, scale: 1.02, transition: { duration: 0.3, type: 'spring', stiffness: 300, damping: 20 } }}
            className={`glass-panel rounded-2xl p-5 relative overflow-hidden group cursor-default transition-all duration-300 z-10 ${glow}`}
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${accent} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 leading-none">
                  {label}
                </span>
                <div className={`w-8 h-8 rounded-lg ${iconBg} flex items-center justify-center`}>
                  <Icon size={15} className={iconColor} />
                </div>
              </div>
              <div className={`font-mono font-bold text-3xl tracking-tight leading-none ${textColor}`}>
                {isText ? (
                  <span>{value}</span>
                ) : (
                  <AnimatedCounter value={value} />
                )}
              </div>
              <div className="mt-3 text-[11px] font-medium text-slate-400 flex items-center gap-1">
                <ArrowUpRight size={11} className={iconColor} />
                {sub}
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* ── Adaptive Timings Section ───────────────────── */}
      <motion.div 
        variants={rise}
        className="glass-panel rounded-2xl p-6 border border-white/[0.05]"
      >
        <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm mb-5 uppercase tracking-widest text-glow">
          ⏱️ Adaptive Signal Timings (seconds)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { dir: '🔼 North Lane', key: 'North' },
            { dir: '🔽 South Lane', key: 'South' },
            { dir: '▶️ East Lane', key: 'East' },
            { dir: '◀️ West Lane', key: 'West' },
          ].map(({ dir, key }) => (
            <div 
              key={key} 
              className="bg-white/[0.015] border border-white/[0.03] rounded-xl p-4 text-center hover:bg-white/[0.03] transition-colors"
            >
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">{dir}</div>
              <div className="font-mono font-bold text-2xl text-sky-400 text-glow-blue">
                {greenTimes[key] !== undefined ? `${greenTimes[key]}s` : '--'}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-5 pt-4 border-t border-white/[0.03] flex justify-between items-center text-xs text-slate-400">
          <span>Adaptive Signal Plan Optimization Loop</span>
          <span>Total Cycle Time: <span className="font-mono font-bold text-emerald-400" id="cycle-time">{signalData.cycle_time}s</span></span>
        </div>
      </motion.div>

      {/* ── 2-Column Metrics Grid ────────────────────────── */}
      <motion.div 
        variants={stagger} 
        initial="hidden" 
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Lane Distribution Bars */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05]"
        >
          <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm mb-5 uppercase tracking-widest">
            📊 Lane Traffic Distribution
          </h3>
          <div className="space-y-4">
            {[
              { label: '🔼 North Lane', key: 'North' },
              { label: '🔽 South Lane', key: 'South' },
              { label: '▶️ East Lane', key: 'East' },
              { label: '◀️ West Lane', key: 'West' },
            ].map(({ label, key }) => {
              const count = vehicleCounts[key] || 0;
              const percent = maxCount > 0 ? (count / maxCount) * 100 : 0;
              return (
                <div key={key} className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold text-slate-400">
                    <span>{label}</span>
                    <span className="font-mono text-emerald-400">{count}</span>
                  </div>
                  <div className="h-2.5 bg-white/[0.02] border border-white/[0.03] rounded-full overflow-hidden relative">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percent}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-sky-500 to-emerald-400 rounded-full shadow-[0_0_10px_rgba(0,255,136,0.15)] relative overflow-hidden"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shine" style={{ backgroundSize: '200% 100%' }} />
                    </motion.div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="text-[11px] text-slate-500 text-right mt-5">
            Last Sync: {time.toLocaleTimeString('en-US', { hour12: false })}
          </div>
        </motion.div>

        {/* Junction Monitor Grid */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05]"
        >
          <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm mb-5 uppercase tracking-widest">
            🚦 4-Way Junction Signal Status
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'NORTH STATUS', key: 'North', arrow: '🔼' },
              { label: 'SOUTH STATUS', key: 'South', arrow: '🔽' },
              { label: 'EAST STATUS', key: 'East', arrow: '▶️' },
              { label: 'WEST STATUS', key: 'West', arrow: '◀️' },
            ].map(({ label, key, arrow }) => {
              const active = key === trafficData.active_lane;
              return (
                <div 
                  key={key}
                  className={`border-2 rounded-2xl p-4 flex flex-col items-center justify-center transition-all duration-300 ${
                    active 
                      ? 'border-emerald-500/40 bg-emerald-500/[0.02] shadow-[0_0_20px_rgba(0,255,136,0.04)]' 
                      : 'border-white/[0.03] bg-white/[0.005]'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all ${
                    active 
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(0,255,136,0.2)]' 
                      : 'bg-rose-500/5 border-rose-500/15 text-rose-400 shadow-[0_0_10px_rgba(255,59,59,0.05)]'
                  }`}>
                    {arrow}
                  </div>
                  <div className={`font-mono font-bold text-xl mt-3 ${active ? 'text-emerald-400 text-glow' : 'text-slate-200'}`}>
                    {vehicleCounts[key] || 0}
                  </div>
                  <div className="text-[9px] font-bold text-slate-400 tracking-wider mt-2">{label}</div>
                </div>
              );
            })}
          </div>
        </motion.div>
      </motion.div>

      {/* ── Line Chart History ─────────────────────────── */}
      <motion.div 
        variants={rise}
        whileHover={{ y: -4, transition: { duration: 0.3 } }}
        className="glass-panel rounded-2xl p-6 border border-white/[0.05] h-[260px] flex flex-col group hover:shadow-[0_24px_50px_-12px_rgba(0,255,136,0.08)] hover:border-emerald-500/30 transition-all duration-300"
      >
        <div className="flex items-center justify-between mb-4 shrink-0">
          <div>
            <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm uppercase tracking-widest">
              <TrendingUp size={15} className="text-emerald-500" /> Vehicle Count Stream History
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">Live tracking data history of total junction density</p>
          </div>
          <span className="text-[9px] font-mono font-semibold text-slate-500 uppercase tracking-widest">Active Stream</span>
        </div>
        
        <div className="flex-1 min-h-0">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 4, left: -28, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff88" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'Space Mono' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'Space Mono' }} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'rgba(0, 255, 136, 0.2)', strokeWidth: 1.5, strokeDasharray: '5 3' }} />
                <Area 
                  type="monotone" 
                  dataKey="vehicles" 
                  stroke="#00ff88" 
                  strokeWidth={2}
                  fill="url(#areaGrad)"
                  activeDot={{ r: 4, fill: '#00ff88', stroke: '#fff', strokeWidth: 1.5 }} 
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex flex-col items-center justify-center gap-2 text-slate-500">
              <Activity size={24} className="opacity-40 animate-pulse" />
              <p className="text-xs font-semibold">Waiting for backend data stream...</p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
