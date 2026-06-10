import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, RadarChart, Radar,
  PolarGrid, PolarAngleAxis
} from 'recharts';
import { motion } from 'framer-motion';
import {
  ShieldAlert, TrendingUp, Clock, Zap, AlertTriangle, Activity
} from 'lucide-react';

const stagger = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.07 } } };
const rise = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { ease: [0.16, 1, 0.3, 1], duration: 0.6 } } };

const VIOLATION_COLORS = ['#ef4444', '#f97316', '#eab308', '#8b5cf6'];
const LANE_COLORS = { North: '#6366f1', South: '#8b5cf6', East: '#10b981', West: '#f59e0b' };

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card px-4 py-3 rounded-xl text-xs shadow-glass-dark border border-white/10">
      <p className="text-slate-400 mb-1 font-medium">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="font-bold text-sm" style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  );
}

export default function Analytics() {
  const { trafficData, violationsData, signalData, history, fetchTrafficData } = useStore();
  const [time, setTime] = useState(new Date());
  const [violationHistory, setViolationHistory] = useState([]);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchTrafficData, 3000);
    fetchTrafficData();
    return () => clearInterval(interval);
  }, []);

  // Build violation history over time
  useEffect(() => {
    const now = time.toLocaleTimeString('en-US', { hour12: false });
    setViolationHistory(prev => {
      const next = [...prev, {
        time: now,
        red_light: violationsData.red_light || 0,
        wrong_side: violationsData.wrong_side || 0,
        speeding: violationsData.speeding || 0,
        no_helmet: violationsData.no_helmet || 0,
      }];
      return next.slice(-15);
    });
  }, [violationsData.total_violations]);

  const totalViolations = violationsData.total_violations || 0;

  const pieData = [
    { name: 'Red Light', value: violationsData.red_light || 0 },
    { name: 'Wrong Side', value: violationsData.wrong_side || 0 },
    { name: 'Speeding', value: violationsData.speeding || 0 },
    { name: 'No Helmet', value: violationsData.no_helmet || 0 },
  ].filter(d => d.value > 0);

  const radarData = [
    { subject: 'North', A: trafficData.vehicle_counts?.North || 0 },
    { subject: 'South', A: trafficData.vehicle_counts?.South || 0 },
    { subject: 'East', A: trafficData.vehicle_counts?.East || 0 },
    { subject: 'West', A: trafficData.vehicle_counts?.West || 0 },
  ];

  const laneBarData = Object.entries(trafficData.vehicle_counts || {}).map(([lane, count]) => ({
    lane,
    vehicles: count,
    greenTime: signalData.green_times?.[lane] || 0,
  }));

  const congestionColor = {
    Low: '#10b981',
    Medium: '#f59e0b',
    High: '#ef4444',
  }[trafficData.congestion_level] || '#6366f1';

  const statCards = [
    { label: 'Total Violations', value: totalViolations, icon: ShieldAlert, color: 'rose', glow: 'rgba(239,68,68,0.15)' },
    { label: 'Red Light Jumps', value: violationsData.red_light || 0, icon: AlertTriangle, color: 'red', glow: 'rgba(239,68,68,0.15)' },
    { label: 'Speeding Cases', value: violationsData.speeding || 0, icon: Zap, color: 'amber', glow: 'rgba(245,158,11,0.15)' },
    { label: 'No Helmet', value: violationsData.no_helmet || 0, icon: Activity, color: 'violet', glow: 'rgba(139,92,246,0.15)' },
  ];

  return (
    <div className="space-y-7 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row sm:items-start justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={13} className="text-amber-400 animate-pulse" />
            <span className="text-[11px] font-bold tracking-[0.15em] text-amber-400 uppercase text-glow">
              Analytics Engine
            </span>
            <span className="w-1 h-1 rounded-full bg-slate-700 mx-1" />
            <span className="text-[11px] font-mono font-medium text-slate-400">
              {time.toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
          <h2 className="text-gradient-hero font-display font-extrabold text-3xl sm:text-4xl tracking-tight leading-none">
            Traffic Analytics
          </h2>
          <p className="text-slate-400 text-sm mt-2 font-sans max-w-lg">
            Deep-dive into violation patterns, lane load distributions, and signal efficiency metrics at Silk Board Junction.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="px-3 py-1.5 rounded-full border text-xs font-mono font-bold uppercase tracking-wider"
            style={{ color: congestionColor, borderColor: `${congestionColor}30`, backgroundColor: `${congestionColor}10` }}>
            <span className="w-2 h-2 rounded-full inline-block mr-1.5" style={{ backgroundColor: congestionColor }} />
            {trafficData.congestion_level || 'Loading'} Congestion
          </div>
        </div>
      </motion.div>

      {/* Stat Cards */}
      <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon: Icon, color, glow }) => (
          <motion.div
            key={label}
            variants={rise}
            whileHover={{ y: -6, scale: 1.02, transition: { duration: 0.3, type: 'spring', stiffness: 300, damping: 20 } }}
            className={`glass-panel rounded-2xl p-5 relative overflow-hidden group cursor-default transition-all duration-300 z-10`}
            style={{ '--glow': glow }}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{label}</span>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-${color}-500/10`}>
                <Icon size={15} className={`text-${color}-400`} />
              </div>
            </div>
            <div className="font-mono font-bold text-3xl tracking-tight text-white">{value.toLocaleString()}</div>
            <div className="mt-2 h-1 rounded-full bg-white/5">
              <motion.div
                className={`h-full rounded-full bg-${color}-500`}
                initial={{ width: 0 }}
                animate={{ width: `${totalViolations > 0 ? Math.min((value / totalViolations) * 100, 100) : 5}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts Grid */}
      <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Violation Breakdown Pie Chart */}
        <motion.div variants={rise} className="glass-panel rounded-2xl p-6 border border-white/[0.05]">
          <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest mb-4 flex items-center gap-2">
            <ShieldAlert size={14} className="text-rose-400" /> Violation Breakdown
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={VIOLATION_COLORS[index % VIOLATION_COLORS.length]} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: '10px', fontFamily: 'monospace', color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[220px] flex items-center justify-center text-slate-500 text-xs">
              Waiting for violations data...
            </div>
          )}
        </motion.div>

        {/* Lane Load Radar Chart */}
        <motion.div variants={rise} className="glass-panel rounded-2xl p-6 border border-white/[0.05]">
          <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest mb-4 flex items-center gap-2">
            <Activity size={14} className="text-indigo-400" /> Lane Load Radar
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart cx="50%" cy="50%" outerRadius={80} data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.05)" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#64748b', fontFamily: 'monospace' }} />
              <Radar name="Vehicles" dataKey="A" stroke="#f97316" fill="#f97316" fillOpacity={0.15} strokeWidth={2} />
              <Tooltip content={<ChartTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Signal Green Time Bar Chart */}
        <motion.div variants={rise} className="glass-panel rounded-2xl p-6 border border-white/[0.05]">
          <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest mb-4 flex items-center gap-2">
            <Clock size={14} className="text-sky-400" /> Signal Green Times
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={laneBarData} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
              <XAxis dataKey="lane" tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: '#64748b', fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="greenTime" name="Green (s)" radius={[4, 4, 0, 0]} fill="#22d3ee" fillOpacity={0.7} />
              <Bar dataKey="vehicles" name="Vehicles" radius={[4, 4, 0, 0]} fill="#f97316" fillOpacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </motion.div>

      {/* Violation Over Time Stacked Bar */}
      <motion.div
        variants={rise}
        className="glass-panel rounded-2xl p-6 border border-white/[0.05] h-[280px] flex flex-col"
      >
        <div className="flex items-center justify-between mb-4 shrink-0">
          <div>
            <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest flex items-center gap-2">
              <TrendingUp size={14} className="text-amber-500" /> Violation Trend (Live)
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">Cumulative violation counts by type over time</p>
          </div>
          <span className="text-[9px] font-mono font-semibold text-slate-500 uppercase tracking-widest">Last 15 snapshots</span>
        </div>
        <div className="flex-1 min-h-0">
          {violationHistory.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={violationHistory} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
                <XAxis dataKey="time" tick={{ fontSize: 8, fill: '#475569', fontFamily: 'monospace' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 8, fill: '#475569', fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="red_light" name="Red Light" stackId="a" fill="#ef4444" fillOpacity={0.85} />
                <Bar dataKey="wrong_side" name="Wrong Side" stackId="a" fill="#f97316" fillOpacity={0.85} />
                <Bar dataKey="speeding" name="Speeding" stackId="a" fill="#eab308" fillOpacity={0.85} />
                <Bar dataKey="no_helmet" name="No Helmet" stackId="a" fill="#8b5cf6" fillOpacity={0.85} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex flex-col items-center justify-center gap-2 text-slate-500">
              <Activity size={24} className="opacity-40 animate-pulse" />
              <p className="text-xs font-semibold">Collecting violation data...</p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Lane Performance Table */}
      <motion.div variants={rise} className="glass-panel rounded-2xl p-6 border border-white/[0.05]">
        <h3 className="font-display font-bold text-slate-200 text-sm uppercase tracking-widest mb-5 flex items-center gap-2">
          🚦 Lane Performance Summary
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b border-white/[0.05]">
                {['Lane', 'Vehicles', 'Green Time', 'Load %', 'Status'].map(h => (
                  <th key={h} className="text-left py-2 px-3 text-[10px] font-bold uppercase tracking-widest text-slate-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(trafficData.vehicle_counts || {}).map(([lane, count]) => {
                const total = trafficData.total_vehicles || 1;
                const pct = Math.round((count / total) * 100);
                const greenTime = signalData.green_times?.[lane] || 0;
                const isActive = lane === trafficData.active_lane;
                return (
                  <tr key={lane} className={`border-b border-white/[0.02] transition-colors ${isActive ? 'bg-amber-500/5' : 'hover:bg-white/[0.015]'}`}>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: LANE_COLORS[lane] }} />
                        <span className={isActive ? 'text-amber-400 font-bold' : 'text-slate-300'}>{lane}</span>
                        {isActive && <span className="text-[8px] bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded-full font-bold uppercase tracking-wider">Active</span>}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-300">{count}</td>
                    <td className="py-3 px-3">
                      <span className="text-sky-400">{greenTime}s</span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-white/[0.05] rounded-full overflow-hidden w-20">
                          <div
                            className="h-full rounded-full transition-all duration-700"
                            style={{ width: `${pct}%`, backgroundColor: LANE_COLORS[lane] }}
                          />
                        </div>
                        <span className="text-slate-400">{pct}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wide ${
                        isActive ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700/50 text-slate-400'
                      }`}>
                        {isActive ? 'GREEN' : 'QUEUED'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="mt-4 pt-3 border-t border-white/[0.03] flex justify-between items-center text-xs text-slate-500">
          <span>Cycle Time: <span className="text-amber-400 font-mono font-bold">{signalData.cycle_time}s</span></span>
          <span>Updated: <span className="font-mono text-slate-400">{time.toLocaleTimeString('en-US', { hour12: false })}</span></span>
        </div>
      </motion.div>
    </div>
  );
}
