/**
 * SoundManager - Client-side synthesizer for game sound effects using Web Audio API
 */
class SoundManager {
    constructor() {
        this.ctx = null;
        // Read initial mute state from localStorage
        this.muted = localStorage.getItem('sfx_muted') === 'true';
    }

    /**
     * Lazy initialize the AudioContext to comply with browser autoplay restrictions.
     */
    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    /**
     * Toggles the mute state and saves to localStorage
     * @returns {boolean} New mute state
     */
    toggleMute() {
        this.muted = !this.muted;
        localStorage.setItem('sfx_muted', this.muted);
        return this.muted;
    }

    /**
     * Check if SFX is currently muted
     * @returns {boolean}
     */
    isMuted() {
        return this.muted;
    }

    /**
     * Play a quick click/selection sound effect
     */
    playClick() {
        if (this.muted) return;
        this.init();

        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.type = 'sine';
            osc.frequency.setValueAtTime(800, this.ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(300, this.ctx.currentTime + 0.08);

            gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);

            osc.start();
            osc.stop(this.ctx.currentTime + 0.08);
        } catch (e) {
            console.warn('Failed to play SFX:', e);
        }
    }

    /**
     * Play battle anticipation tension sound effect (drum roll pattern)
     */
    playBattle() {
        if (this.muted) return;
        this.init();

        try {
            const duration = 0.55;
            const tickCount = 6;
            const interval = duration / tickCount;

            for (let i = 0; i < tickCount; i++) {
                const time = this.ctx.currentTime + i * interval;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.type = 'triangle';
                // Linearly increase frequency with each tick to build suspense
                const freq = 120 + (i * 20);
                osc.frequency.setValueAtTime(freq, time);
                osc.frequency.linearRampToValueAtTime(freq - 30, time + 0.05);

                gain.gain.setValueAtTime(0.15, time);
                gain.gain.linearRampToValueAtTime(0.001, time + 0.05);

                osc.start(time);
                osc.stop(time + 0.05);
            }
        } catch (e) {
            console.warn('Failed to play SFX:', e);
        }
    }

    /**
     * Play victory sound effect (Major chord arpeggio)
     */
    playWin() {
        if (this.muted) return;
        this.init();

        try {
            const now = this.ctx.currentTime;
            const notes = [
                { f: 523.25, d: 0.08 },  // C5
                { f: 659.25, d: 0.08 },  // E5
                { f: 783.99, d: 0.08 },  // G5
                { f: 1046.50, d: 0.35 }  // C6
            ];

            let start = now;
            notes.forEach((note) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.type = 'sine';
                osc.frequency.setValueAtTime(note.f, start);

                gain.gain.setValueAtTime(0, start);
                gain.gain.linearRampToValueAtTime(0.15, start + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.001, start + note.d);

                osc.start(start);
                osc.stop(start + note.d);

                start += note.d - 0.01;
            });
        } catch (e) {
            console.warn('Failed to play SFX:', e);
        }
    }

    /**
     * Play defeat sound effect (Minor/dissonant pitch decay)
     */
    playLose() {
        if (this.muted) return;
        this.init();

        try {
            const now = this.ctx.currentTime;
            const notes = [
                { f: 220.00, d: 0.15, type: 'sawtooth' }, // A3
                { f: 207.65, d: 0.15, type: 'sawtooth' }, // G#3
                { f: 196.00, d: 0.40, type: 'sawtooth' }  // G3
            ];

            let start = now;
            notes.forEach((note) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.type = note.type;
                osc.frequency.setValueAtTime(note.f, start);
                osc.frequency.linearRampToValueAtTime(note.f - 40, start + note.d);

                gain.gain.setValueAtTime(0.1, start);
                gain.gain.linearRampToValueAtTime(0.001, start + note.d);

                osc.start(start);
                osc.stop(start + note.d);

                start += note.d - 0.04;
            });
        } catch (e) {
            console.warn('Failed to play SFX:', e);
        }
    }

    /**
     * Play draw sound effect (Dual tone soft chimes)
     */
    playDraw() {
        if (this.muted) return;
        this.init();

        try {
            const now = this.ctx.currentTime;
            const notes = [
                { f: 392.00, d: 0.12 }, // G4
                { f: 493.88, d: 0.22 }  // B4
            ];

            let start = now;
            notes.forEach((note) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(note.f, start);

                gain.gain.setValueAtTime(0.12, start);
                gain.gain.exponentialRampToValueAtTime(0.001, start + note.d);

                osc.start(start);
                osc.stop(start + note.d);

                start += note.d + 0.05;
            });
        } catch (e) {
            console.warn('Failed to play SFX:', e);
        }
    }
}

// Global instance to be used across pages
window.soundManager = new SoundManager();
