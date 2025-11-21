import React, { useEffect, useState } from 'react'
import Header from './components/Header'
import SimpleStats from './components/SimpleStats'
import SimpleScanPanel from './components/SimpleScanPanel'
import SimpleFilterBar from './components/SimpleFilterBar'
import SimpleJobCard from './components/SimpleJobCard'
import JobModal from './components/JobModal'
import { fetchJobs, fetchStats } from './services/api'
import { mockInit } from './data/mock'

function App() {
  // initialize mock in dev
  // if (import.meta.env.MODE === 'development') {
  //   mockInit()
  // }

  const [jobs, setJobs] = useState([])
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [stats, setStats] = useState({ total: 0, status_counts: {} })
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingJob, setEditingJob] = useState(null)
  const [currentView, setCurrentView] = useState('dashboard')

  useEffect(() => {
    loadJobs()
    loadStats()
  }, [])

  async function loadJobs() {
    setLoading(true)
    try {
      const data = await fetchJobs()
      setJobs(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function loadStats() {
    try {
      const s = await fetchStats()
      setStats(s)
    } catch (err) {
      console.error(err)
    }
  }

  const handleEditJob = (job) => {
    setEditingJob(job)
    setIsModalOpen(true)
  }

  const handleAddJob = () => {
    setEditingJob(null)
    setIsModalOpen(true)
  }

  const handleSaveJob = async (jobData) => {
    try {
      // TODO: Implement API call to save job
      console.log('Saving job:', jobData)
      
      // For now, just refresh the data
      await loadJobs()
      await loadStats()
    } catch (err) {
      console.error('Error saving job:', err)
    }
  }

  const filteredJobs = jobs
    .filter(job => {
      const matchesStatus = filter === 'all' || job.status === filter
      const matchesSearch = !searchTerm || 
        job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (job.notes && job.notes.toLowerCase().includes(searchTerm.toLowerCase())) ||
        job.email_subject.toLowerCase().includes(searchTerm.toLowerCase())
      return matchesStatus && matchesSearch
    })

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 min-h-screen text-white p-6 sidebar">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center text-2xl">
              🎯
            </div>
            <div>
              <h1 className="text-2xl font-bold">Job Tracker</h1>
              <p className="text-base text-white/70">AI Powered</p>
            </div>
          </div>

          <nav className="space-y-3">
            <button 
              onClick={() => setCurrentView('dashboard')}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-colors text-lg ${
                currentView === 'dashboard' ? 'bg-white/20' : 'hover:bg-white/10'
              }`}
            >
              <span className="text-2xl">📊</span>
              <span className="font-medium">Dashboard</span>
            </button>
            <button 
              onClick={() => setCurrentView('applications')}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-colors text-lg ${
                currentView === 'applications' ? 'bg-white/20' : 'hover:bg-white/10'
              }`}
            >
              <span className="text-2xl">📝</span>
              <span className="font-medium">Applications</span>
            </button>
            <button 
              onClick={() => setCurrentView('analytics')}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-colors text-lg ${
                currentView === 'analytics' ? 'bg-white/20' : 'hover:bg-white/10'
              }`}
            >
              <span className="text-2xl">📈</span>
              <span className="font-medium">Analytics</span>
            </button>
            <button 
              onClick={() => setCurrentView('settings')}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-colors text-lg ${
                currentView === 'settings' ? 'bg-white/20' : 'hover:bg-white/10'
              }`}
            >
              <span className="text-2xl">⚙️</span>
              <span className="font-medium">Settings</span>
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">
                {currentView === 'dashboard' && 'Dashboard'}
                {currentView === 'applications' && 'All Applications'}
                {currentView === 'analytics' && 'Analytics'}
                {currentView === 'settings' && 'Settings'}
              </h1>
              <p className="text-lg text-gray-600 mt-2">
                {currentView === 'dashboard' && 'Track and manage your job applications'}
                {currentView === 'applications' && 'Manage all your job applications'}
                {currentView === 'analytics' && 'Analyze your job search performance'}
                {currentView === 'settings' && 'Configure your application preferences'}
              </p>
            </div>
            {currentView !== 'settings' && (
              <button
                onClick={handleAddJob}
                className="btn-primary flex items-center gap-3 text-lg px-6 py-3"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Add Application
              </button>
            )}
          </div>

          {/* Stats Cards - Show on Dashboard and Analytics */}
          {(currentView === 'dashboard' || currentView === 'analytics') && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="card p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-base font-medium text-gray-600">Total Applications</p>
                    <p className="text-4xl font-bold text-gray-900 mt-2">{stats.total || 0}</p>
                  </div>
                  <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center">
                    <span className="text-3xl">📋</span>
                  </div>
                </div>
              </div>
              
              <div className="card p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-base font-medium text-gray-600">Interviews</p>
                    <p className="text-4xl font-bold text-gray-900 mt-2">{stats.status_counts?.Interview || 0}</p>
                  </div>
                  <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center">
                    <span className="text-3xl">🎯</span>
                  </div>
                </div>
              </div>
              
              <div className="card p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-base font-medium text-gray-600">Offers</p>
                    <p className="text-4xl font-bold text-gray-900 mt-2">{stats.status_counts?.Offer || 0}</p>
                  </div>
                  <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center">
                    <span className="text-3xl">🎉</span>
                  </div>
                </div>
              </div>
              
              <div className="card p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-base font-medium text-gray-600">Success Rate</p>
                    <p className="text-4xl font-bold text-gray-900 mt-2">
                      {stats.total > 0 ? Math.round(((stats.status_counts?.Interview || 0) + (stats.status_counts?.Offer || 0)) / stats.total * 100) : 0}%
                    </p>
                  </div>
                  <div className="w-16 h-16 bg-yellow-100 rounded-xl flex items-center justify-center">
                    <span className="text-3xl">📈</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Dashboard View */}
          {currentView === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8">
                {/* Gmail Scanner */}
                <div className="card p-8">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">📧</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-semibold">Gmail Scanner</h2>
                      <p className="text-gray-600 text-base">Automatically detect job applications</p>
                    </div>
                  </div>
                  <SimpleScanPanel onScanComplete={() => { loadJobs(); loadStats(); }} />
                </div>

                {/* Recent Applications */}
                <div className="card p-8">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-semibold">Recent Applications</h2>
                    <SimpleFilterBar 
                      current={filter} 
                      onChange={setFilter} 
                      onRefresh={loadJobs}
                      searchTerm={searchTerm}
                      onSearchChange={setSearchTerm}
                    />
                  </div>
                  
                  <div className="space-y-4">
                    {loading ? (
                      <div className="flex items-center justify-center p-12">
                        <div className="text-center">
                          <div className="text-5xl mb-4">⏳</div>
                          <div className="text-gray-600 text-lg">Loading applications...</div>
                        </div>
                      </div>
                    ) : filteredJobs.length === 0 ? (
                      <div className="text-center p-12">
                        <div className="text-6xl mb-4">📭</div>
                        <div className="text-gray-900 font-semibold text-xl mb-2">No applications found</div>
                        <div className="text-gray-600 text-base">Try launching a scan or add applications manually</div>
                      </div>
                    ) : (
                      <div className="grid gap-4">
                        {filteredJobs.slice(0, 6).map((job) => (
                          <div key={job.id} className="border border-gray-200 rounded-lg p-6 hover:bg-gray-50 transition-colors">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="font-semibold text-gray-900 text-lg">{job.company}</h3>
                                  <span className={`px-3 py-1 text-sm font-medium rounded-full status-${job.status.toLowerCase()}`}>
                                    {job.status}
                                  </span>
                                </div>
                                <p className="text-gray-600 text-base mb-2">{job.role}</p>
                                <p className="text-gray-500 text-sm">
                                  Applied {new Date(job.date_applied).toLocaleDateString()}
                                </p>
                              </div>
                              <button
                                onClick={() => handleEditJob(job)}
                                className="text-gray-400 hover:text-gray-600 p-2"
                              >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                                </svg>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <SimpleStats stats={stats} />
              </div>
            </div>
          )}

          {/* Applications View */}
          {currentView === 'applications' && (
            <div className="space-y-6">
              <div className="card p-8">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-semibold">All Applications</h2>
                  <SimpleFilterBar 
                    current={filter} 
                    onChange={setFilter} 
                    onRefresh={loadJobs}
                    searchTerm={searchTerm}
                    onSearchChange={setSearchTerm}
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {loading ? (
                    <div className="col-span-full flex items-center justify-center p-12">
                      <div className="text-center">
                        <div className="text-5xl mb-4">⏳</div>
                        <div className="text-gray-600 text-lg">Loading applications...</div>
                      </div>
                    </div>
                  ) : filteredJobs.length === 0 ? (
                    <div className="col-span-full text-center p-12">
                      <div className="text-6xl mb-4">📭</div>
                      <div className="text-gray-900 font-semibold text-xl mb-2">No applications found</div>
                      <div className="text-gray-600 text-base">Try launching a scan or add applications manually</div>
                    </div>
                  ) : (
                    filteredJobs.map((job) => (
                      <SimpleJobCard 
                        key={job.id} 
                        job={job} 
                        onEdit={() => handleEditJob(job)}
                      />
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Analytics View */}
          {currentView === 'analytics' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="card p-8">
                  <h2 className="text-2xl font-semibold mb-6">Application Timeline</h2>
                  <div className="text-center p-12">
                    <div className="text-5xl mb-4">📊</div>
                    <div className="text-gray-900 font-semibold text-xl mb-2">Coming Soon</div>
                    <div className="text-gray-600 text-base">Advanced analytics and charts will be available here</div>
                  </div>
                </div>

                <div className="card p-8">
                  <h2 className="text-2xl font-semibold mb-6">Success Metrics</h2>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-3">
                      <span className="text-gray-600 text-base">Response Rate</span>
                      <span className="font-semibold text-lg">
                        {stats.total > 0 ? Math.round((stats.status_counts?.Interview || 0) / stats.total * 100) : 0}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-3">
                      <span className="text-gray-600 text-base">Interview Rate</span>
                      <span className="font-semibold text-lg">
                        {stats.total > 0 ? Math.round((stats.status_counts?.Interview || 0) / stats.total * 100) : 0}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-3">
                      <span className="text-gray-600 text-base">Offer Rate</span>
                      <span className="font-semibold text-lg">
                        {stats.total > 0 ? Math.round((stats.status_counts?.Offer || 0) / stats.total * 100) : 0}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Settings View */}
          {currentView === 'settings' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="card p-8">
                  <h2 className="text-2xl font-semibold mb-6">Application Settings</h2>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <label className="text-gray-900 font-medium text-base">Email Notifications</label>
                        <p className="text-gray-600 text-sm">Get notified about new applications</p>
                      </div>
                      <button className="w-12 h-6 bg-indigo-600 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <label className="text-gray-900 font-medium text-base">Auto Scan</label>
                        <p className="text-gray-600 text-sm">Automatically scan Gmail daily</p>
                      </div>
                      <button className="w-12 h-6 bg-gray-300 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5"></div>
                      </button>
                    </div>
                  </div>
                </div>

                <div className="card p-8">
                  <h2 className="text-2xl font-semibold mb-6">Data Management</h2>
                  <div className="space-y-4">
                    <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                      <div className="font-medium text-base text-gray-900">Export Data</div>
                      <div className="text-gray-600 text-sm">Download all your applications</div>
                    </button>
                    
                    <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                      <div className="font-medium text-base text-gray-900">Import Data</div>
                      <div className="text-gray-600 text-sm">Import from CSV or other sources</div>
                    </button>
                    
                    <button className="w-full text-left px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
                      <div className="font-medium text-base text-red-900">Clear All Data</div>
                      <div className="text-red-600 text-sm">Permanently delete all applications</div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <JobModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        job={editingJob}
        onSave={handleSaveJob}
      />
    </div>
  )
}

export default App
