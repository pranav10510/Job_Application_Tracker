import React, { useState } from 'react'
import { motion } from 'framer-motion'

function statusColor(status) {
  const map = {
    Applied: 'bg-blue-100 text-blue-800',
    Interview: 'bg-green-100 text-green-800',
    Offer: 'bg-purple-100 text-purple-800',
    Rejected: 'bg-red-100 text-red-800'
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

function statusIcon(status) {
  const icons = {
    Applied: '📝',
    Interview: '🎯',
    Offer: '🎉',
    Rejected: '❌'
  }
  return icons[status] || '📋'
}

export default function JobCard({ job, index = 0, onEdit }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className="glass-card rounded-xl p-6 hover:shadow-lg transition-all duration-300"
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold text-white">{job.company}</h3>
            <span className="text-lg">{statusIcon(job.status)}</span>
          </div>
          <p className="text-gray-200 font-medium">{job.role}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColor(job.status)}`}>
          {job.status}
        </span>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-center gap-2 text-gray-300">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3M3 11h18M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <span>{new Date(job.date_applied).toLocaleDateString('en-US', { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
          })}</span>
        </div>
        
        <motion.div 
          className="bg-white/10 p-3 rounded-lg backdrop-blur-sm cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
          whileHover={{ backgroundColor: 'rgba(255,255,255,0.15)' }}
        >
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-200 truncate flex-1">
              {job.email_subject}
            </span>
            <svg 
              className={`w-4 h-4 text-gray-300 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
          <motion.div
            initial={false}
            animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            {isExpanded && (
              <div className="mt-2 pt-2 border-t border-white/20 text-xs text-gray-300">
                Full email subject and additional details would appear here...
              </div>
            )}
          </motion.div>
        </motion.div>
      </div>

      {job.notes && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-blue-500/20 border border-blue-400/30 p-3 rounded-lg text-sm text-blue-100 mb-4"
        >
          <div className="flex items-center gap-2 mb-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
            </svg>
            <span className="font-medium">Notes</span>
          </div>
          {job.notes}
        </motion.div>
      )}

      <div className="flex gap-2">
        <motion.button 
          onClick={onEdit}
          className="flex-1 py-2 px-4 rounded-lg btn-primary text-white font-medium"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Edit Details
        </motion.button>
        <motion.button 
          className="p-2 rounded-lg btn-secondary text-gray-700"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
          </svg>
        </motion.button>
      </div>
    </motion.div>
  )
}
