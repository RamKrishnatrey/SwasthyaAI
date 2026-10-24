import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode, type RefObject } from 'react';
import {
  Activity, ArrowRight, ArrowUpRight, AudioLines, BellRing, BookOpenText, CalendarClock, Check,
  CheckCircle2, ChevronRight, ClipboardList, Compass, HeartHandshake, Home, Languages, LayoutDashboard,
  LockKeyhole, MessageCircle, Mic, MicOff, MoreHorizontal, Plus, Send, ShieldAlert, ShieldCheck,
  SlidersHorizontal, Sparkles, Users, Volume2, Waves, X,
} from 'lucide-react';
import { Navbar, BrandMark } from './components/Navbar';
import { CaregiverCard } from './components/CaregiverCard';
import { ExplainabilityPanel } from './components/ExplainabilityPanel';
import { PrivacyDisclaimerModal } from './components/PrivacyDisclaimerModal';
import { SafetyShieldUrgentModal } from './components/SafetyShieldUrgentModal';
import { translations } from './i18n/translations';
import { sendAgentMessage } from './services/agentApi';
import { demoCaregivers } from './services/demoFixtures';
import type { AgentResponse, Caregiver, Language, ViewId } from './types/agent';
import { rankCaregiver, RANKING_WEIGHTS } from './utils/rankingFormula';

interface ChatMessage { id: string; role: 'user' | 'assistant'; content: string; }
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';
const makeSessionId = () => `sw-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

const navItems: Array<{ id: ViewId; label: string; icon: typeof Home; group: 'main' | 'manage' }> = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, group: 'main' },
  { id: 'care', label: 'Care check', icon: MessageCircle, group: 'main' },
  { id: 'caregivers', label: 'Find care', icon: Users, group: 'main' },
  { id: 'future', label: 'Future radar', icon: Activity, group: 'manage' },
  { id: 'privacy', label: 'Privacy & safety', icon: ShieldCheck, group: 'manage' },
];

function App() {
  const [view, setView] = useState<ViewId>('overview');
  const [language, setLanguage] = useState<Language>('en');
  const [elderCare, setElderCare] = useState(false);
  const [privacyOpen, setPrivacyOpen] = useState(false);
  const [urgentOpen, setUrgentOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [agentResult, setAgentResult] = useState<AgentResponse | null>(null);
  const [sessionId, setSessionId] = useState(makeSessionId());
  const [turnCount, setTurnCount] = useState(0);
  const [showRankDetails, setShowRankDetails] = useState(false);
  const [bookedCaregiver, setBookedCaregiver] = useState<Caregiver | null>(null);
  const [bookingMessage, setBookingMessage] = useState('');
  const [selectedTime, setSelectedTime] = useState('First available');
  const [shareFamily, setShareFamily] = useState(false);
  const [reminders, setReminders] = useState(false);
  const [privacySaved, setPrivacySaved] = useState(false);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('best');
  const messageEndRef = useRef<HTMLDivElement | null>(null);
  const caregiverSource = useMemo(() => {
    if (agentResult?.source === 'api') return agentResult.caregiver_matches ?? [];
    if (agentResult?.status === 'routed' && agentResult.caregiver_matches?.length) return agentResult.caregiver_matches;
    return DEMO_MODE ? demoCaregivers : [];
  }, [agentResult]);
  const allCaregivers = useMemo(() => caregiverSource.map(rankCaregiver).sort((a, b) => b.score - a.score), [caregiverSource]);
  const visibleCaregivers = useMemo(() => {
    const filtered = allCaregivers.filter((c) => `${c.name} ${c.role} ${c.skills.join(' ')} ${c.languages.join(' ')}`.toLowerCase().includes(search.toLowerCase()));
    return [...filtered].sort((a, b) => sortBy === 'distance' ? a.distanceKm - b.distanceKm : sortBy === 'rating' ? b.rating - a.rating : b.score - a.score);
  }, [allCaregivers, search, sortBy]);

  useEffect(() => { messageEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }, [chatMessages, busy]);
  useEffect(() => {
    const onRank = () => setShowRankDetails(true);
    window.addEventListener('swasthya:show-ranking', onRank);
    return () => window.removeEventListener('swasthya:show-ranking', onRank);
  }, []);

  const beginCareCheck = (prompt = '') => {
    setView('care'); setError(''); setBookingMessage('');
    if (prompt) setMessage(prompt);
    else if (chatMessages.length === 0) setMessage('');
  };

  const resetJourney = () => {
    setChatMessages([]); setAgentResult(null); setTurnCount(0); setMessage(''); setError('');
    setSessionId(makeSessionId()); setUrgentOpen(false); setView('care');
  };

  const sendMessage = async (override?: string) => {
    const content = (override ?? message).trim();
    if (!content || busy) return;
    setError(''); setBusy(true); setMessage('');
    const newHistory: ChatMessage[] = [...chatMessages, { id: `${Date.now()}-u`, role: 'user', content }];
    setChatMessages(newHistory);
    try {
      const result = await sendAgentMessage({
        session_id: sessionId,
        message: content,
        language,
        history: newHistory.map(({ role, content: text }) => ({ role, content: text })),
      }, turnCount);
      setAgentResult(result);
      setTurnCount((current) => current + 1);
      setChatMessages((current) => [...current, { id: `${Date.now()}-a`, role: 'assistant', content: result.response }]);
      if (result.status === 'possible_emergency') setUrgentOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reach the agent. No live result was generated.');
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); void sendMessage(); };
  const handleBook = (caregiver: Caregiver) => { setBookedCaregiver(caregiver); setBookingMessage(''); setSelectedTime(caregiver.availability); };
  const confirmDemoBooking = () => {
    setBookingMessage(`Demo booking request created for ${bookedCaregiver?.name}. This is a local simulation; no provider has been contacted and no appointment is confirmed.`);
  };

  return (
    <div className={`app-shell ${elderCare ? 'elder-care-mode' : ''}`}>
      <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}>
        <div className="brand-lockup"><BrandMark/><div><span className="brand-name">Swasthya<span>AI</span></span><span className="brand-descriptor">CARE, MADE CLEARER</span></div><button className="mobile-close icon-button" onClick={() => setMobileNavOpen(false)} aria-label="Close navigation"><X size={18}/></button></div>
        <div className="sidebar-label">YOUR WORKSPACE</div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {navItems.filter((item) => item.group === 'main').map((item) => <NavButton key={item.id} item={item} active={view === item.id} onClick={() => { setView(item.id); setMobileNavOpen(false); }}/>) }
          <div className="nav-divider"/><div className="sidebar-label sidebar-label-spaced">PLANNING & TRUST</div>
          {navItems.filter((item) => item.group === 'manage').map((item) => <NavButton key={item.id} item={item} active={view === item.id} onClick={() => { setView(item.id); setMobileNavOpen(false); }}/>) }
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-help"><div className="help-icon"><HeartHandshake size={19}/></div><div><strong>Care should feel human.</strong><span>Questions? Explore privacy & safety.</span><button onClick={() => setPrivacyOpen(true)}>Read our approach <ArrowUpRight size={13}/></button></div></div>
          <div className="profile-row"><div className="profile-avatar">S</div><div className="profile-meta"><strong>Demo workspace</strong><span>Local session · No sign-in</span></div><MoreHorizontal size={18} className="profile-more"/></div>
        </div>
      </aside>

      <div className="main-column">
        <Navbar language={language} onLanguageChange={setLanguage} elderCare={elderCare} onElderCareChange={setElderCare} onPrivacy={() => setPrivacyOpen(true)} demoMode={DEMO_MODE}/>
        <main className="main-content">
          {DEMO_MODE && <div className="demo-banner"><span className="demo-banner-icon"><Sparkles size={15}/></span><span><strong>Interactive demo</strong> Synthetic profiles and illustrative outputs only. Do not enter real health information.</span><button onClick={() => setPrivacyOpen(true)}>Read limitations <ArrowUpRight size={13}/></button></div>}
          {view === 'overview' && <OverviewView onStart={beginCareCheck} onNavigate={setView} language={language} onPrivacy={() => setPrivacyOpen(true)}/>}
          {view === 'care' && <CareView language={language} message={message} setMessage={setMessage} busy={busy} error={error} chatMessages={chatMessages} result={agentResult} onSubmit={handleSubmit} onSend={sendMessage} onReset={resetJourney} messageEndRef={messageEndRef} onPrivacy={() => setPrivacyOpen(true)} onViewCaregivers={() => setView('caregivers')}/>}
          {view === 'caregivers' && <CaregiversView caregivers={visibleCaregivers} demoProfiles={DEMO_MODE && agentResult?.source !== 'api'} search={search} onSearch={setSearch} sortBy={sortBy} onSort={setSortBy} onBook={handleBook} showRankDetails={showRankDetails} setShowRankDetails={setShowRankDetails}/>}
          {view === 'future' && <FutureView/>}
          {view === 'privacy' && <PrivacyView shareFamily={shareFamily} setShareFamily={setShareFamily} reminders={reminders} setReminders={setReminders} saved={privacySaved} onSave={() => setPrivacySaved(true)}/>}
          <footer className="app-footer"><span>© 2026 SwasthyaAI <span className="footer-separator">·</span> A care-navigation prototype</span><span><ShieldCheck size={13}/> Not a diagnosis or medical advice</span></footer>
        </main>
      </div>

      <SafetyShieldUrgentModal result={urgentOpen ? agentResult : null} onClose={() => setUrgentOpen(false)} />
      {urgentOpen && agentResult?.status === 'possible_emergency' && <div className="urgent-state-backdrop" aria-hidden="true"/>}
      {privacyOpen && <PrivacyDisclaimerModal onClose={() => setPrivacyOpen(false)}/>}
      {bookedCaregiver && <BookingModal caregiver={bookedCaregiver} selectedTime={selectedTime} onTimeChange={setSelectedTime} message={bookingMessage} onConfirm={confirmDemoBooking} onClose={() => { setBookedCaregiver(null); setBookingMessage(''); }}/>}
    </div>
  );
}

type NavItem = typeof navItems[number];
function NavButton({ item, active, onClick }: { item: NavItem; active: boolean; onClick: () => void }) {
  const Icon = item.icon;
  return <button className={`nav-button ${active ? 'nav-button-active' : ''}`} onClick={onClick}><Icon size={18} strokeWidth={active ? 2.1 : 1.8}/><span>{item.label}</span>{active && <span className="nav-active-indicator"/>}</button>;
}

function SectionHeading({ eyebrow, title, subtitle, action }: { eyebrow?: string; title: string; subtitle?: string; action?: ReactNode }) {
  return <div className="section-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action}</div>;
}

function OverviewView({ onStart, onNavigate, language, onPrivacy }: { onStart: (prompt?: string) => void; onNavigate: (view: ViewId) => void; language: Language; onPrivacy: () => void }) {
  const t = translations[language];
  return <div className="page-stack overview-page">
    <section className="hero-panel">
      <div className="hero-copy"><div className="eyebrow hero-eyebrow"><span className="eyebrow-dot"/> YOUR NEXT STEP, WITH CLARITY</div><h1>{t.title === 'Care, made clearer.' ? <>A little more clarity.<br/><em>A lot more care.</em></> : t.title}</h1><p>{t.subtitle} SwasthyaAI brings together guided intake, safety-first navigation and caregiver discovery in one calm experience.</p><div className="hero-actions"><button className="button button-primary" onClick={() => onStart()}>{t.start}<ArrowRight size={17}/></button><button className="button button-ghost" onClick={() => onNavigate('caregivers')}>Explore caregivers <ArrowUpRight size={16}/></button></div><div className="hero-trust"><span><CheckCircle2 size={15}/> Plain-language guidance</span><span><CheckCircle2 size={15}/> Safety-aware workflow</span></div></div>
      <div className="hero-art" aria-label="Illustration of a guided care journey">
        <div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/><div className="art-dot art-dot-one"/><div className="art-dot art-dot-two"/>
        <div className="art-center"><div className="art-heart"><Activity size={36}/></div><span>CARE, CONNECTED</span></div>
        <div className="art-chip art-chip-top"><span className="mini-icon mini-icon-sage"><Languages size={15}/></span><div><strong>Your language</strong><small>English · हिन्दी · Hinglish</small></div></div>
        <div className="art-chip art-chip-bottom"><span className="mini-icon mini-icon-amber"><ShieldCheck size={16}/></span><div><strong>Safety comes first</strong><small>Guidance before matching</small></div></div>
        <div className="art-caption"><span className="caption-line"/>Designed around people, not just prompts.</div>
      </div>
      <div className="hero-index">01 <span>/</span> 04</div>
    </section>

    <div className="section-kicker-row"><div><div className="eyebrow">WHERE WOULD YOU LIKE TO BEGIN?</div><h2>Start where you are.</h2></div><span className="small-muted">Three simple paths into care</span></div>
    <section className="entry-grid">
      <button className="entry-card entry-card-primary" onClick={() => onStart()}><div className="entry-card-top"><div className="entry-icon entry-icon-green"><MessageCircle size={20}/></div><span className="entry-count">01</span></div><div><h3>Talk through a concern</h3><p>Share what's happening in your own words. Get help navigating your next step.</p></div><span className="entry-link">Start a care check <ArrowUpRight size={16}/></span><div className="entry-decoration entry-decoration-one"/></button>
      <button className="entry-card" onClick={() => onNavigate('caregivers')}><div className="entry-card-top"><div className="entry-icon entry-icon-amber"><Users size={20}/></div><span className="entry-count">02</span></div><div><h3>Explore care options</h3><p>Compare illustrative caregiver profiles by fit, language, distance and availability.</p></div><span className="entry-link">Find care <ArrowUpRight size={16}/></span><div className="entry-decoration entry-decoration-two"/></button>
      <button className="entry-card" onClick={() => onNavigate('future')}><div className="entry-card-top"><div className="entry-icon entry-icon-blue"><Activity size={20}/></div><span className="entry-count">03</span></div><div><h3>Look ahead</h3><p>Explore how care teams could prepare for changing service demand.</p></div><span className="entry-link">Open Future Radar <ArrowUpRight size={16}/></span><div className="entry-decoration entry-decoration-three"/></button>
    </section>

    <section className="journey-section"><div className="journey-head"><div><div className="eyebrow">A CARE JOURNEY, NOT A CHATBOT</div><h2>From first concern to next step.</h2></div><button className="text-button" onClick={() => onStart()}>See it in action <ArrowRight size={15}/></button></div><div className="journey-track"><JourneyStep number="01" icon={<MessageCircle size={18}/>} title="Listen" text="Understand the message; clarify what's missing."/><div className="journey-connector"/><JourneyStep number="02" icon={<ShieldCheck size={18}/>} title="Check safety" text="Check the configured safety pathway first."/><div className="journey-connector"/><JourneyStep number="03" icon={<Compass size={18}/>} title="Navigate" text="Show a structured result with clear reasons."/><div className="journey-connector"/><JourneyStep number="04" icon={<HeartHandshake size={18}/>} title="Connect" text="Explore eligible care options when appropriate."/></div></section>

    <section className="future-strip"><div className="future-strip-icon"><Waves size={22}/></div><div className="future-strip-copy"><div className="eyebrow">DESIGNED FOR WHAT'S NEXT</div><h3>Care systems will change. Navigation should keep up.</h3><p>Older adults, stretched care teams and uneven access require more than a symptom checker. SwasthyaAI is designed to grow toward continuity of care and resource planning.</p></div><button className="button button-light" onClick={() => onNavigate('future')}>Explore future features <ArrowUpRight size={16}/></button></section>
    <div className="mini-disclaimer"><ShieldCheck size={15}/><span>SwasthyaAI is a care-navigation prototype, not a diagnostic or treatment service.</span><button onClick={onPrivacy}>How we handle safety <ArrowUpRight size={13}/></button></div>
  </div>;
}
function JourneyStep({ number, icon, title, text }: { number: string; icon: ReactNode; title: string; text: string }) { return <div className="journey-step"><div className="journey-step-top"><span>{number}</span><div>{icon}</div></div><h3>{title}</h3><p>{text}</p></div>; }

function CareView({ language, message, setMessage, busy, error, chatMessages, result, onSubmit, onSend, onReset, messageEndRef, onPrivacy, onViewCaregivers }: { language: Language; message: string; setMessage: (message: string) => void; busy: boolean; error: string; chatMessages: ChatMessage[]; result: AgentResponse | null; onSubmit: (event: FormEvent<HTMLFormElement>) => void; onSend: (message?: string) => Promise<void>; onReset: () => void; messageEndRef: RefObject<HTMLDivElement | null>; onPrivacy: () => void; onViewCaregivers: () => void }) {
  const [speechSupported, setSpeechSupported] = useState(typeof window !== 'undefined' && 'SpeechRecognition' in window || typeof window !== 'undefined' && 'webkitSpeechRecognition' in window);
  const [listening, setListening] = useState(false);
  const [speechError, setSpeechError] = useState('');
  const t = translations[language];

  const startSpeechInput = () => {
    const browser = window as Window & { SpeechRecognition?: new () => SpeechRecognitionLike; webkitSpeechRecognition?: new () => SpeechRecognitionLike };
    const SpeechRecognitionCtor = browser.SpeechRecognition || browser.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) { setSpeechSupported(false); setSpeechError('Speech input is not supported in this browser. You can type instead.'); return; }
    const recognition = new SpeechRecognitionCtor();
    recognition.lang = language === 'hi' ? 'hi-IN' : language === 'hinglish' ? 'hi-IN' : 'en-IN';
    recognition.interimResults = false; recognition.maxAlternatives = 1;
    recognition.onresult = (event) => { const text = event.results[0]?.[0]?.transcript; if (text) setMessage(text); setListening(false); };
    recognition.onerror = () => { setListening(false); setSpeechError('Speech recognition stopped. Please type your message instead.'); };
    recognition.onend = () => setListening(false);
    setSpeechError(''); setListening(true); recognition.start();
  };
  const readLastResponse = () => {
    if (!result?.response || !('speechSynthesis' in window)) { setSpeechError('Read-aloud is unavailable in this browser.'); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(result.response);
    utterance.lang = language === 'hi' ? 'hi-IN' : language === 'hinglish' ? 'hi-IN' : 'en-IN';
    window.speechSynthesis.speak(utterance);
  };

  return <div className="page-stack care-page">
    <SectionHeading eyebrow="BASHACARE · GUIDED INTAKE" title="Let's take this one step at a time." subtitle="Share only what you are comfortable sharing. The demo uses illustrative outputs and is not a medical assessment." action={<button className="button button-outline" onClick={onReset}><Plus size={15}/> New session</button>}/>
    <div className="care-layout">
      <section className="conversation-panel">
        <div className="conversation-toolbar"><div className="conversation-agent"><div className="agent-orb"><Activity size={18}/></div><div><strong>Swasthya assistant</strong><span><span className="status-dot"/>{busy ? 'Working on your message…' : 'Guided care navigation'}</span></div></div><div className="conversation-tools"><span className="language-chip"><Languages size={13}/>{language === 'hi' ? 'हिन्दी' : language === 'hinglish' ? 'Hinglish' : 'English'}</span><button className="icon-button subtle-icon" title="Read latest response aloud" onClick={readLastResponse}><Volume2 size={17}/></button></div></div>
        <div className="conversation-content">
          {chatMessages.length === 0 && <div className="conversation-welcome"><div className="welcome-art"><div className="welcome-art-circle"><MessageCircle size={26}/></div><span className="welcome-spark welcome-spark-a">✳</span><span className="welcome-spark welcome-spark-b">·</span></div><div className="eyebrow">A QUIETER PLACE TO START</div><h2>What's on your mind?</h2><p>Describe the concern in your own words. We'll guide the demo conversation one step at a time.</p><div className="prompt-label">TRY A DEMO SCENARIO</div><div className="prompt-chips"><button onClick={() => setMessage('Papa ko do din se bukhar hai aur khansi bhi.')}>Hinglish · Fever and cough <ArrowUpRight size={13}/></button><button onClick={() => setMessage('I have felt dizzy since this morning.')}>English · Dizziness <ArrowUpRight size={13}/></button><button className="prompt-chip-warning" onClick={() => setMessage('I have severe chest pain and difficulty breathing.')}>Safety test · Urgent phrase <ShieldAlert size={13}/></button></div></div>}
          {chatMessages.map((chat) => <div className={`chat-message chat-message-${chat.role}`} key={chat.id}>{chat.role === 'assistant' && <div className="chat-avatar"><Activity size={15}/></div>}<div className="chat-bubble-wrap"><div className="chat-role-label">{chat.role === 'assistant' ? 'SWASTHYAAI' : 'YOU'}</div><div className="chat-bubble">{chat.content}</div></div>{chat.role === 'user' && <div className="chat-user-avatar">S</div>}</div>)}
          {busy && <div className="chat-message chat-message-assistant"><div className="chat-avatar"><Activity size={15}/></div><div className="typing-bubble"><span/><span/><span/></div></div>}
          {error && <div className="api-error"><ShieldAlert size={17}/><div><strong>No live result returned</strong><p>{error}</p><span>Check the backend URL or explicitly enable demo mode for the demonstration.</span></div></div>}
          {result?.status === 'needs_followup' && result.follow_up_question && <div className="followup-card"><div className="followup-label"><span>FOLLOW-UP</span><span>To clarify</span></div><h3>{result.follow_up_question.text}</h3><div className="followup-options">{(result.follow_up_question.options || []).map((option) => <button key={option} onClick={() => void onSend(option)} disabled={busy}>{option}<ChevronRight size={14}/></button>)}</div><div className="followup-freeform"><span>Or type your own answer below</span><InfoInline/></div></div>}
          {result?.status === 'possible_emergency' && <div className="urgent-inline"><div className="urgent-inline-icon"><ShieldAlert size={20}/></div><div><strong>Safety pathway activated</strong><p>Normal caregiver matching has been bypassed. This demo trigger is not a validated triage assessment.</p><button onClick={onPrivacy}>Read safety limitations <ArrowUpRight size={14}/></button></div></div>}
          {result?.status === 'routed' && result.triage && <div className="result-preview"><div className="result-preview-header"><span className="result-check-icon"><ClipboardList size={17}/></span><div><div className="eyebrow">DEMO CARE-NAVIGATION RESULT</div><h3>{result.triage.care_type}</h3></div><span className="urgency-unknown">Urgency: {result.triage.urgency}</span></div><p>{result.triage.explanation}</p><div className="result-steps">{result.triage.next_steps.map((step, index) => <div key={step}><span>{index + 1}</span>{step}</div>)}</div><div className="result-caveat"><InfoInline/>{result.triage.model_name || 'Demo adapter'} · Not a diagnosis · No clinical urgency determined</div><ExplainabilityPanel explanations={result.explanation || []}/>{result.caregiver_matches && result.caregiver_matches.length > 0 && <button className="button button-primary button-full" onClick={onViewCaregivers}>Explore demo caregiver matches <ArrowRight size={16}/></button>}</div>}
          <div ref={messageEndRef}/>
        </div>
        <form className="composer" onSubmit={onSubmit}><div className="composer-top"><span>{t.language}: <strong>{language === 'hi' ? 'हिन्दी' : language === 'hinglish' ? 'Hinglish' : 'English'}</strong></span><span>Press Enter to send</span></div><div className="composer-input-row"><textarea rows={1} value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void onSend(); } }} placeholder={t.describe} aria-label="Describe your concern" disabled={busy} maxLength={1200}/><button type="button" className={`composer-tool ${listening ? 'composer-tool-live' : ''}`} onClick={startSpeechInput} title={speechSupported ? 'Use voice input' : 'Voice input unsupported'} disabled={busy}><Mic size={18}/></button><button className="send-button" type="submit" disabled={busy || !message.trim()} aria-label="Send message">{busy ? <span className="mini-spinner"/> : <Send size={17}/>}</button></div>{speechError && <div className="speech-note">{listening ? <AudioLines size={14}/> : <MicOff size={14}/>} {speechError}</div>}<div className="composer-foot"><span><LockKeyhole size={13}/> Don't enter real personal health information in demo mode.</span><span>{message.length}/1200</span></div></form>
      </section>
      <aside className="care-side-column">
        <div className="side-info-card safety-info-card"><div className="side-info-head"><div className="mini-icon mini-icon-sage"><ShieldCheck size={17}/></div><span className="eyebrow">SAFETYSHIELD</span><span className="status-pill status-pill-neutral">Guardrail</span></div><h3>Safety before suggestions.</h3><p>Possible emergency phrases must bypass normal matching. Demo rules are illustrative and are not clinically validated.</p><div className="safety-info-foot"><span><span className="status-dot status-dot-green"/> Workflow separation</span><button onClick={onPrivacy}>Details <ArrowUpRight size={13}/></button></div></div>
        <div className="side-info-card journey-status-card"><div className="side-info-head"><div className="mini-icon mini-icon-amber"><Compass size={17}/></div><span className="eyebrow">YOUR SESSION</span></div><h3>Care journey</h3><div className="mini-progress-list"><MiniProgress done={chatMessages.length > 0} title="Listen" subtitle="Understand your message"/><MiniProgress done={Boolean(result && result.status !== 'needs_followup')} title="Navigate" subtitle="Return a structured result"/><MiniProgress done={false} title="Connect" subtitle="Explore care options if appropriate"/></div><div className="side-divider"/><div className="side-callout"><BookOpenText size={16}/><span>You're in a local demo session. Results may be simulated.</span></div></div>
        <div className="side-note-card"><div className="side-note-mark"><HeartHandshake size={18}/></div><div><strong>Need a human, not an app?</strong><p>If you are worried about an urgent situation, contact local emergency services or a qualified healthcare professional directly.</p></div></div>
      </aside>
    </div>
  </div>;
}
interface SpeechRecognitionLike { lang: string; interimResults: boolean; maxAlternatives: number; onresult: (event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void; onerror: () => void; onend: () => void; start: () => void; }
function InfoInline() { return <span className="info-inline" aria-label="Information">i</span>; }
function MiniProgress({ done, title, subtitle }: { done: boolean; title: string; subtitle: string }) { return <div className={`mini-progress ${done ? 'mini-progress-done' : ''}`}><div className="mini-progress-node">{done ? <Check size={12}/> : null}</div><div><strong>{title}</strong><span>{subtitle}</span></div></div>; }

function CaregiversView({ caregivers, demoProfiles, search, onSearch, sortBy, onSort, onBook, showRankDetails, setShowRankDetails }: { caregivers: ReturnType<typeof rankCaregiver>[]; demoProfiles: boolean; search: string; onSearch: (value: string) => void; sortBy: string; onSort: (value: string) => void; onBook: (caregiver: Caregiver) => void; showRankDetails: boolean; setShowRankDetails: (value: boolean) => void }) {
  return <div className="page-stack caregivers-page"><SectionHeading eyebrow="CARE NAVIGATION · MATCHING" title="Find care that fits." subtitle={demoProfiles ? 'Explore synthetic caregiver profiles and understand what influences a match.' : 'Review caregiver matches returned by the connected agent and backend.'} action={<span className="demo-tag demo-tag-large">{demoProfiles ? 'Demo profiles only' : 'Connected result data'}</span>}/>
    <div className="matching-intro"><div><div className="matching-intro-icon"><Users size={20}/></div><div><strong>Eligibility first. Ranking second.</strong><p>{demoProfiles ? 'Only providers meeting mandatory requirements should be ranked. These illustrative profiles have not been verified.' : 'Only providers meeting mandatory requirements should be ranked. Verify credential and availability fields before acting on them.'}</p></div></div><button className="text-button" onClick={() => setShowRankDetails(!showRankDetails)}>{showRankDetails ? 'Hide' : 'View'} ranking formula <ArrowUpRight size={15}/></button></div>
    {showRankDetails && <div className="ranking-details"><div><div className="eyebrow">ILLUSTRATIVE RANKING FORMULA</div><h3>S = 0.35K + 0.25D + 0.20A + 0.10L + 0.10R</h3><p>Weights are configurable engineering assumptions, not validated measures of care quality. The score is not a probability of a successful outcome.</p></div><div className="weight-bars">{Object.entries(RANKING_WEIGHTS).map(([key, value]) => <div className="weight-row" key={key}><span>{({ skillFit: 'Skill fit', distance: 'Distance', availability: 'Slot suitability', language: 'Language', rating: 'Rating' } as Record<string, string>)[key]}</span><div className="weight-bar"><span style={{ width: `${value * 100}%` }}/></div><strong>{Math.round(value * 100)}%</strong></div>)}</div></div>}
    <div className="list-controls"><div className="search-field"><SlidersHorizontal size={16}/><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Search skills, language or role…" aria-label="Search caregiver profiles"/>{search && <button onClick={() => onSearch('')} aria-label="Clear search"><X size={14}/></button>}</div><label className="sort-select"><span>Sort by</span><select value={sortBy} onChange={(event) => onSort(event.target.value)}><option value="best">Best match</option><option value="distance">Distance</option><option value="rating">Rating</option></select></label><span className="results-count">{caregivers.length} demo profiles</span></div>
    {caregivers.length ? <div className="caregiver-grid">{caregivers.map((caregiver) => <CaregiverCard key={caregiver.id} caregiver={caregiver} onBook={onBook} demoProfile={demoProfiles}/>)}</div> : <div className="empty-state"><Users size={25}/><h3>{demoProfiles ? 'No matching demo profiles' : 'No caregiver matches returned'}</h3><p>{demoProfiles ? 'Try a different name, skill or language.' : 'Complete a care check or connect the provider data service to return suitable matches.'}</p><button className="button button-outline" onClick={() => onSearch('')}>Clear search</button></div>}
    <div className="matching-caveat"><ShieldCheck size={16}/><p><strong>Before this becomes a live service:</strong> verify provider credentials, service area and availability. A weighted score cannot replace mandatory qualification checks or professional judgement.</p></div>
  </div>;
}

function FutureView() {
  const demand = [{ day: 'Mon', value: 44 }, { day: 'Tue', value: 61 }, { day: 'Wed', value: 48 }, { day: 'Thu', value: 73 }, { day: 'Fri', value: 88 }, { day: 'Sat', value: 67 }, { day: 'Sun', value: 39 }];
  const features = [
    { icon: <HeartHandshake size={19}/>, title: 'CareContinuity', label: 'PROPOSED', text: 'Patient-approved visit summaries and opt-in follow-up reminders, with clear sharing controls.' },
    { icon: <Users size={19}/>, title: 'CareLoad', label: 'PROPOSED', text: 'Help coordinators notice unfilled service requests and capacity gaps before they become harder to manage.' },
    { icon: <Waves size={19}/>, title: 'CareFallback', label: 'PLANNED', text: 'Keep limited static guidance accessible offline while being honest that live checks and bookings may fail.' },
    { icon: <Languages size={19}/>, title: 'BhashaCare expansion', label: 'PLANNED', text: 'Expand language coverage only when the models and evaluation datasets genuinely support it.' },
  ];
  return <div className="page-stack future-page"><SectionHeading eyebrow="PLANNING FOR TOMORROW" title="Care needs don't stand still." subtitle="A concept view of how the platform could help teams prepare for changing demand. All figures below are synthetic demo data." action={<span className="status-pill status-pill-neutral"><span className="status-dot"/> Simulation</span>}/>
    <section className="radar-overview"><div className="radar-overview-copy"><div className="eyebrow eyebrow-light">FUTUREDEMAND RADAR</div><h2>See the pressure points.<br/><em>Plan the next move.</em></h2><p>Use aggregated service requests to explore where demand may outpace available capacity. This prototype illustrates a workflow; it is not a validated forecast.</p><div className="radar-metrics"><div><span>Example requests</span><strong>420</strong><small>synthetic sample</small></div><div><span>Unfilled requests</span><strong>18</strong><small>synthetic sample</small></div><div><span>Data window</span><strong>7 days</strong><small>illustrative only</small></div></div></div><div className="demand-chart-card"><div className="chart-title-row"><div><strong>Request volume by day</strong><span>Example weekly pattern</span></div><span className="chart-label">DEMO</span></div><div className="chart-area"><div className="chart-ylabels"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div><div className="chart-bars">{demand.map((item) => <div className="chart-bar-wrap" key={item.day}><div className="chart-bar-value">{item.value}</div><div className="chart-bar-column"><span style={{ height: `${item.value}%` }}/></div><span className="chart-day">{item.day}</span></div>)}</div></div><div className="chart-legend"><span><i/> Illustrative requests</span><span>Not real operational data</span></div></div></section>
    <div className="section-kicker-row future-section-title"><div><div className="eyebrow">A ROADMAP WITH A PURPOSE</div><h2>Designed for future pressure.</h2></div><span className="small-muted">Ideas, not live services</span></div><section className="future-feature-grid">{features.map((feature) => <article className="future-feature-card" key={feature.title}><div className="future-feature-top"><div className="entry-icon entry-icon-green">{feature.icon}</div><span className="roadmap-label">{feature.label}</span></div><h3>{feature.title}</h3><p>{feature.text}</p><div className="future-feature-foot"><span>Future capability</span><ArrowUpRight size={15}/></div></article>)}</section>
    <div className="future-caveat"><InfoInline/><p><strong>Responsible forecasting:</strong> Use synthetic data for the demo. Real demand forecasting requires suitable historical data, data governance, validation and monitoring; it must not be presented as a prediction of an individual person's illness.</p></div>
  </div>;
}

function PrivacyView({ shareFamily, setShareFamily, reminders, setReminders, saved, onSave }: { shareFamily: boolean; setShareFamily: (v: boolean) => void; reminders: boolean; setReminders: (v: boolean) => void; saved: boolean; onSave: () => void }) {
  return <div className="page-stack privacy-page"><SectionHeading eyebrow="TRUST BY DESIGN" title="Your care story stays yours." subtitle="Privacy controls shown here are a prototype. Actual storage and access controls depend on the integrated backend."/><section className="privacy-hero"><div className="privacy-hero-icon"><LockKeyhole size={25}/></div><div><div className="eyebrow">PRIVACY PASSPORT</div><h2>Clarity about what gets shared.</h2><p>A healthcare interface should explain what information is needed, why it is needed and who will be able to access it.</p></div></section><section className="privacy-control-list"><div className="privacy-control"><div className="privacy-control-icon"><Users size={19}/></div><div className="privacy-control-copy"><strong>Trusted contact sharing</strong><p>Allow a future connected feature to share booking updates or summaries with a contact you choose. This toggle is a local prototype state only.</p></div><button className={`switch ${shareFamily ? 'switch-on' : ''}`} role="switch" aria-checked={shareFamily} onClick={() => setShareFamily(!shareFamily)}><span/></button></div><div className="privacy-control"><div className="privacy-control-icon"><BellRing size={19}/></div><div className="privacy-control-copy"><strong>Follow-up reminders</strong><p>Opt in to a future reminder workflow. No message will be sent by this prototype.</p></div><button className={`switch ${reminders ? 'switch-on' : ''}`} role="switch" aria-checked={reminders} onClick={() => setReminders(!reminders)}><span/></button></div></section><div className="privacy-data-grid"><div><span className="privacy-data-number">01</span><strong>Minimum necessary</strong><p>Collect only the information required for the immediate task.</p></div><div><span className="privacy-data-number">02</span><strong>Visible boundaries</strong><p>Explain what the system can and cannot do in plain language.</p></div><div><span className="privacy-data-number">03</span><strong>Honest status</strong><p>Never claim data was deleted, shared or booked unless the backend confirms it.</p></div></div><div className="privacy-save-row"><div>{saved && <span className="save-confirmation"><CheckCircle2 size={15}/> Prototype preferences saved in this page state.</span>}</div><button className="button button-primary" onClick={onSave}>Save demo preferences <Check size={15}/></button></div><div className="matching-caveat"><ShieldCheck size={16}/><p>Do not enter real patient information in demo mode. Before deployment, document retention, access controls, logging, third-party speech processing and deletion behavior accurately.</p></div></div>;
}

function BookingModal({ caregiver, selectedTime, onTimeChange, message, onConfirm, onClose }: { caregiver: Caregiver; selectedTime: string; onTimeChange: (value: string) => void; message: string; onConfirm: () => void; onClose: () => void }) {
  return <div className="modal-backdrop" role="presentation"><section className="booking-modal" role="dialog" aria-modal="true" aria-labelledby="booking-title"><button className="modal-close" onClick={onClose} aria-label="Close booking"><X size={19}/></button><div className="privacy-icon booking-modal-icon"><CalendarClock size={24}/></div><div className="eyebrow">DEMO BOOKING REQUEST</div><h2 id="booking-title">Request a care slot.</h2><p>Choose a preferred time for the demo flow. No provider is contacted and no real appointment will be created.</p><div className="booking-caregiver-summary"><div className="caregiver-avatar">{caregiver.name.split(' ').map((part) => part[0]).join('').replace('.', '').slice(0,2)}</div><div><strong>{caregiver.name}</strong><span>{caregiver.role} · Synthetic profile</span></div></div><label className="booking-label">Preferred time<select value={selectedTime} onChange={(event) => onTimeChange(event.target.value)}><option>{caregiver.availability}</option><option>First available</option><option>Tomorrow morning</option><option>Tomorrow afternoon</option></select></label>{message ? <div className="booking-confirmation"><CheckCircle2 size={17}/><span>{message}</span></div> : <button className="button button-primary button-full" onClick={onConfirm}>Create demo request <ArrowRight size={16}/></button>}<button className="button button-ghost button-full" onClick={onClose}>Close</button></section></div>;
}

export default App;
