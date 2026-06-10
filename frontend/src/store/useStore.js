import { create } from 'zustand';
import axios from 'axios';

// Self-sensing API URL resolver
const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

export const useStore = create((set, get) => ({
  // Theme State
  theme: 'dark',
  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    set({ theme });
  },
  toggleTheme: () => {
    const nextTheme = get().theme === 'light' ? 'dark' : 'light';
    get().setTheme(nextTheme);
  },

  // Traffic State
  systemStatus: 'ACTIVE',
  trafficData: {
    status: 'online',
    junction: 'Silk Board, Bengaluru',
    active_lane: '--',
    vehicle_counts: {
      North: 0,
      South: 0,
      East: 0,
      West: 0,
    },
    total_vehicles: 0,
    tracked_vehicles: 0,
    violations: 0,
  },
  signalData: {
    green_times: {
      North: 0,
      South: 0,
      East: 0,
      West: 0,
    },
    priority_lane: '--',
    cycle_time: 0,
  },

  // Vehicle Count Streaming History for Recharts
  history: [],

  // Fetch all traffic metrics from Flask API
  fetchTrafficData: async () => {
    try {
      const statusRes = await api.get('/status');
      const signalRes = await api.get('/signal');

      const trafficData = statusRes.data;
      const signalData = signalRes.data;

      // Update history stream (max 20 entries)
      const now = new Date().toLocaleTimeString('en-US', { hour12: false });
      const currentHistory = [...get().history];
      if (currentHistory.length >= 20) {
        currentHistory.shift();
      }
      currentHistory.push({
        time: now,
        vehicles: trafficData.total_vehicles,
      });

      set({
        trafficData,
        signalData,
        systemStatus: 'ACTIVE',
        history: currentHistory,
      });
    } catch (err) {
      console.error('Failed to sync traffic API:', err);
      set({ systemStatus: 'OFFLINE' });
    }
  },
}));
