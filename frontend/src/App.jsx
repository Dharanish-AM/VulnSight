import { useState, useEffect } from 'react'
import { api } from './api'

function App() {
  const [target, setTarget] = useState('')
  const [scanning, setScanning] = useState(false)
  const [results, setResults] = useState(null)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    loadLatestResults()
  }, [])

  const loadLatestResults = async () => {
    const data = await api.getLatestResults()
    if (data.results && data.results.length > 0) {
      setResults(data)
    }
  }

  const handleScan = async () => {
    if (!target) return
    setScanning(true)
    try {
      const data = await api.scan(target)
      setResults(data)
    } catch (err) {
      console.error(err)
    } finally {
      setScanning(false)
    }
  }

  const handleChat = async (e) => {
    e.preventDefault()
    if (!chatInput) return

    const newMessage = { role: 'user', content: chatInput }
    setChatMessages([...chatMessages, newMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      const data = await api.askAI(chatInput)
      setChatMessages(prev => [...prev, { role: 'ai', content: data.response }])
    } catch (err) {
      console.error(err)
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#010103] text-[#f8fafc] flex flex-col font-sans selection:bg-blue-500/10 selection:text-blue-400">
      {/* Immersive Foundation */}
      <div className="bg-mesh" />
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-15%] left-[-5%] w-[50%] h-[50%] bg-blue-600/[0.07] rounded-full blur-[140px]" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-emerald-500/[0.03] rounded-full blur-[120px]" />
      </div>

      {/* Machined Tactical Header */}
      <header className="h-20 flex items-center px-12 justify-between z-50 sticky top-0 backdrop-blur-xl border-b border-white/[0.02] bg-black/20">
        <div className="flex items-center space-x-5">
          <div className="relative group perspective-1000">
            <div className="absolute inset-0 bg-blue-500/30 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            <div className="relative w-11 h-11 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-900 flex items-center justify-center border border-white/10 shadow-2xl transition-transform duration-500 group-hover:rotate-[10deg]">
              <span className="font-black text-white text-2xl uppercase italic drop-shadow-lg">V</span>
            </div>
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-black tracking-[-0.05em] text-white uppercase italic leading-none">VulnSight.Core</h1>
            <div className="flex items-center space-x-2 mt-1.5">
              <span className="w-1 h-1 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-[10px] uppercase tracking-[0.4em] font-black text-white/20">A.I. Analysis Node 01</span>
            </div>
          </div>
        </div>

        <nav className="hidden xl:flex items-center space-x-12 text-[10px] font-black uppercase tracking-[0.3em] text-white/30">
          {['Mainframe', 'Neural Mesh', 'Archive', 'Protocols'].map(item => (
            <a key={item} href="#" className="hover:text-white transition-all duration-300 relative group">
              <span className="relative z-10">{item}</span>
              <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-blue-500 transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
          <div className="w-[1px] h-4 bg-white/5" />
          <div className="flex items-center space-x-3 bg-white/[0.02] px-4 py-2 rounded-full border border-white/5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-20" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-emerald-500/60 font-black">Node Secured</span>
          </div>
        </nav>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Main Workspace */}
        <main className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">

          {/* Tactical Command Center */}
          <section className="max-w-4xl mx-auto w-full transition-all duration-1000 ease-out translate-y-0 opacity-100 italic">
            <div className="text-center mb-10 space-y-3">
              <h2 className="text-3xl font-black tracking-[-0.06em] text-white/90 italic uppercase">INFRASTRUCTURE CORE</h2>
              <div className="flex items-center justify-center space-x-4">
                <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-white/10" />
                <p className="text-[10px] font-black text-white/20 uppercase tracking-[0.6em]">Initialize Deep-Scan Protocol</p>
                <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-white/10" />
              </div>
            </div>

            <div className="relative group p-[1px] rounded-[32px] bg-gradient-to-b from-white/15 to-transparent shadow-[0_30px_100px_rgba(0,0,0,0.8)]">
              <div className="bg-[#08080a] rounded-[31px] flex items-center p-2.5 border border-white/[0.02] shadow-inner-white">
                <div className="pl-8 pr-5 text-white/10 group-focus-within:text-blue-500 transition-all duration-500 scale-110">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Target domain or operational IPv4..."
                  className="flex-1 bg-transparent border-none text-lg font-bold placeholder-white/5 focus:outline-none focus:ring-0 text-white py-5 px-2 tracking-tight"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleScan()}
                />
                <button
                  onClick={handleScan}
                  disabled={scanning}
                  className={`px-10 h-16 rounded-[24px] font-black text-[12px] uppercase tracking-[0.2em] transition-all duration-500 flex items-center space-x-4 border border-white/5 ${scanning
                    ? 'bg-white/[0.02] text-white/10 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_40px_rgba(37,99,235,0.3)] active:scale-95 hover:-translate-y-0.5'
                    }`}
                >
                  {scanning ? (
                    <>
                      <div className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-white" />
                      </div>
                      <span className="italic uppercase">ENGAGING...</span>
                    </>
                  ) : (
                    <>
                      <span className="italic uppercase">Analyze</span>
                      <svg className="w-5 h-5 opacity-50 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap justify-center gap-8 px-4 font-black uppercase tracking-[0.3em] text-[10px]">
              <span className="text-white/10">Recent Nodes:</span>
              {['1.1.1.1', 'google.com', 'scanme.nmap.org'].map(suggested => (
                <button key={suggested} onClick={() => setTarget(suggested)} className="text-white/30 hover:text-blue-500 transition-all duration-300 flex items-center space-x-1.5 group">
                  <div className="w-1 h-1 rounded-full bg-white/10 group-hover:bg-blue-500 transition-colors" />
                  <span>{suggested}</span>
                </button>
              ))}
            </div>
          </section>

          {/* Infrastructure Matrix */}
          <section className="max-w-7xl mx-auto w-full space-y-10 italic">
            <div className="flex items-end justify-between border-b border-white/[0.02] pb-8 relative">
              <div className="absolute bottom-0 left-0 w-32 h-[1px] bg-blue-500" />
              <div className="space-y-2">
                <span className="text-[10px] uppercase tracking-[0.6em] font-black text-blue-500/80 italic">Telemetry Grid</span>
                <h2 className="text-2xl font-black text-white italic tracking-tight uppercase">INFRASTRUCTURE NODES</h2>
              </div>
              <div className="flex items-center space-x-6 text-[10px] font-black uppercase tracking-[0.3em] text-white/20 italic">
                <div className="flex flex-col items-end">
                  <span className="text-white/40 uppercase">Active Target</span>
                  <span className="text-white/70 mt-1 uppercase">{results ? results.target : 'Waiting...'}</span>
                </div>
                <div className="w-[1px] h-8 bg-white/5" />
                <div className="flex flex-col items-end">
                  <span className="text-white/40 uppercase">Detections</span>
                  <span className="text-white/70 mt-1 uppercase">{results ? results.results.length : 0} Segments</span>
                </div>
              </div>
            </div>

            {results ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
                {results.results.map((res, idx) => (
                  <div key={idx} className="group relative bg-[#0a0a0c]/80 edge-light rounded-[40px] p-8 transition-all duration-700 hover:shadow-[0_40px_100px_rgba(0,0,0,0.6)] hover:-translate-y-2 overflow-hidden border border-white/[0.02]">
                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent pointer-events-none" />

                    <div className="relative flex items-center justify-between mb-8">
                      <div className="flex space-x-4 items-center">
                        <div className="w-12 h-12 rounded-2xl bg-white/[0.03] flex items-center justify-center border border-white/5">
                          <svg className="w-5 h-5 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                          </svg>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] uppercase">Access Point</span>
                          <span className="text-xl font-black text-white italic uppercase">PORT {res.port}</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end pt-1">
                        <span className="text-[9px] font-black text-blue-500/50 uppercase tracking-[0.4em] mb-1">Service</span>
                        <div className="bg-white/[0.03] px-3 py-1 rounded-full border border-white/5 shadow-sm">
                          <span className="text-[10px] font-black text-white/80 uppercase tracking-tighter italic">{res.service}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="grid grid-cols-2 gap-4 pb-4 border-b border-white/[0.03]">
                        <div className="flex flex-col">
                          <span className="text-[9px] font-black text-white/10 uppercase tracking-widest uppercase">Protocol</span>
                          <span className="text-[11px] font-bold text-white/50 uppercase">TCP / State-Full</span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[9px] font-black text-white/10 uppercase tracking-widest uppercase">Security</span>
                          <span className={`text-[11px] font-bold uppercase ${res.vulnerabilities.length > 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                            {res.vulnerabilities.length > 0 ? 'Exposed' : 'Optimal'}
                          </span>
                        </div>
                      </div>

                      {res.vulnerabilities.length > 0 ? (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 pb-1">
                            <span className="relative flex h-2 w-2">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600" />
                            </span>
                            <span className="text-[10px] font-black text-red-500/80 uppercase tracking-[0.3em] italic uppercase">Active Threats Found</span>
                          </div>
                          {res.vulnerabilities.map((v, vidx) => (
                            <div key={vidx} className="bg-[#120a0a]/50 border border-red-900/10 rounded-2xl p-5 space-y-2 group-hover:bg-[#1a0c0c]/80 transition-all duration-500 shadow-xl">
                              <span className="text-[12px] font-black text-red-400 uppercase tracking-tight italic">{v.id}</span>
                              <p className="text-[11px] text-red-200/30 line-clamp-2 leading-relaxed font-bold uppercase tracking-wide">{v.output.split('\n')[0]}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="h-40 flex flex-col items-center justify-center text-center space-y-5 bg-gradient-to-b from-transparent to-white/[0.01] rounded-[32px] border border-white/[0.01]">
                          <div className="relative">
                            <div className="absolute inset-0 bg-emerald-500/10 blur-2xl rounded-full" />
                            <svg className="w-10 h-10 text-emerald-500/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                          </div>
                          <span className="text-[10px] font-black text-emerald-500/30 uppercase tracking-[0.5em] italic">Segment Integrity Verified</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-[600px] flex flex-col items-center justify-center text-center space-y-8">
                <div className="relative group perspective-1000">
                  <div className="absolute inset-0 bg-blue-500/10 blur-[100px] opacity-60 group-hover:bg-blue-500/20 transition-all duration-1000" />
                  <div className="relative w-48 h-48 bg-[#0a0a0c] border border-white/[0.03] rounded-[60px] flex items-center justify-center transition-all duration-1000 group-hover:rotate-[15deg] group-hover:scale-110 shadow-2xl">
                    <svg className="w-16 h-16 text-white/[0.02] group-hover:text-blue-500/10 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="0.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-sm font-black text-white/10 uppercase tracking-[0.8em] italic uppercase">System Hibernation</h3>
                  <p className="text-[10px] text-white/5 font-black uppercase tracking-[0.4em] italic uppercase">Awaiting operational telemetry for node auditing</p>
                </div>
              </div>
            )}
          </section>
        </main>

        {/* Neural Overlay Sidebar */}
        <aside className="w-[520px] bg-black/40 backdrop-blur-3xl border-l border-white/[0.02] flex flex-col z-20 shadow-[-40px_0_120px_rgba(0,0,0,0.9)] relative overflow-hidden">
          {/* Neural Flux Animation Background */}
          <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.5),transparent_70%)] animate-pulse" />
          </div>

          <div className="h-20 px-10 border-b border-white/[0.03] flex items-center justify-between relative z-10">
            <div className="flex items-center space-x-5">
              <div className="relative inline-flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-40"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]"></span>
              </div>
              <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-white/90 italic">Intelligence Neural</h3>
            </div>
            <div className="flex space-x-1.5 opacity-30">
              <div className="w-1 h-1 rounded-full bg-white animate-pulse" />
              <div className="w-1 h-1 rounded-full bg-white animate-pulse [animation-delay:0.2s]" />
              <div className="w-1 h-1 rounded-full bg-white animate-pulse [animation-delay:0.4s]" />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-12 space-y-10 custom-scrollbar relative z-10">
            {chatMessages.length === 0 && (
              <div className="space-y-12 py-6">
                <div className="relative p-12 rounded-[50px] bg-gradient-to-br from-blue-600/[0.03] to-transparent border border-white/[0.03] edge-light shadow-2xl">
                  <div className="absolute top-0 right-0 p-10 opacity-[0.03] rotate-12 scale-150">
                    <svg className="w-24 h-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="0.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="text-[11px] font-black text-blue-500 uppercase tracking-[0.3em] italic mb-6">Autonomous Core</h4>
                  <p className="text-[12px] text-white/50 leading-relaxed font-black uppercase tracking-widest italic">
                    Neural bridge established. Cross-referencing infrastructure telemetry with threat databases. Requesting operational directives.
                  </p>
                </div>

                <div className="space-y-6 px-4">
                  <span className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-black italic">Active Directives</span>
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      'Map critical exploit chain',
                      'Contextualize top-tier threats',
                      'Audit network entry vectors'
                    ].map((q) => (
                      <button
                        key={q}
                        onClick={() => setChatInput(q)}
                        className="text-left text-[10px] font-black text-white/30 hover:text-white/90 bg-white/[0.01] hover:bg-white/[0.04] border border-white/[0.01] hover:border-white/10 p-6 rounded-[32px] transition-all duration-500 transform active:scale-[0.98] group flex items-center justify-between uppercase tracking-widest italic"
                      >
                        <span>"{q}"</span>
                        <div className="w-8 h-8 rounded-full bg-white/[0.02] flex items-center justify-center group-hover:bg-blue-600 transition-all duration-500 group-hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                          <svg className="w-3 h-3 text-white/20 group-hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[90%] px-8 py-6 text-[13px] font-black leading-relaxed tracking-wide shadow-2xl transition-all duration-700 hover:scale-[1.02] ${msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-t-[32px] rounded-bl-[32px] rounded-br-[8px] shadow-blue-600/20 italic'
                    : 'bg-white/[0.03] text-white/60 border border-white/[0.02] rounded-t-[32px] rounded-br-[32px] rounded-bl-[8px] backdrop-blur-3xl'
                  }`}>
                  {msg.content}
                </div>
              </div>
            ))}

            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white/[0.02] border border-white/[0.03] rounded-t-3xl rounded-br-3xl rounded-bl-lg px-8 py-6 flex items-center space-x-3 backdrop-blur-xl">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-duration:0.6s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-duration:0.6s] [animation-delay:0.1s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-duration:0.6s] [animation-delay:0.2s]"></div>
                </div>
              </div>
            )}
          </div>

          <div className="p-12 border-t border-white/[0.03] bg-black/40 relative z-10">
            <form onSubmit={handleChat} className="bg-white/[0.02] border border-white/[0.04] rounded-[36px] p-2.5 flex items-center group focus-within:border-blue-500/30 transition-all duration-700 shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
              <input
                type="text"
                placeholder="Synchronize with Neural Core..."
                className="flex-1 bg-transparent border-none text-[13px] font-black placeholder-white/5 focus:outline-none focus:ring-0 text-white px-8 uppercase tracking-[0.1em] italic"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button
                type="submit"
                className="w-14 h-14 rounded-[24px] bg-white/[0.02] group-focus-within:bg-blue-600 flex items-center justify-center transition-all duration-700 group-focus-within:shadow-[0_0_30px_rgba(37,99,235,0.4)] text-white/10 group-focus-within:text-white border border-white/5"
                disabled={chatLoading}
              >
                <svg className="w-6 h-6 transition-transform group-focus-within:-rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
