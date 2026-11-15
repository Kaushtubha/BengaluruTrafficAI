/**
 * Web Audio API synthesizer for junction telemetry, radar sonar, and incident chimes.
 * Operates purely via Web Audio oscillator synthesis (no external MP3/WAV assets).
 */

class AudioTelemetryService {
  constructor() {
    this.ctx = null;
    this.enabled = typeof window !== 'undefined'
      ? localStorage.getItem('blr_audio_telemetry') === 'true'
      : false;
  }

  _initContext() {
    if (typeof window === 'undefined') return false;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return Boolean(this.ctx);
  }

  setEnabled(enabled) {
    this.enabled = Boolean(enabled);
    if (typeof window !== 'undefined') {
      localStorage.setItem('blr_audio_telemetry', String(this.enabled));
    }
    if (this.enabled) {
      this._initContext();
      this.playSuccessBeep();
    }
  }

  toggle() {
    this.setEnabled(!this.enabled);
    return this.enabled;
  }

  isEnabled() {
    return this.enabled;
  }

  /**
   * Subtle radar sonar ping for vehicle detection / radar sweep
   */
  playSonarPing(freq = 640) {
    if (!this.enabled || !this._initContext()) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(freq * 1.5, now + 0.12);

      gain.gain.setValueAtTime(0.04, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.25);
    } catch {
      // Audio safety fallback
    }
  }

  /**
   * Double-tone alert chime for emergency priority preemption
   */
  playEmergencyChime() {
    if (!this.enabled || !this._initContext()) return;
    try {
      const now = this.ctx.currentTime;
      const playTone = (freq, start, duration) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.09, start);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(start);
        osc.stop(start + duration);
      };

      playTone(880, now, 0.18);
      playTone(1174, now + 0.16, 0.35);
    } catch {
      // Audio safety fallback
    }
  }

  /**
   * Attention chime for registered safety violations (Red light / wrong side)
   */
  playViolationAlert() {
    if (!this.enabled || !this._initContext()) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(320, now + 0.22);

      gain.gain.setValueAtTime(0.05, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.22);
    } catch {
      // Audio safety fallback
    }
  }

  /**
   * Soft affirmative tone for location found or telemetry refresh
   */
  playSuccessBeep() {
    if (!this.enabled || !this._initContext()) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.setValueAtTime(880.00, now + 0.08); // A5

      gain.gain.setValueAtTime(0.03, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.2);
    } catch {
      // Audio safety fallback
    }
  }
}

export const audioTelemetry = new AudioTelemetryService();

