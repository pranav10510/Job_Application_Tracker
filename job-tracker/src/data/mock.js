import axios from 'axios'

// Basic in-memory dataset
let jobs = [
  { id: 1, company: 'Acme Inc', role: 'Frontend Engineer', status: 'Applied', date_applied: '2025-11-01', email_subject: 'Application - Frontend Engineer', notes: 'Referred by Alice' },
  { id: 2, company: 'Nimbus', role: 'Data Analyst', status: 'Interview', date_applied: '2025-10-20', email_subject: 'Interview Invite', notes: '' },
  { id: 3, company: 'Helix', role: 'ML Engineer', status: 'Offer', date_applied: '2025-09-15', email_subject: 'Offer Letter', notes: 'Negotiation in progress' }
]

let stats = {
  total: jobs.length,
  status_counts: jobs.reduce((acc, j) => {
    acc[j.status] = (acc[j.status] || 0) + 1
    return acc
  }, {})
}

// tiny axios mock adaptor:
export function mockInit() {
  // attach routes at /__mock__/...
  axios.interceptors.request.use(config => {
    if (config.url && config.url.startsWith('/__mock__/')) {
      // build response ourselves
      const path = config.url.replace('/__mock__', '')
      if (path === '/jobs' && config.method === 'get') {
        return Promise.resolve({ data: jobs, status: 200, config })
      }
      if (path === '/stats' && config.method === 'get') {
        return Promise.resolve({ data: stats, status: 200, config })
      }
      if (path === '/scan' && config.method === 'post') {
        // simulate scan triggered: add one mock job after delay (but we won't actually wait here)
        const newJob = {
          id: Date.now(),
          company: 'Synth Systems',
          role: 'QA Engineer',
          status: 'Applied',
          date_applied: new Date().toISOString(),
          email_subject: 'New Application',
          notes: ''
        }
        jobs = [newJob, ...jobs]
        stats.total = jobs.length
        stats.status_counts = jobs.reduce((acc, j) => { acc[j.status] = (acc[j.status] || 0) + 1; return acc }, {})
        return Promise.resolve({ data: { ok: true }, status: 200, config })
      }
    }
    return config
  }, err => Promise.reject(err))

  // intercept axios responses: handle the fake-resolves above
  axios.interceptors.response.use(resp => {
    // if route returned a fake object as "resolve", axios expects a full response object already
    if ('data' in resp && resp.config && resp.config.url && resp.config.url.startsWith('/__mock__/')) {
      return resp
    }
    return resp
  }, err => Promise.reject(err))
}
