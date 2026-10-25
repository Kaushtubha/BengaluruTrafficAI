import React, { useEffect, useState, useCallback } from 'react';
import { useStore } from '../store/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Navigation, MapPin, Compass, AlertCircle, CheckCircle2,
  Clock, ShieldAlert, RefreshCw, Car, Info, ShieldCheck,
  AlertTriangle, ArrowRight, CornerDownRight, Radio, ExternalLink
} from 'lucide-react';
import toast from 'react-hot-toast';

const CORRIDORS = [
  { id: 'North', name: 'North Corridor', desc: 'From Hosur Rd / Koramangala', heading: '0° N' },
  { id: 'South', name: 'South Corridor', desc: 'From Electronic City / Bommanahalli', heading: '180° S' },
  { id: 'East', name: 'East Corridor', desc: 'From HSR Layout / Bellandur / ORR', heading: '90° E' },
  { id: 'West', name: 'West Corridor', desc: 'From BTM Layout / Bannerghatta', heading: '270° W' },
];

const LANDMARKS = [
  { name: 'Koramangala 5th Block', lat: 12.9352, lon: 77.6245 },
  { name: 'HSR Layout Sector 1', lat: 12.9116, lon: 77.6389 },
  { name: 'BTM Layout 2nd Stage', lat: 12.9166, lon: 77.6101 },
  { name: 'Electronic City Tollgate', lat: 12.8452, lon: 77.6602 },
];

const stagger = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
const rise = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { ease: [0.16, 1, 0.3, 1], duration: 0.5 } } };

export default function DriverPortal() {
  const {
    driverAdvice,
    driverLoading,
    driverError,
    selectedCorridor,
    userCoords,
    setSelectedCorridor,
    setUserCoords,
    fetchDriverAdvice,
    trafficData,
    signalData
  } = useStore();

  const [autoRefresh, setAutoRefresh] = useState(true);
  const [gpsDetecting, setGpsDetecting] = useState(false);
  const [gpsError, setGpsError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const handleFetch = useCallback(() => {
    fetchDriverAdvice(selectedCorridor, userCoords?.lat, userCoords?.lon);
    setLastRefreshed(new Date());
  }, [fetchDriverAdvice, selectedCorridor, userCoords]);

  // Initial load and periodic refresh
  useEffect(() => {
    handleFetch();
  }, [selectedCorridor, userCoords]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      handleFetch();
    }, 4000);
    return () => clearInterval(interval);
  }, [autoRefresh, handleFetch]);

  // Geolocation handler
  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser');
      setGpsError('UNSUPPORTED');
      return;
    }

    setGpsDetecting(true);
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = {
          lat: parseFloat(pos.coords.latitude.toFixed(6)),
          lon: parseFloat(pos.coords.longitude.toFixed(6)),
        };
        setUserCoords(coords);
        setGpsDetecting(false);
        setGpsError(null);
        toast.success(`Location set: ${coords.lat}, ${coords.lon}`);
      },
      (err) => {
        setGpsDetecting(false);
        console.warn('Geolocation error:', err);
        let msg = 'Unable to retrieve location';
        if (err.code === 1) {
          msg = 'Location access denied. You may choose an approximate landmark preset.';
          setGpsError('PERMISSION_DENIED');
        } else if (err.code === 2) {
          msg = 'Location unavailable. Try an approximate landmark preset.';
          setGpsError('POSITION_UNAVAILABLE');
        } else if (err.code === 3) {
          msg = 'Location request timed out.';
          setGpsError('TIMEOUT');
        }
        toast.error(msg);
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  };

  const handleClearLocation = () => {
    setUserCoords(null);
    setGpsError(null);
    fetchDriverAdvice(selectedCorridor, null, null);
    toast('GPS coordinates cleared', { icon: '📍' });
  };

  // ── Exact Schema Field Mapping Against Real Backend ────────
  const advice = driverAdvice || {};
  const isSimulated = advice.data_source === 'demo_sim';
  const junctionInfo = advice.junction || {};
  const approachInfo = advice.approach || {};
  const distanceTelemetry = advice.distance_telemetry || {};
  const delayTelemetry = advice.delay_telemetry || {};
  const corridorStatus = advice.corridor_status || {};
  const guidelines = advice.safety_guidelines || [];

  const congestionLevel = approachInfo.congestion_level || trafficData?.congestion_level || 'Normal';
  const congestionBadge = {
    Low: { bg: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20', label: 'Flowing Smoothly' },
    Medium: { bg: 'bg-amber-500/10 text-amber-500 border-amber-500/20', label: 'Moderate Density' },
    High: { bg: 'bg-rose-500/10 text-rose-500 border-rose-500/20', label: 'Heavy Congestion' },
  }[congestionLevel] || { bg: 'bg-slate-500/10 text-slate-400 border-slate-500/20', label: 'Calculating...' };

  const isGreenActive = (signalData?.active_lane === selectedCorridor);

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="show"
      className="space-y-6 pb-14 max-w-7xl mx-auto"
    >
      {/* ── Top Header ────────────────────────────────────────── */}
      <motion.div variants={rise} className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-amber-500/10 text-amber-500 border border-amber-500/20">
              Commuter Telemetry
            </span>
            <span className="text-xs text-slate-400 dark:text-dark-400 font-mono">
              Refreshed {lastRefreshed.toLocaleTimeString()}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-extrabold text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
            <Navigation className="text-amber-500" size={28} />
            Driver Assistance Portal
          </h1>
          <p className="text-sm text-slate-500 dark:text-dark-300 mt-1">
            Live corridor approach conditions, aerial proximity, and dynamic junction advisory.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2 self-start md:self-auto flex-wrap">
          <button
            onClick={() => setAutoRefresh(v => !v)}
            aria-label="Toggle automated live synchronization (refreshes every 4 seconds)"
            aria-pressed={autoRefresh}
            className={`px-3 py-2 rounded-xl text-xs font-semibold border flex items-center gap-2 transition-all touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none ${
              autoRefresh
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-600 dark:text-amber-400 shadow-sm'
                : 'bg-slate-100 dark:bg-dark-800 border-slate-200 dark:border-dark-700 text-slate-500 dark:text-dark-400'
            }`}
            title="Toggle automated refresh"
          >
            <Radio size={14} className={autoRefresh ? 'animate-pulse text-amber-500' : ''} />
            {autoRefresh ? 'Live Sync ON' : 'Live Sync Paused'}
          </button>

          <button
            onClick={handleFetch}
            disabled={driverLoading}
            aria-label="Refresh commuter telemetry immediately"
            className="p-2.5 rounded-xl border border-slate-200 dark:border-dark-700 bg-white dark:bg-dark-800 hover:bg-slate-50 dark:hover:bg-dark-750 text-slate-600 dark:text-dark-200 transition-all shadow-sm disabled:opacity-50 touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none"
            title="Refresh now"
          >
            <RefreshCw size={15} className={driverLoading ? 'animate-spin text-amber-500' : ''} />
          </button>
        </div>
      </motion.div>

      {/* ── Backend Telemetry Error / Idle Sleep Alert ──────────── */}
      {driverError && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          role="alert"
          aria-live="polite"
          className="p-4 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle size={20} className="text-amber-500 shrink-0" />
            <div className="text-xs">
              <span className="font-bold text-amber-400 uppercase tracking-wide block">
                Backend Telemetry Offline or Waking Up
              </span>
              <span className="text-amber-100/80">
                {driverError}. Render free-tier instances may require 30–50 seconds to wake from idle spin-down.
              </span>
            </div>
          </div>
          <button
            onClick={handleFetch}
            disabled={driverLoading}
            className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-600 text-white shrink-0 self-start sm:self-auto flex items-center gap-1.5 shadow-sm transition-all disabled:opacity-50 touch-manipulation"
          >
            <RefreshCw size={13} className={driverLoading ? 'animate-spin' : ''} />
            Retry Connection
          </button>
        </motion.div>
      )}

      {/* ── Data Provenance & Junction Disclosure ───────────────── */}
      <motion.div variants={rise} className="glass-card p-4 sm:p-5 rounded-2xl border border-white/60 dark:border-white/[0.08] relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className={`p-2.5 rounded-xl shrink-0 mt-0.5 ${
              isSimulated
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              <Info size={18} />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-white">
                  Data Provenance:
                </span>
                <span className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wide border ${
                  isSimulated
                    ? 'bg-blue-500/10 text-blue-500 dark:text-blue-400 border-blue-500/20'
                    : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
                }`}>
                  {isSimulated ? 'Simulation Feed (demo_sim)' : 'Computer Vision Inference (live_cv)'}
                </span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-dark-800 text-slate-600 dark:text-dark-300">
                  Zero Paid External APIs
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-dark-300 mt-1 leading-relaxed">
                {advice.feed_description || 'Active backend telemetry channel.'} Reference junction:{' '}
                <strong className="text-slate-800 dark:text-slate-200">
                  {junctionInfo.name || 'Silk Board, Bengaluru'}
                </strong>{' '}
                ({junctionInfo.latitude != null && junctionInfo.longitude != null ? `${junctionInfo.latitude}° N, ${junctionInfo.longitude}° E` : 'Configured Coordinates'}).
              </p>
              <p className="text-[11px] text-slate-400 dark:text-dark-500 mt-1 italic">
                * Note: Video stream and simulated vehicle detections are generic urban roadway demonstration models and are not verified field sensor observations from the physical Silk Board intersection.
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ── Emergency Vehicle Active Alert ─────────────────────── */}
      <AnimatePresence>
        {signalData?.priority_lane && signalData.priority_lane !== '--' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            role="alert"
            aria-live="assertive"
            className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 flex items-center gap-3.5"
          >
            <ShieldAlert size={22} className="text-rose-500 shrink-0 animate-bounce" />
            <div className="flex-1 text-xs">
              <span className="font-bold text-rose-400 uppercase tracking-wide block">
                Emergency Priority Vehicle Detected in {signalData.priority_lane} Approach
              </span>
              <span className="text-rose-200/90">
                Automated junction controller has preempted normal cycles to prioritize emergency vehicle clearance. Maintain clear lanes and yield right of way.
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Approach Corridor Selection Grid ──────────────────── */}
      <motion.div variants={rise} className="space-y-3">
        <div className="flex items-center justify-between">
          <label id="corridor-group-label" className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-dark-400">
            Select Your Approach Corridor
          </label>
          <span className="text-xs text-slate-400 dark:text-dark-400">
            Viewing: <strong className="text-amber-500">{selectedCorridor} Corridor</strong>
          </span>
        </div>

        <div
          role="radiogroup"
          aria-labelledby="corridor-group-label"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5"
        >
          {CORRIDORS.map(corridor => {
            const isSelected = selectedCorridor === corridor.id;
            const count = (selectedCorridor === corridor.id && approachInfo.visible_vehicle_count != null)
              ? approachInfo.visible_vehicle_count
              : (trafficData?.vehicle_counts?.[corridor.id] ?? 0);
            const isLaneActive = signalData?.active_lane === corridor.id;

            return (
              <motion.button
                key={corridor.id}
                role="radio"
                aria-checked={isSelected}
                tabIndex={0}
                aria-label={`${corridor.name}, heading ${corridor.heading}. Approach vehicle count: ${count}. Signal status: ${isLaneActive ? 'Green' : 'Red'}`}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedCorridor(corridor.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setSelectedCorridor(corridor.id);
                  }
                }}
                className={`p-4 rounded-2xl text-left border transition-all duration-200 relative overflow-hidden flex flex-col justify-between touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none focus:outline-none ${
                  isSelected
                    ? 'bg-amber-500/10 dark:bg-amber-500/[0.12] border-amber-500/40 shadow-glow-sm'
                    : 'bg-white/80 dark:bg-dark-850/60 border-slate-200/80 dark:border-white/[0.06] hover:border-slate-300 dark:hover:border-white/[0.12]'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-dark-800 text-slate-500 dark:text-dark-400">
                      {corridor.heading}
                    </span>
                    <span className={`w-2 h-2 rounded-full ${
                      isLaneActive ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]' : 'bg-rose-400/70'
                    }`} title={isLaneActive ? 'Green Signal' : 'Red Signal'} />
                  </div>
                  <h3 className={`font-display font-bold text-sm ${isSelected ? 'text-amber-600 dark:text-amber-400' : 'text-slate-800 dark:text-white'}`}>
                    {corridor.name}
                  </h3>
                  <p className="text-[11px] text-slate-400 dark:text-dark-400 mt-0.5 line-clamp-1">
                    {corridor.desc}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-white/[0.05] flex items-center justify-between">
                  <span className="text-xs text-slate-400 dark:text-dark-500">Approaching:</span>
                  <span className="text-xs font-mono font-bold text-slate-700 dark:text-dark-200">
                    {count} vehicles
                  </span>
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>

      {/* ── GPS Proximity & Distance Section ───────────────────── */}
      <motion.div variants={rise} className="glass-card p-5 sm:p-6 rounded-2xl border border-white/60 dark:border-white/[0.08] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20">
              <Compass size={18} />
            </div>
            <div>
              <h2 className="font-display font-bold text-base text-slate-900 dark:text-white">
                GPS Proximity & Junction Distance
              </h2>
              <p className="text-xs text-slate-400 dark:text-dark-400">
                Optional geolocation to determine straight-line proximity to the junction.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={handleDetectLocation}
              disabled={gpsDetecting}
              aria-label={gpsDetecting ? 'Detecting current GPS location' : userCoords ? 'Re-detect current location' : 'Detect current GPS location'}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-600 text-white flex items-center gap-2 shadow-sm transition-all disabled:opacity-50 touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none"
            >
              <MapPin size={14} className={gpsDetecting ? 'animate-bounce' : ''} />
              {gpsDetecting ? 'Detecting Location...' : userCoords ? 'Re-detect Location' : 'Detect My Location'}
            </button>
            {userCoords && (
              <button
                onClick={handleClearLocation}
                aria-label="Clear current GPS coordinates"
                className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-150 dark:bg-dark-800 text-slate-500 hover:text-slate-800 dark:hover:text-white border border-slate-200 dark:border-dark-700 transition-colors touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none"
              >
                Clear GPS
              </button>
            )}
          </div>
        </div>

        {/* Quick Presets with Explicit Approximate Disclosure */}
        <div className="pt-2">
          <span id="landmark-presets-label" className="text-[11px] font-semibold text-slate-400 dark:text-dark-400 uppercase tracking-wider block mb-2">
            Or select an approximate reference landmark (not your actual location):
          </span>
          <div role="group" aria-labelledby="landmark-presets-label" className="flex flex-wrap gap-2">
            {LANDMARKS.map(lm => {
              const isActive = userCoords?.lat === lm.lat && userCoords?.lon === lm.lon;
              return (
                <button
                  key={lm.name}
                  aria-label={`Select ${lm.name} reference landmark preset`}
                  aria-pressed={isActive}
                  onClick={() => setUserCoords({ lat: lm.lat, lon: lm.lon })}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all touch-manipulation focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none ${
                    isActive
                      ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                      : 'bg-slate-50 dark:bg-dark-800/80 border-slate-200 dark:border-dark-700 text-slate-600 dark:text-dark-300 hover:border-amber-500/50'
                  }`}
                >
                  {lm.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Distance Display & Disclaimer */}
        <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-dark-850/80 border border-slate-200/70 dark:border-dark-700/60 mt-3">
          {userCoords && distanceTelemetry.straight_line_distance_km != null ? (
            <div className="space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 dark:text-dark-400">Straight-Line Aerial Distance:</span>
                  <span className="text-xl font-display font-extrabold text-amber-500 font-mono">
                    {distanceTelemetry.straight_line_distance_km} km
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400 dark:text-dark-400">
                  From: {userCoords.lat}° N, {userCoords.lon}° E
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-dark-400 leading-relaxed border-t border-slate-200/60 dark:border-dark-700/60 pt-2">
                <strong className="text-slate-700 dark:text-slate-300">Notice:</strong>{' '}
                {distanceTelemetry.disclaimer ||
                  'Straight-line aerial distance only. Actual road driving distance will be longer due to road topology and flyover ramps.'}
              </p>
            </div>
          ) : (
            <div className="text-xs text-slate-500 dark:text-dark-400 flex items-start gap-2">
              <Info size={15} className="text-slate-400 shrink-0 mt-0.5" />
              <span>
                {gpsError === 'PERMISSION_DENIED'
                  ? 'Location permission was denied in your browser. You can still select any of the landmark presets above to view straight-line proximity.'
                  : gpsError === 'TIMEOUT'
                  ? 'Location request timed out. Please retry or click an approximate landmark preset above.'
                  : distanceTelemetry.status === 'INCOMPLETE_COORDINATES_MISSING_LAT' || distanceTelemetry.status === 'INCOMPLETE_COORDINATES_MISSING_LON'
                  ? 'Incomplete GPS coordinates provided. Please detect location or select an approximate landmark preset.'
                  : distanceTelemetry.status === 'COORDINATES_OUT_OF_RANGE'
                  ? 'Supplied coordinates were outside valid geographic ranges (-90 to 90 lat, -180 to 180 lon).'
                  : distanceTelemetry.status === 'INVALID_COORDINATE_FORMAT'
                  ? 'Supplied coordinate format was not valid numbers.'
                  : distanceTelemetry.status === 'JUNCTION_COORDINATES_CONFIG_ERROR'
                  ? 'Junction reference coordinates are misconfigured in environment.'
                  : 'No coordinates supplied. Detect your browser location or click an approximate landmark preset to calculate aerial proximity to the junction.'}
              </span>
            </div>
          )}
        </div>
      </motion.div>

      {/* ── Main Corridor Metrics & Advisory Grid ─────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Signal & Approach Status */}
        <motion.div variants={rise} className="glass-card p-6 rounded-2xl border border-white/60 dark:border-white/[0.08] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
                  <Clock size={16} />
                </div>
                <h3 className="font-display font-bold text-sm text-slate-900 dark:text-white">
                  Signal & Clearance
                </h3>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wide border ${
                isGreenActive
                  ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-500 border-rose-500/20'
              }`}>
                {isGreenActive ? 'Signal: GREEN' : 'Signal: RED'}
              </span>
            </div>

            <div className="space-y-3.5">
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-white/[0.05]">
                <span className="text-xs text-slate-400 dark:text-dark-400">Green Time Allotted</span>
                <span className="text-sm font-mono font-bold text-slate-800 dark:text-white">
                  {approachInfo.assigned_green_time_sec ?? signalData?.green_times?.[selectedCorridor] ?? 0}s
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-white/[0.05]">
                <span className="text-xs text-slate-400 dark:text-dark-400">Active Priority Approach</span>
                <span className="text-sm font-semibold text-slate-800 dark:text-white">
                  {signalData?.priority_lane && signalData.priority_lane !== '--' ? `${signalData.priority_lane} (Emergency)` : 'Standard Rotation'}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-white/[0.05]">
                <span className="text-xs text-slate-400 dark:text-dark-400">Signal Cycle Duration</span>
                <span className="text-sm font-mono font-bold text-slate-800 dark:text-white">
                  {approachInfo.cycle_time_sec ?? signalData?.cycle_time ?? 120}s
                </span>
              </div>
            </div>
          </div>

          <div className="mt-5 p-3 rounded-xl bg-slate-50 dark:bg-dark-850 border border-slate-200/60 dark:border-dark-700/60 text-xs">
            <span className="font-bold text-slate-700 dark:text-slate-300 block mb-0.5">
              Cycle Recommendation:
            </span>
            <span className="text-slate-500 dark:text-dark-400">
              {isGreenActive
                ? 'Lane currently has green clearance. Proceed smoothly without blocking box junctions.'
                : 'Lane is on red standby. Anticipate next phase as queue clears in priority order.'}
            </span>
          </div>
        </motion.div>

        {/* Card 2: Density & Queue Delay Status (Honest Telemetry) */}
        <motion.div variants={rise} className="glass-card p-6 rounded-2xl border border-white/60 dark:border-white/[0.08] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
                  <Car size={16} />
                </div>
                <h3 className="font-display font-bold text-sm text-slate-900 dark:text-white">
                  Corridor Congestion
                </h3>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${congestionBadge.bg}`}>
                {congestionBadge.label}
              </span>
            </div>

            <div className="space-y-3.5">
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-white/[0.05]">
                <span className="text-xs text-slate-400 dark:text-dark-400">Vehicles in Approach</span>
                <span className="text-sm font-mono font-bold text-slate-800 dark:text-white">
                  {approachInfo.visible_vehicle_count ?? trafficData?.vehicle_counts?.[selectedCorridor] ?? 0}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-white/[0.05]">
                <span className="text-xs text-slate-400 dark:text-dark-400">Estimated Clearance Delay</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-dark-800 text-slate-500 dark:text-dark-400">
                  Unavailable (Field-of-View Limit)
                </span>
              </div>
            </div>
          </div>

          <div className="mt-5 p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs">
            <div className="flex items-start gap-2">
              <AlertCircle size={15} className="text-amber-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-amber-600 dark:text-amber-400 block mb-0.5">
                  Queue Delay Transparency:
                </span>
                <p className="text-slate-500 dark:text-dark-400 text-[11px] leading-relaxed">
                  {delayTelemetry.reason ||
                    'Queue clearance delay cannot be accurately calculated without upstream queue length and continuous arrival rates outside camera FOV.'}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Card 3: Alternative Routes Status (Zero Fabrication) */}
        <motion.div variants={rise} className="glass-card p-6 rounded-2xl border border-white/60 dark:border-white/[0.08] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
                  <CornerDownRight size={16} />
                </div>
                <h3 className="font-display font-bold text-sm text-slate-900 dark:text-white">
                  Alternative Rerouting
                </h3>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-dark-800 text-slate-500 dark:text-dark-400 border border-slate-200 dark:border-dark-700">
                Single Junction Feeds
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-dark-850 border border-slate-200/60 dark:border-dark-700/60 text-xs space-y-2">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-semibold">
                <Info size={14} className="text-slate-400 shrink-0" />
                <span>Reroute Advice: Not Fabricated</span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-dark-400 leading-relaxed">
                Alternative corridor conditions require external city telemetry or multi-camera feeds not present in this single-junction system ({corridorStatus.unmonitored_routes || 'DATA_UNAVAILABLE'}).
              </p>
            </div>
          </div>

          <div className="mt-5 p-3 rounded-xl bg-slate-100/60 dark:bg-dark-800/40 border border-slate-200/50 dark:border-dark-700/50 text-xs text-slate-500 dark:text-dark-400">
            <span>
              Operating within strict ₹0 open-source constraints. No commercial mapping APIs (Google Maps, Mapbox, TomTom) are invoked.
            </span>
          </div>
        </motion.div>
      </div>

      {/* ── Dynamic Advisory & Safety Guidelines ────────────────── */}
      <motion.div variants={rise} className="glass-card p-6 rounded-2xl border border-white/60 dark:border-white/[0.08] space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
            <ShieldCheck size={18} />
          </div>
          <div>
            <h2 className="font-display font-bold text-base text-slate-900 dark:text-white">
              Dynamic Commuter Advisory Guidelines
            </h2>
            <p className="text-xs text-slate-400 dark:text-dark-400">
              Corridor-specific safety and situational instructions calculated from active vehicle density.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-1">
          {guidelines.length > 0 ? (
            guidelines.map((guideline, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-50/80 dark:bg-dark-850/60 border border-slate-200/60 dark:border-dark-700/60 flex items-start gap-3"
              >
                <div className="w-5 h-5 rounded-full bg-amber-500/15 text-amber-500 flex items-center justify-center shrink-0 font-bold text-[10px] mt-0.5">
                  {idx + 1}
                </div>
                <p className="text-xs text-slate-700 dark:text-dark-200 leading-relaxed font-medium">
                  {guideline}
                </p>
              </div>
            ))
          ) : (
            <div className="col-span-3 text-xs text-slate-400 dark:text-dark-500 py-3 text-center">
              Fetching active corridor guidelines...
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
