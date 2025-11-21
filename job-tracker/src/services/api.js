import axios from 'axios'

export async function fetchJobs() {
  const res = await axios.get('/api/jobs')
  return res.data
}

export async function fetchStats() {
  const res = await axios.get('/api/stats')
  return res.data
}

export async function startScan(days_back) {
  const res = await axios.post('/api/scan', { days_back })
  return res.data
}

export async function fetchScanStatus() {
  const res = await axios.get('/api/scan/status')
  return res.data
}

export async function saveNotes(id, notes) {
  const res = await axios.post('/api/note', { id, notes })
  return res.data
}
