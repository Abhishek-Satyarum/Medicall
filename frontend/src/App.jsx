import { useEffect, useRef, useState } from 'react'
import { BrowserRouter, NavLink, Navigate, Route, Routes } from 'react-router-dom'
import {
  Activity, CalendarDays, Clock3, HeartPulse, LayoutDashboard,
  Menu, Mic, MicOff, Phone, PhoneOff, Search, Stethoscope,
  UserRound, X, Users, CircleDollarSign, Bell,
} from 'lucide-react'
import { PipecatClient } from '@pipecat-ai/client-js'
import { SmallWebRTCTransport } from '@pipecat-ai/small-webrtc-transport'
import { getDashboardStats } from './services/dashboard'
import { cancelAppointment, getAppointments } from './services/appointments'
import { getDoctors, getSpecialties } from './services/doctors'
import { getAvailability } from './services/availability'

const navItems = [
  ['Overview', '/', LayoutDashboard],
  ['Appointments', '/appointments', CalendarDays],
  ['Doctors', '/doctors', Stethoscope],
  ['Availability', '/availability', Clock3],
  ['AI Receptionist', '/receptionist', Activity],
]

function Shell() {
  const [open, setOpen] = useState(false)
  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><HeartPulse size={21} /></div>
          <div><strong>Medicall</strong><span>AI healthcare reception</span></div>
          <button className="icon-btn close-menu" onClick={() => setOpen(false)}><X /></button>
        </div>
        <nav>
          {navItems.map(([label, to, Icon]) => (
            <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <Icon size={18} /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="admin-avatar">A</div>
          <div><strong>Administrator</strong><span>Clinic admin</span></div>
        </div>
      </aside>
      {open && <button className="overlay" aria-label="Close menu" onClick={() => setOpen(false)} />}
      <div className="main">
        <header className="topbar">
          <button className="icon-btn menu-btn" onClick={() => setOpen(true)}><Menu /></button>
          <div className="topbar-date">{new Intl.DateTimeFormat('en-IN', { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())}</div>
          <div className="topbar-actions"><button className="icon-btn" title="Notifications"><Bell size={19} /></button><div className="top-avatar">A</div></div>
        </header>
        <main className="content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/doctors" element={<Doctors />} />
            <Route path="/availability" element={<Availability />} />
            <Route path="/receptionist" element={<Receptionist />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function PageHeader({ title, subtitle, action }) {
  return <div className="page-header"><div><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action}</div>
}

function EmptyState({ text = 'No records found.' }) {
  return <div className="empty-state"><CalendarDays size={26} /><p>{text}</p></div>
}

function StatusBadge({ status }) {
  return <span className={`status-badge ${status === 'booked' ? 'booked' : 'cancelled'}`}>{status === 'booked' ? 'Booked' : 'Cancelled'}</span>
}

function Overview() {
  const [stats, setStats] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [error, setError] = useState('')
  useEffect(() => {
    Promise.all([getDashboardStats(), getAppointments()])
      .then(([s, a]) => { setStats(s); setAppointments(a) })
      .catch(() => setError('Unable to load dashboard data.'))
  }, [])
  const upcoming = appointments.filter(a => a.status === 'booked').slice(0, 5)
  const cards = [
    ['Total Doctors', stats?.total_doctors, Users, 'teal'],
    ['Total Appointments', stats?.total_appointments, CalendarDays, 'blue'],
    ['Upcoming', stats?.upcoming_appointments, Clock3, 'green'],
    ['Cancelled', stats?.cancelled_appointments, X, 'red'],
  ]
  return (
    <div>
      <PageHeader title="Overview" subtitle="Clinic operations at a glance" />
      {error && <div className="error-banner">{error}</div>}
      <div className="stat-grid">{cards.map(([label, value, Icon, tone]) =>
        <div className="stat-card" key={label}><div className={`stat-icon ${tone}`}><Icon size={20} /></div><div><span>{label}</span><strong>{value ?? '—'}</strong></div></div>
      )}</div>
      <section className="panel"><div className="panel-header"><div><h2>Upcoming appointments</h2><p>Next scheduled patient visits</p></div></div>
        {upcoming.length ? <div className="table-wrap"><table><thead><tr><th>Patient</th><th>Doctor</th><th>Date & time</th><th>Status</th></tr></thead><tbody>{upcoming.map(a =>
          <tr key={a.id}><td><strong>{a.patient_name}</strong><small>{a.patient_phone_number}</small></td><td>{a.doctor_name}<small>{a.specialty}</small></td><td>{a.slot_date}<small>{formatTime(a.start_time)} – {formatTime(a.end_time)}</small></td><td><StatusBadge status={a.status} /></td></tr>
        )}</tbody></table></div> : <EmptyState text="No upcoming appointments." />}
      </section>
    </div>
  )
}

function Appointments() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [date, setDate] = useState('')
  const [error, setError] = useState('')
  const load = async () => {
    setLoading(true)
    try { setItems(await getAppointments({ status: status || undefined, appointment_date: date || undefined })) }
    catch { setError('Unable to load appointments.') }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [status, date])
  const cancel = async (appointment) => {
    if (!window.confirm(`Cancel appointment #${appointment.id} for ${appointment.patient_name}?`)) return
    try {
      await cancelAppointment(appointment.id, appointment.patient_phone_number)
      await load()
    } catch (e) { setError(e.response?.data?.detail || 'Cancellation could not be completed.') }
  }
  const filtered = items.filter(a => `${a.patient_name} ${a.patient_phone_number}`.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => `${a.slot_date}${a.start_time}`.localeCompare(`${b.slot_date}${b.start_time}`))
  return (
    <div>
      <PageHeader title="Appointments" subtitle="Search, filter and manage patient visits" />
      {error && <div className="error-banner">{error}</div>}
      <div className="toolbar">
        <label className="search-box"><Search size={18} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search patient or phone" /></label>
        <select value={status} onChange={e => setStatus(e.target.value)}><option value="">All statuses</option><option value="booked">Booked</option><option value="cancelled">Cancelled</option></select>
        <input type="date" value={date} onChange={e => setDate(e.target.value)} />
      </div>
      <section className="panel">
        {loading ? <div className="loading">Loading appointments…</div> : filtered.length ? <div className="table-wrap"><table><thead><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date & time</th><th>Fee</th><th>Status</th><th></th></tr></thead><tbody>{filtered.map(a =>
          <tr key={a.id}><td># {a.id}</td><td><strong>{a.patient_name}</strong><small>{a.patient_phone_number}</small></td><td>{a.doctor_name}<small>{a.specialty}</small></td><td>{a.slot_date}<small>{formatTime(a.start_time)} – {formatTime(a.end_time)}</small></td><td>₹{a.consultation_fee}</td><td><StatusBadge status={a.status} /></td><td>{a.status === 'booked' && <button className="danger-btn" onClick={() => cancel(a)}>Cancel</button>}</td></tr>
        )}</tbody></table></div> : <EmptyState text="No appointments match the selected filters." />}
      </section>
    </div>
  )
}

function Doctors() {
  const [doctors, setDoctors] = useState([])
  const [specialties, setSpecialties] = useState([])
  const [search, setSearch] = useState('')
  const [specialty, setSpecialty] = useState('')
  useEffect(() => { Promise.all([getDoctors(), getSpecialties()]).then(([d, s]) => { setDoctors(d); setSpecialties(s) }).catch(() => {}) }, [])
  const filtered = doctors.filter(d => d.name.toLowerCase().includes(search.toLowerCase()) && (!specialty || d.specialty.name === specialty))
  return (
    <div>
      <PageHeader title="Doctors" subtitle="Manage clinic doctors and consultation schedules" />
      <div className="toolbar"><label className="search-box"><Search size={18} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search doctors" /></label><select value={specialty} onChange={e => setSpecialty(e.target.value)}><option value="">All specialties</option>{specialties.map(s => <option key={s.id}>{s.name}</option>)}</select></div>
      <div className="doctor-grid">{filtered.map(d => <article className="doctor-card" key={d.id}><div className="doctor-avatar">{initials(d.name)}</div><div className="doctor-main"><div><h3>{d.name}</h3><span className="status-dot">{d.is_active ? 'Active' : 'Inactive'}</span></div><p>{d.specialty.name}</p><div className="doctor-meta"><span><CircleDollarSign size={16} /> ₹{d.consultation_fee} consultation</span></div></div></article>)}</div>
      {!filtered.length && <EmptyState text="No doctors match your search." />}
    </div>
  )
}

function Availability() {
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [doctorId, setDoctorId] = useState('')
  const [doctors, setDoctors] = useState([])
  const [slots, setSlots] = useState([])
  const [specialty, setSpecialty] = useState('')
  const [specialties, setSpecialties] = useState([])
  useEffect(() => { Promise.all([getDoctors(), getSpecialties()]).then(([d, s]) => { setDoctors(d); setSpecialties(s) }).catch(() => {}) }, [])
  useEffect(() => { getAvailability(date, doctorId).then(setSlots).catch(() => setSlots([])) }, [date, doctorId])
  const filtered = slots.filter(slot => !specialty || doctors.find(d => d.id === slot.doctor_id)?.specialty.name === specialty)
  return (
    <div>
      <PageHeader title="Availability" subtitle="View real-time appointment slots" />
      <div className="toolbar"><input type="date" value={date} onChange={e => setDate(e.target.value)} /><select value={specialty} onChange={e => setSpecialty(e.target.value)}><option value="">All specialties</option>{specialties.map(s => <option key={s.id}>{s.name}</option>)}</select><select value={doctorId} onChange={e => setDoctorId(e.target.value)}><option value="">All doctors</option>{doctors.map(d => <option value={d.id} key={d.id}>{d.name}</option>)}</select></div>
      <section className="panel"><div className="slot-grid">{filtered.map(slot => { const doctor = doctors.find(d => d.id === slot.doctor_id); return <div className="slot-card" key={slot.id}><div><strong>{doctor?.name || 'Doctor'}</strong><span>{doctor?.specialty.name}</span></div><div className="slot-time"><Clock3 size={16} />{formatTime(slot.start_time)} – {formatTime(slot.end_time)}</div><div className="slot-footer"><span>₹{doctor?.consultation_fee}</span><span className="status-badge booked">Available</span></div></div> })}</div>{!filtered.length && <EmptyState text="No available slots for this selection." />}</section>
    </div>
  )
}

function Receptionist() {
  const [status, setStatus] = useState('idle')
  const [messages, setMessages] = useState([])
  const [muted, setMuted] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [error, setError] = useState('')
  const [audioBlocked, setAudioBlocked] = useState(false)
  const clientRef = useRef(null)
  const timerRef = useRef(null)
  const transcriptRef = useRef(null)
  const audioRef = useRef(null)
  const remoteAudioStreamRef = useRef(null)

  const releaseRemoteAudio = () => {
    const audio = audioRef.current
    if (audio) {
      audio.pause()
      audio.srcObject = null
    }
    remoteAudioStreamRef.current?.getTracks().forEach(track => track.stop())
    remoteAudioStreamRef.current = null
  }

  const playRemoteAudio = async () => {
    const audio = audioRef.current
    if (!audio || !audio.srcObject) return
    audio.muted = false
    audio.volume = 1
    try {
      await audio.play()
      console.info('Medicall remote audio playback started')
      setAudioBlocked(false)
    } catch (playError) {
      console.error('Medicall remote audio playback error', playError)
      setAudioBlocked(true)
    }
  }

  useEffect(() => () => {
    clearInterval(timerRef.current)
    const client = clientRef.current
    clientRef.current = null
    releaseRemoteAudio()
    if (client) {
      client.disconnect().catch(disconnectError => {
        console.error('Error disconnecting the Medicall voice client', disconnectError)
      })
    }
  }, [])
  useEffect(() => { transcriptRef.current?.scrollTo({ top: transcriptRef.current.scrollHeight }) }, [messages])
  useEffect(() => {
    if (status !== 'connected') return
    timerRef.current = setInterval(() => setSeconds(s => s + 1), 1000)
    return () => clearInterval(timerRef.current)
  }, [status])

  const startCall = async () => {
    if (clientRef.current) return
    setError('')
    setMessages([])
    setSeconds(0)
    setMuted(false)
    setAudioBlocked(false)
    releaseRemoteAudio()
    setStatus('connecting')
    let client
    try {
      client = new PipecatClient({
        transport: new SmallWebRTCTransport(),
        enableCam: false,
        enableMic: true,
        callbacks: {
          onConnected: () => setStatus('connected'),
          onDisconnected: () => setStatus('ended'),
          onTransportStateChanged: (state) => {
            if (state === 'error') setStatus('error')
            if (state === 'reconnecting') setStatus('reconnecting')
          },
          onTrackStarted: (track, participant) => {
            if (track.kind !== 'audio' || participant?.local) return
            console.info('Medicall remote audio track received', {
              id: track.id,
              readyState: track.readyState,
              muted: track.muted,
            })
            const stream = new MediaStream([track])
            remoteAudioStreamRef.current = stream
            const audio = audioRef.current
            if (!audio) {
              console.error('Medicall audio element is unavailable for the remote track')
              return
            }
            audio.srcObject = stream
            audio.muted = false
            audio.volume = 1
            console.info('Medicall remote audio stream attached to audio element')
            void playRemoteAudio()
          },
          onTrackStopped: (track, participant) => {
            if (track.kind !== 'audio' || participant?.local) return
            console.info('Medicall remote audio track stopped', {
              id: track.id,
              readyState: track.readyState,
            })
            if (track.readyState === 'ended' && remoteAudioStreamRef.current?.getTracks().some(item => item.id === track.id)) {
              releaseRemoteAudio()
            }
          },
          onUserTranscript: (data) => addMessage('patient', data.text, data.final),
          onBotTranscript: (data) => addMessage('medicall', data.text, true),
        },
      })
      clientRef.current = client
      await client.connect({
        connection_url: import.meta.env.VITE_PIPECAT_CONNECTION_URL || 'http://localhost:7860/api/offer',
      })
    } catch (e) {
      if (client) {
        try {
          await client.disconnect()
        } catch (disconnectError) {
          console.error('Error cleaning up the failed Medicall call', disconnectError)
        }
      }
      releaseRemoteAudio()
      setStatus('error')
      setError(e?.message?.includes('Permission') ? 'Microphone permission is required to start the call.' : 'Could not connect to the Medicall voice service. Ensure the Pipecat bot is running.')
      clientRef.current = null
    }
  }

  const addMessage = (speaker, text, final) => {
    if (!text) return
    setMessages(prev => {
      if (!final) {
        const last = prev[prev.length - 1]
        if (last?.speaker === speaker && last.partial) return [...prev.slice(0, -1), { speaker, text, partial: true, time: nowTime() }]
      }
      if (final) {
        const last = prev[prev.length - 1]
        if (last?.speaker === speaker && last.partial) return [...prev.slice(0, -1), { speaker, text, time: nowTime() }]
        if (last?.speaker === speaker && last.text === text) return prev
      }
      return [...prev, { speaker, text, time: nowTime(), ...(final ? {} : { partial: true }) }]
    })
  }

  const endCall = async () => {
    clearInterval(timerRef.current)
    const client = clientRef.current
    clientRef.current = null
    try {
      if (client) await client.disconnect()
    } catch (disconnectError) {
      console.error('Error ending the Medicall voice call', disconnectError)
      setError('The call ended, but the voice connection did not shut down cleanly.')
    } finally {
      releaseRemoteAudio()
      setAudioBlocked(false)
      setStatus('ended')
    }
  }

  const toggleMute = () => {
    if (!clientRef.current) return
    const next = !muted
    clientRef.current.enableMic(!next)
    setMuted(next)
  }

  return (
    <div>
      <PageHeader title="AI Receptionist" subtitle="Live voice appointments and patient support" />
      <div className="receptionist-grid">
        <section className="call-panel">
          <div className="call-orbit"><div className={`pulse-ring ${status === 'connected' ? 'active' : ''}`}><div className="call-avatar"><HeartPulse size={34} /></div></div></div>
          <h2>Medicall Assistant</h2><p className="call-status"><span className={`live-dot ${status}`} />{statusLabel(status)}</p>
          {status === 'connected' && <div className="call-duration">{formatDuration(seconds)}</div>}
          {error && <div className="call-error">{error}</div>}
          <div className="call-controls">
            {(status === 'idle' || status === 'ended' || status === 'error') && <button className="call-start" onClick={startCall}><Phone size={20} /> Start call</button>}
            {(status === 'connecting' || status === 'connected' || status === 'reconnecting') && <>
              <button className={`call-control ${muted ? 'muted' : ''}`} onClick={toggleMute} title={muted ? 'Unmute' : 'Mute'}>{muted ? <MicOff /> : <Mic />}</button>
              <button className="call-end" onClick={endCall}><PhoneOff /></button>
            </>}
          </div>
          {audioBlocked && <div className="audio-help"><p>Browser playback was blocked. Enable audio to hear Medicall.</p><button className="enable-audio" onClick={() => void playRemoteAudio()}>Enable audio</button></div>}
          <p className="permission-note">The browser will ask for microphone access before connecting.</p>
        </section>
        <section className="transcript-panel"><div className="panel-header"><div><h2>Live transcript</h2><p>Real-time conversation</p></div></div><div className="transcript" ref={transcriptRef}>
          {!messages.length && <div className="transcript-empty"><UserRound size={28} /><p>Conversation messages will appear here after the call connects.</p></div>}
          {messages.map((m, i) => <div className={`message ${m.speaker}`} key={i}><div className="message-avatar">{m.speaker === 'patient' ? 'P' : 'M'}</div><div><div className="message-meta\"><strong>{m.speaker === 'patient' ? 'Patient' : 'Medicall'}</strong><span>{m.time}</span></div><p>{m.text}</p></div></div>)}
        </div></section>
      </div>
      <audio ref={audioRef} autoPlay playsInline onError={event => {
        console.error('Medicall audio element playback error', event.currentTarget.error)
        setAudioBlocked(true)
      }} />
    </div>
  )
}

function formatTime(value) {
  if (!value) return ''
  const [h, m] = value.slice(0, 5).split(':').map(Number)
  return `${h % 12 || 12}:${String(m).padStart(2, '0')} ${h >= 12 ? 'PM' : 'AM'}`
}
function formatDuration(s) { return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}` }
function initials(name) { return name.replace(/^Dr\.?\s*/, '').split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase() }
function nowTime() { return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
function statusLabel(status) { return ({ idle: 'Idle', connecting: 'Connecting', connected: 'Connected', reconnecting: 'Reconnecting', ended: 'Call ended', error: 'Connection error' })[status] || status }

export default function App() {
  return <BrowserRouter><Shell /></BrowserRouter>
}
