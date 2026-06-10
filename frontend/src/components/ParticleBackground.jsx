import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function ParticleBackground() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-100" />

      {/* Mouse Follow Glow */}
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full bg-brand-500/15 blur-[160px] dark:bg-brand-500/20"
        animate={{
          x: mousePosition.x - 300,
          y: mousePosition.y - 300,
        }}
        transition={{ type: 'tween', ease: 'backOut', duration: 1 }}
      />

      {/* Cinematic aurora blobs */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 2 }}
        className="absolute -top-[20%] -left-[10%] w-[55%] h-[55%] rounded-full bg-gradient-radial from-brand-500/15 via-brand-600/5 to-transparent blur-[140px] animate-pulse-glow dark:from-brand-500/15" 
      />
      <motion.div 
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 2.5, delay: 0.5 }}
        className="absolute -bottom-[15%] -right-[10%] w-[50%] h-[50%] rounded-full bg-gradient-radial from-indigo-500/15 via-purple-600/5 to-transparent blur-[120px] animate-pulse-glow dark:from-indigo-500/15"
      />
      
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[600px] max-h-[600px] rounded-full bg-brand-500/20 dark:bg-brand-500/30 blur-[120px] mix-blend-multiply dark:mix-blend-screen animate-float-orb-1" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[45vw] h-[45vw] max-w-[500px] max-h-[500px] rounded-full bg-indigo-500/20 dark:bg-indigo-500/30 blur-[120px] mix-blend-multiply dark:mix-blend-screen animate-float-orb-2" />
      <div className="absolute top-[40%] right-[20%] w-[35vw] h-[35vw] max-w-[400px] max-h-[400px] rounded-full bg-rose-500/10 dark:bg-rose-500/20 blur-[120px] mix-blend-multiply dark:mix-blend-screen animate-float-orb-1" style={{ animationDelay: '-5s' }} />

      {/* Subtle noise overlay */}
      <div 
        className="absolute inset-0 opacity-[0.02] dark:opacity-[0.05]"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")" }} 
      />

      {/* Cinematic Vignette */}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_40%,rgba(248,250,252,0.4)_100%)] dark:bg-[radial-gradient(circle_at_center,transparent_40%,rgba(9,13,24,0.85)_100%)]" />
    </div>
  );
}
