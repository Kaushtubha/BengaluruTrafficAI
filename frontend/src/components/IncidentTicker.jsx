import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';
import { audioTelemetry } from '../utils/audioTelemetry';
import {
  AlertTriangle, ShieldAlert, Zap, Activity, X,
  ExternalLink, Volume2, CheckCircle2, Copy
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function IncidentTicker() {
  const { violationsData, trafficData } = useStore();
  const [currentIncident, setCurrentIncident] = useState(null);
  const [modalIncident, setModalIncident] = useState(null);
  const [isDismissed, setIsDismissed] = useState(false);

  // Generate synthetic incident event whenever violation counts increment
  useEffect(() => {
    if (violationsData.total_violations > 0) {
      const corridors = ['North', 'South', 'East', 'West'];
      const randomLane = corridors[Math.floor(Math.random() * corridors.length)];
      const randomVehicleId = Math.floor(Math.random() * 800 + 100);

      const incidentTypes = [
        {
          type: 'Speeding Violation',
          lane: randomLane,
          speed: `${Math.floor(Math.random() * 25 + 68)} km/h`,
          speedLimit: '40 km/h',
          vehicle: `Vehicle #${randomVehicleId}`,
          severity: 'HIGH',
          action: 'Automatic speed camera enforcement logged. Issue electronic e-challan.',
          icon: Zap,
          color: 'text-amber-400 bg-amber-500/10 border-amber-500/20'
        },
        {
          type: 'Red Light Jump',
          lane: randomLane,
          vehicle: `Vehicle #${randomVehicleId}`,
          severity: 'CRITICAL',
          action: 'Stop line breach past signal phase. Alert Silk Board junction patrol.',
          icon: AlertTriangle,
          color: 'text-rose-400 bg-rose-500/10 border-rose-500/20'
        },
        {
          type: 'Wrong-Side Driving',
          lane: randomLane,
          vehicle: `Vehicle #${randomVehicleId}`,
          severity: 'CRITICAL',
          action: 'Opposing corridor encroachment. Trigger digital variable message sign (VMS).',
          icon: ShieldAlert,
          color: 'text-red-400 bg-red-500/10 border-red-500/20'
        },
        {
          type: 'Helmet Non-Compliance',
          lane: randomLane,
          vehicle: `Two-Wheeler #${randomVehicleId}`,
          severity: 'MODERATE',
          action: 'Rider safety non-compliance detected by edge vision classifier.',
          icon: Activity,
          color: 'text-violet-400 bg-violet-500/10 border-violet-500/20'
        }
      ];

      const selected = incidentTypes[Math.floor(Math.random() * incidentTypes.length)];
      setCurrentIncident({
        id: Date.now(),
        ...selected,
        timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      });
      setIsDismissed(false);
    }
  }, [violationsData.total_violations]);

  if (!currentIncident || isDismissed) return null;

  const Icon = currentIncident.icon;

  const copyIncidentData = () => {
    const text = `[INCIDENT #${currentIncident.id}] ${currentIncident.type} - ${currentIncident.vehicle} on ${currentIncident.lane} Corridor at ${currentIncident.timestamp}. Action: ${currentIncident.action}`;
    navigator.clipboard?.writeText(text);
    toast.success('Incident details copied to clipboard');
  };

  return (
    <>
      {/* ── Floating Real-Time Incident Ticker ──────────────── */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mb-4 w-full"
      >
        <div className="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl bg-slate-900/90 dark:bg-dark-900/90 backdrop-blur-xl border border-rose-500/20 shadow-lg text-xs">
          <div className="flex items-center gap-2.5 min-w-0">
            <span className="flex h-2 w-2 relative shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500" />
            </span>
            <div className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider border shrink-0 ${currentIncident.color}`}>
              {currentIncident.type}
            </div>
            <p className="text-slate-200 truncate font-medium">
              <strong className="text-white font-mono">{currentIncident.vehicle}</strong> on <span className="text-amber-400">{currentIncident.lane} Lane</span> {currentIncident.speed ? `(${currentIncident.speed})` : ''}
            </p>
            <span className="text-slate-500 font-mono text-[10px] hidden sm:inline shrink-0">
              {currentIncident.timestamp}
            </span>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={() => setModalIncident(currentIncident)}
              className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/15 text-slate-200 font-semibold text-[11px] transition-all flex items-center gap-1"
            >
              <span>Inspect</span>
              <ExternalLink size={11} className="text-slate-400" />
            </button>
            <button
              onClick={() => setIsDismissed(true)}
              aria-label="Dismiss incident ticker"
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* ── Incident Detail Inspection Modal ────────────────── */}
      <AnimatePresence>
        {modalIncident && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setModalIncident(null)}
              className="fixed inset-0 bg-black/60 backdrop-blur-md"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-md rounded-2xl bg-white dark:bg-[#0f1523] border border-slate-200 dark:border-white/10 p-6 shadow-2xl z-10 space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <div className={`p-2 rounded-xl border ${modalIncident.color}`}>
                    <Icon size={18} />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                      Incident #{modalIncident.id.toString().slice(-6)}
                    </span>
                    <h3 className="font-display font-bold text-base text-slate-900 dark:text-white">
                      {modalIncident.type}
                    </h3>
                  </div>
                </div>
                <button
                  onClick={() => setModalIncident(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-2 text-xs font-mono bg-slate-50 dark:bg-dark-850/80 p-3.5 rounded-xl border border-slate-200/60 dark:border-white/[0.06]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Junction:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{trafficData.junction || 'Silk Board, Bengaluru'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Corridor Approach:</span>
                  <span className="font-bold text-amber-500">{modalIncident.lane} Lane</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Target Vehicle:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{modalIncident.vehicle}</span>
                </div>
                {modalIncident.speed && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Recorded Velocity:</span>
                    <span className="font-bold text-rose-400">{modalIncident.speed} (Limit: {modalIncident.speedLimit})</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-400">Time Registered:</span>
                  <span className="text-slate-600 dark:text-slate-300">{modalIncident.timestamp}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Enforcement Tier:</span>
                  <span className="font-bold text-rose-500">{modalIncident.severity}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
                <span className="font-bold text-amber-500 block uppercase text-[10px] tracking-wider mb-1">
                  Automated Recommendation:
                </span>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  {modalIncident.action}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => audioTelemetry.playViolationAlert()}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 flex items-center gap-1.5 transition-all"
                >
                  <Volume2 size={14} className="text-amber-500" />
                  Replay Alert
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={copyIncidentData}
                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/15 text-slate-700 dark:text-slate-200 flex items-center gap-1.5 transition-all"
                  >
                    <Copy size={13} />
                    Copy
                  </button>
                  <button
                    onClick={() => {
                      toast.success('Incident dispatched to Silk Board Traffic Division');
                      setModalIncident(null);
                    }}
                    className="btn-primary !px-4 !py-1.5 !text-xs"
                  >
                    Dispatch Action
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
