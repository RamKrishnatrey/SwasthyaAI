import { Activity, ArrowUpRight, CircleHelp, Moon, ShieldCheck } from 'lucide-react';
import type { Language } from '../types/agent';
import { translations } from '../i18n/translations';

interface NavbarProps {
  language: Language;
  onLanguageChange: (language: Language) => void;
  elderCare: boolean;
  onElderCareChange: (value: boolean) => void;
  onPrivacy: () => void;
  demoMode: boolean;
}

export function Navbar({ language, onLanguageChange, elderCare, onElderCareChange, onPrivacy, demoMode }: NavbarProps) {
  const t = translations[language];
  return (
    <header className="topbar">
      <div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>{t.overview}</strong></div>
      <div className="topbar-actions">
        {demoMode && <span className="demo-status"><span className="pulse-dot" /> Demo environment</span>}
        <label className="language-select"><span className="sr-only">Choose language</span>
          <select value={language} onChange={(event) => onLanguageChange(event.target.value as Language)} aria-label="Choose language">
            <option value="en">EN · English</option><option value="hi">HI · हिन्दी</option><option value="hinglish">Hinglish</option>
          </select>
        </label>
        <button className={`utility-toggle ${elderCare ? 'utility-toggle-active' : ''}`} onClick={() => onElderCareChange(!elderCare)} aria-pressed={elderCare} title="Toggle ElderCare Mode">
          <Moon size={15} /> <span>ElderCare</span>
        </button>
        <button className="icon-button" title="Privacy and safety" onClick={onPrivacy}><ShieldCheck size={18} /></button>
        <button className="icon-button" title="Help and limitations" onClick={onPrivacy}><CircleHelp size={18} /></button>
        <div className="avatar" aria-label="Demo profile">S</div>
      </div>
    </header>
  );
}

export function BrandMark() {
  return <div className="brand-mark" aria-hidden="true"><Activity size={23} strokeWidth={2.2} /><span className="brand-mark-spark">✳</span></div>;
}

export function BottomNotice() {
  return <div className="bottom-notice"><ShieldCheck size={14}/><span>Designed for care navigation, with safety and clarity at its core.</span><ArrowUpRight size={13}/></div>;
}
