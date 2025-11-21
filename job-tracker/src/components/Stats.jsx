import React from 'react'
import { motion } from 'framer-motion'

function ProgressBar({ value, max, color, label }) {
  const percentage = max > 0 ? (value / max) * 100 : 0
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className="text-gray-800 font-bold">{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <motion.div 
          className={`h-2 rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
    </div>
  )
}

function DonutChart({ data, total }) {
  const colors = {
    Applied: '#3B82F6',
    Interview: '#10B981', 
    Offer: '#8B5CF6',
    Rejected: '#EF4444'
  }
  
  let currentAngle = 0
  const radius = 35
  const centerX = 50
  const centerY = 50
  
  return (
    <div className="relative">
      <svg viewBox="0 0 100 100" className="w-32 h-32 transform -rotate-90">
        {Object.entries(data).map(([status, count]) => {
          if (count === 0) return null
          
          const percentage = (count / total) * 100
          const angle = (percentage / 100) * 360
          const startAngle = currentAngle
          const endAngle = currentAngle + angle
          
          const startX = centerX + radius * Math.cos((startAngle * Math.PI) / 180)
          const startY = centerY + radius * Math.sin((startAngle * Math.PI) / 180)
          const endX = centerX + radius * Math.cos((endAngle * Math.PI) / 180)
          const endY = centerY + radius * Math.sin((endAngle * Math.PI) / 180)
          
          const largeArcFlag = angle > 180 ? 1 : 0
          
          const pathData = [
            `M ${centerX} ${centerY}`,
            `L ${startX} ${startY}`,
            `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endX} ${endY}`,
            'Z'
          ].join(' ')
          
          currentAngle += angle
          
          return (
            <motion.path
              key={status}
              d={pathData}
              fill={colors[status]}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: Object.keys(data).indexOf(status) * 0.1 }}
            />
          )
        })}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-800">{total}</div>
          <div className="text-xs text-gray-500">Total</div>
        </div>
      </div>
    </div>
  )
}

export default function Stats({ stats }) {
  const s = stats || { total: 0, status_counts: {} }
  const statusData = {
    Applied: s.status_counts.Applied || 0,
    Interview: s.status_counts.Interview || 0,
    Offer: s.status_counts.Offer || 0,
    Rejected: s.status_counts.Rejected || 0
  }

  const maxValue = Math.max(...Object.values(statusData))
  const successRate = s.total > 0 ? (((statusData.Offer + statusData.Interview) / s.total) * 100).toFixed(1) : 0

  return (
    <div className="space-y-6">
      {/* Main Stats Card */}
      <motion.div 
        className="glass-strong p-6 rounded-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gray-800">Application Stats</h3>
          <span className="text-2xl">📊</span>
        </div>
        
        <div className="flex items-center justify-center mb-6">
          <DonutChart data={statusData} total={s.total} />
        </div>

        <div className="space-y-3">
          <ProgressBar 
            value={statusData.Applied} 
            max={maxValue} 
            color="bg-blue-500" 
            label="Applied" 
          />
          <ProgressBar 
            value={statusData.Interview} 
            max={maxValue} 
            color="bg-green-500" 
            label="Interviews" 
          />
          <ProgressBar 
            value={statusData.Offer} 
            max={maxValue} 
            color="bg-purple-500" 
            label="Offers" 
          />
          {statusData.Rejected > 0 && (
            <ProgressBar 
              value={statusData.Rejected} 
              max={maxValue} 
              color="bg-red-500" 
              label="Rejected" 
            />
          )}
        </div>
      </motion.div>

      {/* Success Rate Card */}
      <motion.div 
        className="glass-strong p-6 rounded-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="text-center">
          <div className="text-3xl mb-2">🎯</div>
          <div className="text-2xl font-bold text-green-600">{successRate}%</div>
          <div className="text-sm text-gray-600">Success Rate</div>
          <div className="text-xs text-gray-500 mt-1">
            (Interviews + Offers)
          </div>
        </div>
      </motion.div>

      {/* Quick Insights */}
      <motion.div 
        className="glass-strong p-6 rounded-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <h4 className="font-semibold text-gray-800 mb-3">Quick Insights</h4>
        <div className="space-y-2 text-sm">
          {s.total === 0 && (
            <div className="text-gray-500">Start tracking your applications to see insights!</div>
          )}
          {s.total > 0 && statusData.Interview === 0 && (
            <div className="text-amber-600">💡 Consider following up on your applications</div>
          )}
          {statusData.Interview > 0 && statusData.Offer === 0 && (
            <div className="text-blue-600">🎯 Great job getting interviews! Keep it up</div>
          )}
          {statusData.Offer > 0 && (
            <div className="text-green-600">🎉 Congratulations on your offers!</div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
