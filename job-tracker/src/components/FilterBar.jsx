import React, { useState } from 'react'
import { motion } from 'framer-motion'

export default function FilterBar({ current, onChange, onRefresh, searchTerm, onSearchChange }) {
  const [sortBy, setSortBy] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')
  const buttons = ['all', 'Applied', 'Interview', 'Offer', 'Rejected']
  
  const statusIcons = {
    all: '📋',
    Applied: '📝',
    Interview: '🎯', 
    Offer: '🎉',
    Rejected: '❌'
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            type="text"
            placeholder="Search companies, roles, or notes..."
            value={searchTerm || ''}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white/90 backdrop-blur-sm border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          />
        </div>
        
        <motion.button 
          onClick={onRefresh}
          className="btn-secondary px-4 py-2 rounded-lg font-medium flex items-center gap-2"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Refresh
        </motion.button>
      </div>

      {/* Filter Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          {buttons.map((b, index) => (
            <motion.button 
              key={b}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onChange(b)}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                current === b 
                  ? 'btn-primary' 
                  : 'btn-secondary text-gray-700'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span>{statusIcons[b]}</span>
              {b === 'all' ? 'All' : b}
            </motion.button>
          ))}
        </div>

        {/* Sort Options */}
        <div className="flex items-center gap-2">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="btn-secondary px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="date">Sort by Date</option>
            <option value="company">Sort by Company</option>
            <option value="status">Sort by Status</option>
          </select>
          
          <motion.button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="btn-secondary p-2 rounded-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
          >
            <svg className={`w-4 h-4 transition-transform ${sortOrder === 'desc' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/>
            </svg>
          </motion.button>
        </div>
      </div>
    </div>
  )
}
