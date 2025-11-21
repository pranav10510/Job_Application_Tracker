import React from 'react'

export default function SimpleStats({ stats }) {
  const s = stats || { total: 0, status_counts: {} }
  const statusData = {
    Applied: s.status_counts.Applied || 0,
    Interview: s.status_counts.Interview || 0,
    Offer: s.status_counts.Offer || 0,
    Rejected: s.status_counts.Rejected || 0
  }

  const successRate = s.total > 0 ? (((statusData.Offer + statusData.Interview) / s.total) * 100).toFixed(1) : 0

  return (
    <div className="space-y-6">
      {/* Activity Feed */}
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3 text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>3 new applications scanned</span>
          </div>
          <div className="flex items-center gap-3 text-gray-600">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Interview scheduled with Google</span>
          </div>
          <div className="flex items-center gap-3 text-gray-600">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>Offer received from Meta</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="space-y-2">
          <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            📊 View Analytics
          </button>
          <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            📧 Scan Gmail
          </button>
          <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            📁 Export Data
          </button>
          <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            ⚙️ Settings
          </button>
        </div>
      </div>

      {/* Tips */}
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 mb-4">💡 Tips</h3>
        <div className="text-sm text-gray-600">
          {s.total === 0 && (
            <p>Start by scanning your Gmail for job applications!</p>
          )}
          {s.total > 0 && statusData.Interview === 0 && (
            <p>Consider following up on your applications to increase interview rates.</p>
          )}
          {statusData.Interview > 0 && statusData.Offer === 0 && (
            <p>Great interview progress! Keep preparing for your next rounds.</p>
          )}
          {statusData.Offer > 0 && (
            <p>🎉 Congratulations on your offers!</p>
          )}
        </div>
      </div>
    </div>
  )
}