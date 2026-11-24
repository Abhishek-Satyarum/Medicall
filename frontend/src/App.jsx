
import { Activity, HeartPulse } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-10 text-center max-w-md w-full">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50">
          <HeartPulse className="h-9 w-9 text-emerald-600" />
        </div>

        <h1 className="text-4xl font-bold tracking-tight text-slate-900">
          Medicall
        </h1>

        <p className="mt-3 text-slate-500">
          AI-powered voice receptionist for healthcare.
        </p>

        <div className="mt-7 inline-flex items-center gap-2 rounded-full bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700">
          <Activity size={16} />
          Frontend initialized successfully
        </div>
      </div>
    </div>
  )
}

export default App
