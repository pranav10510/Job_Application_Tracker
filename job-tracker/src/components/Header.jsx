import React from 'react'

export default function Header() {
  return (
    <header className="bg-white rounded-lg shadow-md p-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="text-4xl">🎯</div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Tracker AI</h1>
          <p className="text-gray-600">Intelligent job application tracking</p>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <button
          className="p-2 text-2xl hover:bg-gray-100 rounded-lg transition-colors"
          title="Dark Mode"
        >
          🌙
        </button>
        
        <button
          className="p-2 text-xl hover:bg-gray-100 rounded-lg transition-colors"
          title="Settings"
        >
          ⚙️
        </button>
      </div>
    </header>
  )
}
