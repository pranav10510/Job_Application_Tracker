import React from 'react'

function statusColor(status) {
  const colors = {
    Applied: 'bg-blue-500 text-white',
    Interview: 'bg-green-500 text-white', 
    Offer: 'bg-purple-500 text-white',
    Rejected: 'bg-red-500 text-white'
  }
  return colors[status] || 'bg-gray-500 text-white'
}

export default function SimpleJobCard({ job, onEdit }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-1">{job.company}</h3>
          <p className="text-gray-600 font-medium">{job.role}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColor(job.status)}`}>
          {job.status}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
          <span>📅</span>
          <span>{new Date(job.date_applied).toLocaleDateString()}</span>
        </div>
        
        <div className="bg-gray-50 p-3 rounded text-sm text-gray-700">
          {job.email_subject}
        </div>
      </div>

      {job.notes && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 mb-4">
          <p className="text-blue-800 text-sm">{job.notes}</p>
        </div>
      )}

      <button
        onClick={onEdit}
        className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors"
      >
        Edit Details
      </button>
    </div>
  )
}