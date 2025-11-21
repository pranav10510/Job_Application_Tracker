import React from 'react'

export default function SimpleFilterBar({ current, onChange, onRefresh, searchTerm, onSearchChange }) {
  const buttons = ['all', 'Applied', 'Interview', 'Offer', 'Rejected']
  
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
      {/* Search */}
      <div className="flex-1 min-w-0">
        <input
          type="text"
          placeholder="Search applications..."
          value={searchTerm || ''}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full px-4 py-2.5 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-1 flex-wrap">
        {buttons.map(status => (
          <button 
            key={status}
            onClick={() => onChange(status)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              current === status 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {status === 'all' ? 'All' : status}
          </button>
        ))}
      </div>
    </div>
  )
}