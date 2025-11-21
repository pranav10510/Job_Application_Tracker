import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { startScan as startScanBackend, fetchScanStatus } from "../services/api";

export default function ScanPanel({ onScanComplete }) {
  const [running, setRunning] = useState(false);
  const [days, setDays] = useState(60);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function startScan() {
    setRunning(true);
    setProgress(0);
    setStatusMessage("Initializing scan...");
    setError("");
    setSuccess(false);

    try {
      // Start scan on backend
      await startScanBackend(days);
      setStatusMessage("Connecting to Gmail...");

      // Poll for status
      const poll = setInterval(async () => {
        try {
          const status = await fetchScanStatus();

          setProgress(status.progress || 0);
          setStatusMessage(status.message || "Processing emails...");

          if (!status.running) {
            clearInterval(poll);
            setSuccess(true);
            setStatusMessage("Scan completed successfully!");
            onScanComplete(); // tell parent to reload jobs/stats
            setRunning(false);
            
            // Clear success message after 3 seconds
            setTimeout(() => setSuccess(false), 3000);
          }
        } catch (pollErr) {
          console.error("Polling error:", pollErr);
          clearInterval(poll);
          setError("Error checking scan status");
          setRunning(false);
        }
      }, 1000);

    } catch (err) {
      console.error(err);
      setRunning(false);
      setError(err.message || "Scan failed. Please check your connection and try again.");
      setStatusMessage("");
    }
  }

  const scanOptions = [
    { value: 5, label: "Last 5 days", icon: "📅" },
    { value: 30, label: "Last 30 days", icon: "📆" },
    { value: 60, label: "Last 60 days", icon: "🗓️" },
    { value: 90, label: "Last 90 days", icon: "📊" }
  ];

  return (
    <motion.div 
      className="glass-strong rounded-xl p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-1">Gmail Scanner</h2>
          <p className="text-gray-600 text-sm">Automatically find job applications from your email</p>
        </div>
        <div className="text-3xl animate-float">📧</div>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Scan Period:
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {scanOptions.map((option) => (
            <motion.button
              key={option.value}
              onClick={() => setDays(option.value)}
              disabled={running}
              className={`p-3 rounded-lg border transition-all text-sm font-medium ${
                days === option.value
                  ? 'border-purple-500 bg-purple-50 text-purple-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-600'
              } ${running ? 'opacity-50 cursor-not-allowed' : ''}`}
              whileHover={{ scale: running ? 1 : 1.02 }}
              whileTap={{ scale: running ? 1 : 0.98 }}
            >
              <div className="text-lg mb-1">{option.icon}</div>
              {option.label}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <motion.button
          onClick={startScan}
          disabled={running}
          className={`w-full py-3 px-6 rounded-lg font-semibold transition-all ${
            running 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'btn-primary text-white hover:shadow-lg'
          }`}
          whileHover={{ scale: running ? 1 : 1.02 }}
          whileTap={{ scale: running ? 1 : 0.98 }}
        >
          {running ? (
            <div className="flex items-center justify-center gap-3">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full spinner"></div>
              <span>Scanning... {progress}%</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              Launch Scan
            </div>
          )}
        </motion.button>

        {/* Progress Bar */}
        <AnimatePresence>
          {running && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-2"
            >
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div 
                  className="progress-bar h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Status Messages */}
        <AnimatePresence>
          {statusMessage && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`p-3 rounded-lg text-sm ${
                success 
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : running
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'bg-gray-50 text-gray-600'
              }`}
            >
              <div className="flex items-center gap-2">
                {success && <span className="text-green-500">✅</span>}
                {running && !success && <div className="w-4 h-4 border-2 border-blue-400/30 border-t-blue-400 rounded-full spinner"></div>}
                <span>{statusMessage}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Messages */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-3 rounded-lg bg-red-50 text-red-700 border border-red-200 text-sm"
            >
              <div className="flex items-center gap-2">
                <span className="text-red-500">❌</span>
                <span>{error}</span>
                <button 
                  onClick={() => setError("")}
                  className="ml-auto text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
