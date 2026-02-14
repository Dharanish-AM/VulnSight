import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { api } from './api'

function App() {
  const [target, setTarget] = useState('')
  const [scanning, setScanning] = useState(false)
  const [scanId, setScanId] = useState(null)
  const [status, setStatus] = useState(null)
  const [results, setResults] = useState(null)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  const pollingRef = useRef(null)

  useEffect(() => {
    const savedTarget = localStorage.getItem('vulnsight_target')
    const savedScanId = localStorage.getItem('vulnsight_scanId')
    const savedMessages = localStorage.getItem('vulnsight_chatMessages')

    if (savedTarget) setTarget(savedTarget)
    if (savedScanId) {
      setScanId(savedScanId)
      recoverScan(savedScanId)
    }
    if (savedMessages) setChatMessages(JSON.parse(savedMessages))
  }, [])

  useEffect(() => {
    localStorage.setItem('vulnsight_target', target)
  }, [target])

  useEffect(() => {
    if (scanId) localStorage.setItem('vulnsight_scanId', scanId)
    else localStorage.removeItem('vulnsight_scanId')
  }, [scanId])

  useEffect(() => {
    localStorage.setItem('vulnsight_chatMessages', JSON.stringify(chatMessages))
  }, [chatMessages])

  const recoverScan = async (id) => {
    try {
      const { status } = await api.getStatus(id)
      setStatus(status)
      if (status === 'completed') {
        const report = await api.getReport(id)
        setResults(report)
      } else if (status === 'running' || status === 'queued') {
        setScanning(true)
        startPolling(id)
      }
    } catch (err) {
      console.error('Failed to recover scan:', err)
      setScanId(null)
    }
  }

  const handleScan = async () => {
    if (!target) return
    setScanning(true)
    setResults(null)
    setStatus('queued')
    setChatMessages([])
    try {
      const { scan_id } = await api.startScan(target)
      setScanId(scan_id)
      startPolling(scan_id)
    } catch (err) {
      console.error(err)
      setScanning(false)
      setStatus('failed')
    }
  }

  const startPolling = (id) => {
    if (pollingRef.current) clearInterval(pollingRef.current)

    pollingRef.current = setInterval(async () => {
      try {
        const { status } = await api.getStatus(id)
        setStatus(status)

        if (status === 'completed') {
          clearInterval(pollingRef.current)
          const report = await api.getReport(id)
          setResults(report)
          setScanning(false)
        } else if (status === 'failed') {
          clearInterval(pollingRef.current)
          setScanning(false)
        }
      } catch (err) {
        console.error(err)
        clearInterval(pollingRef.current)
        setScanning(false)
      }
    }, 2000)
  }

  const handleChat = async (e) => {
    e.preventDefault()
    if (!chatInput) return

    const newMessage = { role: 'user', content: chatInput }
    setChatMessages(prev => [...prev, newMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      const data = await api.askAI(chatInput, scanId)
      const aiResponse = `### ${data.Summary}\n\n**Attack Explanation:** ${data['Attack Explanation']}\n\n**Mitigation:** ${data.Mitigation}\n\n**References:**\n${data.References.map(r => `- [${r}](${r})`).join('\n')}`
      setChatMessages(prev => [...prev, { role: 'ai', content: aiResponse }])
    } catch (err) {
      console.error(err)
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="h-screen bg-[#050505] text-[#fcfcfc] flex flex-col font-sans selection:bg-blue-500/20 selection:text-blue-400 overflow-hidden">
      <header className="h-20 shrink-0 flex items-center px-8 justify-between z-50 sticky top-0 bg-[#050505]/80 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)]">
            <span className="font-bold text-lg">V</span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-semibold tracking-tight leading-none">VulnSight</h1>
            <span className="text-[10px] text-blue-500 font-medium tracking-[0.2em] uppercase mt-1">Intelligence System</span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full bg-emerald-500 ${scanning ? 'animate-pulse' : ''}`} />
            <span className="text-[10px] font-semibold text-emerald-500 uppercase tracking-wider">
              {scanning ? `Scanner: ${status.toUpperCase()}` : 'System Ready'}
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <main className="flex-1 overflow-y-auto p-12 custom-scrollbar space-y-16">
          <section className="max-w-2xl mx-auto w-full text-center space-y-8">
            <div className="space-y-3">
              <h2 className="text-4xl font-bold tracking-tight bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">Infrastructure Analysis</h2>
              <p className="text-white/40 text-sm font-medium tracking-wide">Enter target domain or IP for intelligence gathering</p>
            </div>

            <div className="glass rounded-[2rem] p-2 border-white/10 shadow-2xl group focus-within:border-blue-500/30 transition-all duration-500">
              <div className="flex items-center bg-white/5 rounded-[1.75rem] px-4">
                <input
                  type="text"
                  placeholder="Target domain or IP address..."
                  className="flex-1 bg-transparent border-none py-5 px-3 text-white placeholder-white/20 font-medium focus:ring-0"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleScan()}
                />
                <button
                  onClick={handleScan}
                  disabled={scanning}
                  className={`px-8 h-12 rounded-2xl font-bold text-sm transition-all duration-300 ${scanning
                    ? 'bg-white/5 text-white/20 cursor-not-allowed'
                    : 'bg-white text-black hover:bg-blue-600 hover:text-white shadow-xl active:scale-95'
                    }`}
                >
                  {scanning ? 'Scanning...' : 'Kickoff Scan'}
                </button>
              </div>
            </div>
          </section>

          <section className="max-w-6xl mx-auto w-full space-y-10 pb-20">
            {results && (
              <div className="space-y-12">
                <div className="flex items-baseline justify-between border-b border-white/5 pb-6">
                  <div>
                    <h3 className="text-2xl font-bold tracking-tight">Intelligence Report</h3>
                    <p className="text-xs text-white/30 font-medium uppercase tracking-widest mt-1">{results.target}</p>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-center px-4 border-r border-white/5">
                      <p className="text-[10px] text-white/20 font-bold uppercase tracking-widest">Findings</p>
                      <p className="text-lg font-bold">{results.vulnerabilities.length}</p>
                    </div>
                    <div className="text-center px-4">
                      <p className="text-[10px] text-white/20 font-bold uppercase tracking-widest">Paths</p>
                      <p className="text-lg font-bold">{results.attack_paths.length}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.vulnerabilities.map((vuln, i) => (
                    <div key={i} className="premium-card edge-shine rounded-[2rem] p-6 space-y-6">
                      <div className="flex justify-between items-start">
                        <div className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider ${vuln.severity === 'Critical' ? 'bg-red-500/10 text-red-500' :
                          vuln.severity === 'High' ? 'bg-orange-500/10 text-orange-500' :
                            'bg-yellow-500/10 text-yellow-500'
                          }`}>
                          {vuln.severity}
                        </div>
                        <span className="text-[10px] font-mono text-white/20">{vuln.cve_id}</span>
                      </div>

                      <div className="space-y-2">
                        <h4 className="text-lg font-bold tracking-tight leading-tight">{vuln.component}</h4>
                        <p className="text-xs text-white/40 leading-relaxed line-clamp-3">{vuln.description}</p>
                      </div>

                      <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                        <div className="flex flex-col">
                          <span className="text-[8px] font-bold text-white/20 uppercase">Tool Source</span>
                          <span className="text-[10px] font-bold text-blue-500">{vuln.source_tool}</span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[8px] font-bold text-white/20 uppercase">CVSS Score</span>
                          <span className="text-[10px] font-bold text-white">{vuln.cvss || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {results.attack_paths.length > 0 && (
                  <div className="space-y-6">
                    <h3 className="text-xl font-bold tracking-tight">Predicted Attack Chains</h3>
                    <div className="grid grid-cols-1 gap-4">
                      {results.attack_paths.map((path, idx) => (
                        <div key={idx} className="bg-white/5 border border-white/5 rounded-2xl p-6 flex items-center gap-6">
                          <div className="w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/20 text-blue-500 font-bold text-xs">
                            #{idx + 1}
                          </div>
                          <div className="flex-1 flex items-center gap-4 flex-wrap">
                            {path.map((node, nIdx) => (
                              <div key={nIdx} className="flex items-center gap-4">
                                <div className="px-4 py-2 bg-white/5 rounded-xl border border-white/10 text-[10px] font-bold uppercase tracking-wider">
                                  {node.split('_')[1]}
                                </div>
                                {nIdx < path.length - 1 && (
                                  <svg className="w-4 h-4 text-white/10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                  </svg>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!results && !scanning && (
              <div className="h-64 flex flex-col items-center justify-center text-center glass rounded-[3rem] border-white/5">
                <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-6">
                  <svg className="w-8 h-8 text-white/10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M12 11V3m0 8l-4-4m4 4l4-4M2 17l.621 2.485A2 2 0 004.561 21h14.878a2 2 0 001.94-1.515L22 17" />
                  </svg>
                </div>
                <h4 className="text-sm font-semibold text-white/40 uppercase tracking-[0.3em]">Awaiting Analysis</h4>
              </div>
            )}
          </section>
        </main>

        <aside className="w-[450px] bg-[#050505] border-l border-white/5 flex flex-col z-20">
          <div className="h-20 px-10 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.6)]" />
              <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/80">Neural Core</h3>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
            {chatMessages.length === 0 && (
              <div className="glass rounded-3xl p-6 border-white/5">
                <p className="text-sm text-white/60 leading-relaxed">
                  Bridge online. Use the input below to query information about the latest scan or general security remediation.
                </p>
              </div>
            )}

            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[90%] px-5 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white/5 text-white/80 border border-white/5'
                  }`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>

          <div className="p-8 border-t border-white/5">
            <form onSubmit={handleChat} className="bg-white/5 border border-white/10 rounded-2xl p-1.5 flex focus-within:border-blue-500/30 transition-all">
              <input
                type="text"
                placeholder="Talk to Neural Core..."
                className="flex-1 bg-transparent border-none text-sm px-4 py-3 text-white focus:ring-0"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button
                type="submit"
                className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
              </button>
            </form>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default App
