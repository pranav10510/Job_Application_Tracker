import React, { useState } from "react";
import { startScan as startScanBackend, fetchScanStatus } from "../services/api";

export default function SimpleScanPanel({ onScanComplete }) {
  const [running, setRunning] = useState(false);
  const [days, setDays] = useState(60);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");

  async function startScan() {
    setRunning(true);
    setProgress(0);
    setStatusMessage("Starting scan...");
    setError("");

    try {
      await startScanBackend(days);
      setStatusMessage("Scanning emails...");

      const poll = setInterval(async () => {
        try {
          const status = await fetchScanStatus();
          setProgress(status.progress || 0);
          setStatusMessage(status.message || "Processing...");

          if (!status.running) {
            clearInterval(poll);
            setStatusMessage("Scan completed!");
            onScanComplete();
            setRunning(false);
            setTimeout(() => setStatusMessage(""), 3000);
          }
        } catch (pollErr) {
          clearInterval(poll);
          setError("Error checking scan status");
          setRunning(false);
        }
      }, 1000);

    } catch (err) {
      setRunning(false);
      setError("Scan failed. Please try again.");
      setStatusMessage("");
    }
  }

  return (
    <div>

      <div className="flex gap-4 items-end mb-6">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scan Period
          </label>
          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            disabled={running}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value={5}>Last 5 days</option>
            <option value={30}>Last 30 days</option>
            <option value={60}>Last 60 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
        
        <button
          onClick={startScan}
          disabled={running}
          className={`btn-primary ${running ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {running ? `Scanning ${progress}%` : 'Start Scan'}
        </button>
      </div>

      {/* Progress Bar */}
      {running && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Status Messages */}
      {statusMessage && (
        <div className={`mt-4 p-3 rounded-lg text-sm ${
          running ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'
        }`}>
          {statusMessage}
        </div>
      )}

      {/* Error Messages */}
      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
          {error}
          <button 
            onClick={() => setError("")}
            className="ml-2 text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
}