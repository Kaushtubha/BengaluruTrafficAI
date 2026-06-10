import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import {
  Clock, TrendingUp, Sparkles, Layers, Activity,
  ArrowUpRight, AlertCircle, RefreshCw, Milestone,
  Navigation, CarFront, ShieldAlert, Cpu, Zap, MapPin
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
      <p className="font-bold text-amber-400 text-sm">
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
  const { 
    trafficData, 
    signalData, 
    violationsData, 
    history, 
    systemStatus, 
    fetchTrafficData, 
    simulateEmergency 
  } = useStore();

  const [refreshing, setRefreshing] = useState(false);
  const [time, setTime] = useState(new Date());
  const [activeOverride, setActiveOverride] = useState(null);

  // Dynamic violation logs state
  const [violationLogs, setViolationLogs] = useState([
    { id: 1, msg: "Speeding detected: Vehicle #142 | North Lane | 78 km/h", time: "02:50:11", type: "speed" },
    { id: 2, msg: "Helmet violation: Motorcycle #91 | South Lane", time: "02:49:58", type: "helmet" },
    { id: 3, msg: "Wrong-side driving: Car #204 | West Lane", time: "02:49:34", type: "wrong" },
    { id: 4, msg: "Red light jump: Bus #112 | East Lane", time: "02:48:50", type: "red" }
  ]);

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

  // Sync state violations with scrolling terminal log
  useEffect(() => {
    if (trafficData.violations > 0) {
      const types = [
        { type: "speed", msg: () => `Speeding detected: Vehicle #` + Math.floor(Math.random() * 200 + 100) + ` | ` + ["North", "South", "East", "West"][Math.floor(Math.random()*4)] + ` Lane | ` + Math.floor(Math.random()*30 + 70) + ` km/h` },
        { type: "helmet", msg: () => `Helmet violation: Motorcycle #` + Math.floor(Math.random() * 200 + 100) + ` | ` + ["North", "South", "East", "West"][Math.floor(Math.random()*4)] + ` Lane` },
        { type: "wrong", msg: () => `Wrong-side driving: Car #` + Math.floor(Math.random() * 200 + 100) + ` | ` + ["North", "South", "East", "West"][Math.floor(Math.random()*4)] + ` Lane` },
        { type: "red", msg: () => `Red light jump: Vehicle #` + Math.floor(Math.random() * 200 + 100) + ` | ` + ["North", "South", "East", "West"][Math.floor(Math.random()*4)] + ` Lane` }
      ];
      const selected = types[Math.floor(Math.random() * types.length)];
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
      
      setViolationLogs(prev => {
        if (prev.length > 0 && prev[0].msg.split('|')[0] === selected.msg().split('|')[0] && Math.random() > 0.3) {
          return prev;
        }
        return [
          { id: Date.now(), msg: selected.msg(), time: timeStr, type: selected.type },
          ...prev.slice(0, 9)
        ];
      });
    }
  }, [trafficData.violations]);

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

  const handleTriggerEmergency = async (lane) => {
    setActiveOverride(lane);
    await simulateEmergency(lane);
    toast.success(`Priority override requested: ${lane} Lane`);
  };

  const handleClearOverride = async () => {
    setActiveOverride(null);
    await simulateEmergency(null);
    toast.success('Simulated priorities cleared');
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

  const totalViolations = violationsData.total_violations || trafficData.violations || 0;

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
            <span className="text-amber-500">
              <Sparkles size={13} className="animate-pulse" />
            </span>
            <span className="text-[11px] font-bold tracking-[0.15em] text-amber-400 uppercase text-glow">
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
              ? 'bg-amber-500/5 border-amber-500/20 text-amber-400' 
              : 'bg-rose-500/5 border-rose-500/20 text-rose-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              systemStatus === 'ACTIVE' 
                ? 'bg-amber-400 shadow-[0_0_10px_#ff9f1c] animate-pulse' 
                : 'bg-rose-400 shadow-[0_0_10px_#ff3b3b]'
            }`} />
            <span className="font-mono text-xs font-semibold tracking-wider">{systemStatus}</span>
          </div>
        </div>
      </motion.div>

      {/* ── KPI Strip — Congestion + Junction info ──── */}
      <motion.div
        variants={rise}
        className="glass-panel rounded-2xl px-6 py-4 border border-white/[0.05] flex flex-wrap gap-4 items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <MapPin size={14} className="text-amber-400 shrink-0" />
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Active Junction</p>
            <p className="text-sm font-semibold text-slate-200 font-mono">Silk Board, Bengaluru</p>
          </div>
        </div>
        <div className="h-8 w-px bg-white/[0.05] hidden sm:block" />
        <div className="flex items-center gap-3">
          <Zap size={14} className={`shrink-0 ${ trafficData.congestion_level === 'High' ? 'text-red-400' : trafficData.congestion_level === 'Medium' ? 'text-amber-400' : 'text-emerald-400' }`} />
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">RF Congestion Model</p>
            <p className={`text-sm font-bold font-mono ${ trafficData.congestion_level === 'High' ? 'text-red-400' : trafficData.congestion_level === 'Medium' ? 'text-amber-400' : 'text-emerald-400' }`}>
              {trafficData.congestion_level || 'Loading...'}
            </p>
          </div>
        </div>
        <div className="h-8 w-px bg-white/[0.05] hidden sm:block" />
        <div className="flex items-center gap-3">
          <Activity size={14} className="text-sky-400 shrink-0" />
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Tracked All-Time</p>
            <p className="text-sm font-bold font-mono text-sky-400">{trafficData.tracked_vehicles?.toLocaleString() || '0'} vehicles</p>
          </div>
        </div>
        <div className="h-8 w-px bg-white/[0.05] hidden sm:block" />
        <div className="flex items-center gap-3">
          <Clock size={14} className="text-violet-400 shrink-0" />
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Cycle Time</p>
            <p className="text-sm font-bold font-mono text-violet-400">{signalData.cycle_time || 0}s</p>
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
            accent: 'from-amber-500/5 to-transparent',
            iconColor: 'text-amber-400',
            iconBg: 'bg-amber-500/10',
            glow: 'hover:shadow-[0_24px_50px_-12px_rgba(249,115,22,0.15)] hover:border-amber-500/30',
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
            value: totalViolations,
            sub: 'Cumulated alerts',
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
          <span>Total Cycle Time: <span className="font-mono font-bold text-amber-400" id="cycle-time">{signalData.cycle_time}s</span></span>
        </div>
      </motion.div>

      {/* ── 3-Column Operations Grid ────────────────────── */}
      <motion.div 
        variants={stagger} 
        initial="hidden" 
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Column 1: Info Metrics (Lanes & Signals) */}
        <div className="space-y-6">
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
                      <span className="font-mono text-amber-400">{count}</span>
                    </div>
                    <div className="h-2.5 bg-white/[0.02] border border-white/[0.03] rounded-full overflow-hidden relative">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percent}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className="h-full bg-gradient-to-r from-amber-500 to-orange-400 rounded-full shadow-[0_0_10px_rgba(249,115,22,0.15)] relative overflow-hidden"
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
            <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm mb-4 uppercase tracking-widest">
              🚦 Signal Lane Status
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'NORTH', key: 'North', arrow: '🔼' },
                { label: 'SOUTH', key: 'South', arrow: '🔽' },
                { label: 'EAST', key: 'East', arrow: '▶️' },
                { label: 'WEST', key: 'West', arrow: '◀️' },
              ].map(({ label, key, arrow }) => {
                const active = key === trafficData.active_lane;
                return (
                  <div 
                    key={key}
                    className={`border rounded-xl p-3 flex flex-col items-center justify-center transition-all duration-300 ${
                      active 
                        ? 'border-amber-500/40 bg-amber-500/[0.02] shadow-[0_0_20px_rgba(249,115,22,0.04)]' 
                        : 'border-white/[0.03] bg-white/[0.005]'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all ${
                      active 
                        ? 'bg-amber-500/10 border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(249,115,22,0.2)]' 
                        : 'bg-rose-500/5 border-rose-500/15 text-rose-400 shadow-[0_0_10px_rgba(255,59,59,0.05)]'
                    }`}>
                      {arrow}
                    </div>
                    <div className={`font-mono font-bold text-lg mt-2 ${active ? 'text-amber-400 text-glow' : 'text-slate-200'}`}>
                      {vehicleCounts[key] || 0}
                    </div>
                    <div className="text-[8px] font-bold text-slate-400 tracking-wider mt-1">{label}</div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* Column 2: Interactive Junction Visualizer (Dynamic SVG Map) */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05] flex flex-col items-center justify-between"
        >
          <div className="w-full mb-3 flex items-center justify-between">
            <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest">
              🗺️ Junction Radar Visualizer
            </h3>
            <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full uppercase tracking-wider">
              Live Simulation
            </span>
          </div>

          <div className="relative w-full h-full min-h-[260px] bg-slate-950/80 rounded-xl overflow-hidden border border-white/[0.05] flex items-center justify-center">
            {/* SVG Intersection Map */}
            <svg viewBox="0 0 200 200" className="w-full h-full p-2">
              {/* Intersection background roads */}
              <rect x="85" y="0" width="30" height="200" fill="#1e293b" opacity="0.6" />
              <rect x="0" y="85" width="200" height="30" fill="#1e293b" opacity="0.6" />
              
              {/* Lane dividers */}
              <line x1="100" y1="0" x2="100" y2="200" stroke="#475569" strokeDasharray="3 3" />
              <line x1="0" y1="100" x2="200" y2="100" stroke="#475569" strokeDasharray="3 3" />
              
              {/* Crosswalk lines */}
              <line x1="85" y1="70" x2="115" y2="70" stroke="#94a3b8" strokeWidth="2" strokeDasharray="2 1" />
              <line x1="85" y1="130" x2="115" y2="130" stroke="#94a3b8" strokeWidth="2" strokeDasharray="2 1" />
              <line x1="70" y1="85" x2="70" y2="115" stroke="#94a3b8" strokeWidth="2" strokeDasharray="2 1" />
              <line x1="130" y1="85" x2="130" y2="115" stroke="#94a3b8" strokeWidth="2" strokeDasharray="2 1" />

              {/* Dynamic traffic lights */}
              {/* North Signal */}
              <circle cx="75" cy="65" r="4" fill={trafficData.active_lane === "North" ? "#10b981" : "#ef4444"} className={trafficData.active_lane === "North" ? "animate-pulse" : ""} />
              {/* South Signal */}
              <circle cx="125" cy="135" r="4" fill={trafficData.active_lane === "South" ? "#10b981" : "#ef4444"} className={trafficData.active_lane === "South" ? "animate-pulse" : ""} />
              {/* East Signal */}
              <circle cx="135" cy="75" r="4" fill={trafficData.active_lane === "East" ? "#10b981" : "#ef4444"} className={trafficData.active_lane === "East" ? "animate-pulse" : ""} />
              {/* West Signal */}
              <circle cx="65" cy="125" r="4" fill={trafficData.active_lane === "West" ? "#10b981" : "#ef4444"} className={trafficData.active_lane === "West" ? "animate-pulse" : ""} />

              {/* Junction center glow */}
              <circle cx="100" cy="100" r="12" fill={trafficData.active_lane ? "rgba(249, 115, 22, 0.1)" : "rgba(255,255,255,0.02)"} stroke={trafficData.active_lane ? "#f97316" : "#475569"} strokeWidth="1" />
              <text x="100" y="102" textAnchor="middle" fill="#f97316" fontSize="6" fontWeight="bold" fontFamily="monospace">
                {trafficData.active_lane ? trafficData.active_lane[0] : "--"}
              </text>

              {/* Animated dots representing traffic flowing */}
              {/* North Lane vehicles flowing downward */}
              {vehicleCounts.North > 0 && (
                <motion.circle
                  cx="92" r="2.5" fill="#f59e0b"
                  initial={{ cy: 10 }}
                  animate={{ cy: [10, 85, 115, 190] }}
                  transition={{ repeat: Infinity, duration: Math.max(1.2, 4.5 - vehicleCounts.North * 0.25), ease: "linear" }}
                />
              )}
              {/* South Lane vehicles flowing upward */}
              {vehicleCounts.South > 0 && (
                <motion.circle
                  cx="108" r="2.5" fill="#3b82f6"
                  initial={{ cy: 190 }}
                  animate={{ cy: [190, 115, 85, 10] }}
                  transition={{ repeat: Infinity, duration: Math.max(1.2, 4.5 - vehicleCounts.South * 0.25), ease: "linear" }}
                />
              )}
              {/* East Lane vehicles flowing westward */}
              {vehicleCounts.East > 0 && (
                <motion.circle
                  cy="92" r="2.5" fill="#10b981"
                  initial={{ cx: 190 }}
                  animate={{ cx: [190, 115, 85, 10] }}
                  transition={{ repeat: Infinity, duration: Math.max(1.2, 4.5 - vehicleCounts.East * 0.25), ease: "linear" }}
                />
              )}
              {/* West Lane vehicles flowing eastward */}
              {vehicleCounts.West > 0 && (
                <motion.circle
                  cy="108" r="2.5" fill="#ec4899"
                  initial={{ cx: 10 }}
                  animate={{ cx: [10, 85, 115, 190] }}
                  transition={{ repeat: Infinity, duration: Math.max(1.2, 4.5 - vehicleCounts.West * 0.25), ease: "linear" }}
                />
              )}
            </svg>
            <div className="absolute bottom-2 left-2 right-2 flex justify-between text-[8px] font-mono text-slate-500">
              <span>LATENCY: ~30ms</span>
              <span>RF STATE: {trafficData.congestion_level}</span>
            </div>
          </div>
          <div className="w-full text-center mt-3 text-xs text-slate-400">
            Active green path: <span className="font-semibold text-emerald-400">{trafficData.active_lane || '--'} Lane</span>
          </div>
        </motion.div>

        {/* Column 3: Real-Time Violation Log Terminal */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05] flex flex-col h-full min-h-[360px]"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest">
              🚨 Live Violation Terminal
            </h3>
            <span className="text-[8px] font-mono font-semibold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full uppercase tracking-widest animate-pulse">
              Live Feed
            </span>
          </div>
          
          <div className="flex-1 bg-black/60 rounded-xl p-4 border border-white/[0.03] font-mono text-xs overflow-y-auto space-y-2.5 max-h-[300px] scrollbar-thin">
            {violationLogs.map((log) => (
              <div key={log.id} className="flex items-start gap-2 text-slate-300">
                <span className="text-slate-500 select-none">[{log.time}]</span>
                <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold uppercase ${
                  log.type === 'speed' ? 'bg-amber-500/20 text-amber-400' :
                  log.type === 'helmet' ? 'bg-indigo-500/20 text-indigo-400' :
                  log.type === 'wrong' ? 'bg-purple-500/20 text-purple-400' :
                  'bg-rose-500/20 text-rose-400'
                }`}>
                  {log.type}
                </span>
                <span className="flex-1">{log.msg}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 text-[10px] text-slate-500 flex justify-between items-center">
            <span>Logged Events ({totalViolations})</span>
            <span>Auto-refreshing</span>
          </div>
        </motion.div>
      </motion.div>

      {/* ── Advanced Control Panels & Detailed Analytics ── */}
      <motion.div 
        variants={stagger} 
        initial="hidden" 
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Interactive Simulation Controls */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05]"
        >
          <div className="flex items-center gap-2 mb-4">
            <Cpu size={16} className="text-amber-400" />
            <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest">
              🎛️ Priority Signal Simulation Override
            </h3>
          </div>
          <p className="text-xs text-slate-400 mb-5 leading-relaxed">
            Click any lane below to simulate an active Emergency Vehicle (Ambulance / Fire Truck) approaching the junction. The smart signaling processor will instantly override the active sequence to prioritize safety.
          </p>

          <div className="grid grid-cols-2 gap-3 mb-4">
            {[
              { name: 'North Lane 🚑', val: 'North' },
              { name: 'South Lane 🚑', val: 'South' },
              { name: 'East Lane 🚒', val: 'East' },
              { name: 'West Lane 🚒', val: 'West' }
            ].map(({ name, val }) => {
              const active = activeOverride === val;
              return (
                <button
                  key={val}
                  onClick={() => handleTriggerEmergency(val)}
                  className={`px-4 py-3 rounded-xl border font-sans font-semibold text-xs transition-all duration-200 active:scale-95 ${
                    active 
                      ? 'bg-amber-500 text-white border-amber-600 shadow-[0_0_12px_rgba(249,115,22,0.3)]' 
                      : 'border-white/[0.04] bg-white/[0.015] text-slate-300 hover:bg-white/[0.04]'
                  }`}
                >
                  {name}
                </button>
              );
            })}
          </div>
          
          <button
            onClick={handleClearOverride}
            disabled={!activeOverride}
            className="w-full py-2.5 rounded-xl border border-rose-500/30 bg-rose-500/5 text-rose-400 font-semibold text-xs transition-all hover:bg-rose-500/10 active:scale-98 disabled:opacity-30 disabled:pointer-events-none"
          >
            Clear Override Protocols
          </button>
        </motion.div>

        {/* Violations Categories Analytics progress bars */}
        <motion.div 
          variants={rise}
          className="glass-panel rounded-2xl p-6 border border-white/[0.05]"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert size={16} className="text-rose-400" />
              <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest">
                📊 Traffic Violation Breakdown
              </h3>
            </div>
            <span className="text-[10px] font-mono font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full">
              Live Categories
            </span>
          </div>

          <div className="space-y-3">
            {[
              { label: '🔴 Red Light Jump Violations', val: violationsData.red_light || 0, max: 100, color: 'from-red-500 to-rose-400' },
              { label: '🚗 Wrong Side Driving Alerts', val: violationsData.wrong_side || 0, max: 100, color: 'from-orange-500 to-amber-400' },
              { label: '⚡ Speed Limit Overriding Speeders', val: violationsData.speeding || 0, max: 100, color: 'from-yellow-500 to-yellow-300' },
              { label: '🪖 Rider Without Helmet Checks', val: violationsData.no_helmet || 0, max: 100, color: 'from-indigo-500 to-purple-400' }
            ].map(({ label, val, color }) => {
              // Calculate percent of total violations safely
              const percent = totalViolations > 0 ? (val / totalViolations) * 100 : 0;
              return (
                <div key={label} className="space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-400 font-medium">
                    <span>{label}</span>
                    <span className="font-mono font-bold text-slate-200">{val}</span>
                  </div>
                  <div className="h-2 bg-white/[0.015] border border-white/[0.03] rounded-full overflow-hidden relative">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percent || 2}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className={`h-full bg-gradient-to-r ${color} rounded-full`}
                    />
                  </div>
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
        className="glass-panel rounded-2xl p-6 border border-white/[0.05] h-[260px] flex flex-col group hover:shadow-[0_24px_50px_-12px_rgba(249,115,22,0.08)] hover:border-amber-500/30 transition-all duration-300"
      >
        <div className="flex items-center justify-between mb-4 shrink-0">
          <div>
            <h3 className="font-display font-bold text-slate-200 flex items-center gap-2 text-sm uppercase tracking-widest">
              <TrendingUp size={15} className="text-amber-500" /> Vehicle Count Stream History
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
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'Space Mono' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'Space Mono' }} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'rgba(249, 115, 22, 0.2)', strokeWidth: 1.5, strokeDasharray: '5 3' }} />
                <Area 
                  type="monotone" 
                  dataKey="vehicles" 
                  stroke="#f97316" 
                  strokeWidth={2}
                  fill="url(#areaGrad)"
                  activeDot={{ r: 4, fill: '#f97316', stroke: '#fff', strokeWidth: 1.5 }} 
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
