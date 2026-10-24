import { Check, LockKeyhole, X } from 'lucide-react';

interface PrivacyDisclaimerModalProps { onClose: () => void }

export function PrivacyDisclaimerModal({ onClose }: PrivacyDisclaimerModalProps) {
  return (
    <div className="modal-backdrop" role="presentation">
      <section className="privacy-modal" role="dialog" aria-modal="true" aria-labelledby="privacy-title">
        <button className="modal-close" onClick={onClose} aria-label="Close privacy information"><X size={19}/></button>
        <div className="privacy-icon"><LockKeyhole size={25}/></div>
        <div className="eyebrow">PRIVACY & LIMITATIONS</div>
        <h2 id="privacy-title">Your care story stays yours.</h2>
        <p>This interface is a hackathon prototype. Please do not enter real personal or medical information into demo mode.</p>
        <div className="privacy-list"><div><Check size={16}/><span>Demo uses synthetic caregiver profiles.</span></div><div><Check size={16}/><span>Optional sharing should be consent-based in the integrated product.</span></div><div><Check size={16}/><span>Actual retention depends on the connected backend and services.</span></div><div><Check size={16}/><span>This tool does not diagnose, prescribe or replace professional care.</span></div></div>
        <button className="button button-primary button-full" onClick={onClose}>Got it</button>
      </section>
    </div>
  );
}
