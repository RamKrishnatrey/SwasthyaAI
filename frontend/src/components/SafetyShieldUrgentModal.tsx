import { AlertOctagon, ArrowUpRight, PhoneCall, ShieldAlert, X } from 'lucide-react';
import type { AgentResponse } from '../types/agent';

interface SafetyShieldUrgentModalProps {
  result: AgentResponse | null;
  onClose: () => void;
}

export function SafetyShieldUrgentModal({ result, onClose }: SafetyShieldUrgentModalProps) {
  if (!result || result.status !== 'possible_emergency') return null;
  return (
    <div className="modal-backdrop" role="presentation">
      <section className="urgent-modal" role="alertdialog" aria-modal="true" aria-labelledby="urgent-title" aria-describedby="urgent-description">
        <button className="modal-close" onClick={onClose} aria-label="Close urgent information"><X size={19}/></button>
        <div className="urgent-icon"><AlertOctagon size={30}/></div>
        <div className="eyebrow eyebrow-red"><span className="pulse-dot pulse-dot-red"/> SAFETYSHIELD · DEMO ALERT</div>
        <h2 id="urgent-title">Please don't wait for this app.</h2>
        <p id="urgent-description">A possible emergency warning phrase was detected. If someone may be in immediate danger, contact local emergency services now. Do not continue ordinary caregiver matching.</p>
        <div className="urgent-action"><PhoneCall size={19}/><div><strong>India emergency number: 112</strong><span>Use the emergency number applicable to your location. Do not rely on this prototype for emergency assessment.</span></div><ArrowUpRight size={17}/></div>
        <div className="urgent-note"><ShieldAlert size={16}/><span>{result.safety.message || 'This demo trigger is not a clinically validated triage assessment.'}</span></div>
        <button className="button button-dark button-full" onClick={onClose}>I understand</button>
      </section>
    </div>
  );
}
