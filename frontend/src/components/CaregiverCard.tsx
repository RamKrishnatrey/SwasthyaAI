import { ArrowUpRight, BadgeCheck, CalendarClock, Languages, MapPin, ShieldCheck, Star } from 'lucide-react';
import type { Caregiver } from '../types/agent';
import { rankCaregiver } from '../utils/rankingFormula';

interface CaregiverCardProps {
  caregiver: Caregiver;
  onBook?: (caregiver: Caregiver) => void;
  compact?: boolean;
  demoProfile?: boolean;
}

export function CaregiverCard({ caregiver, onBook, compact = false, demoProfile = true }: CaregiverCardProps) {
  const ranked = rankCaregiver(caregiver);
  return (
    <article className={`caregiver-card ${compact ? 'caregiver-card-compact' : ''}`}>
      <div className="caregiver-card-top">
        <div className={`caregiver-avatar caregiver-avatar-${caregiver.id.slice(-1)}`}>{caregiver.name.split(' ').map((part) => part[0]).join('').replace('.', '').slice(0, 2)}</div>
        <div className="caregiver-identity">
          <div className="caregiver-name-line"><h3>{caregiver.name}</h3>{demoProfile && <span className="demo-tag">Demo profile</span>}</div>
          <p>{caregiver.role}</p>
        </div>
        <div className="match-score"><strong>{Math.round(ranked.score * 100)}</strong><span>match score</span></div>
      </div>
      <div className="caregiver-attributes">
        <span><MapPin size={14}/>{caregiver.distanceKm.toFixed(1)} km away</span>
        <span><Languages size={14}/>{caregiver.languages.join(' · ')}</span>
        <span><CalendarClock size={14}/>{caregiver.availability}</span>
        <span><Star size={14}/>{caregiver.rating.toFixed(1)} <small>({caregiver.reviewCount})</small></span>
      </div>
      <div className="skill-tags">{caregiver.skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
      <div className="caregiver-qualification"><ShieldCheck size={14}/><span>{caregiver.verified ? 'Verification status provided by API' : 'Demo profile · qualifications not verified'}</span></div>
      {!compact && <div className="match-reasons"><strong><BadgeCheck size={15}/> Why this match</strong><p>Skill fit, service distance, slot suitability, language and rating contribute to the illustrative ranking. Mandatory eligibility checks must be completed separately.</p></div>}
      <div className="caregiver-card-actions">
        <button className="text-button" onClick={() => window.dispatchEvent(new CustomEvent('swasthya:show-ranking'))}>View match details <ArrowUpRight size={15}/></button>
        {onBook && <button className="button button-primary button-small" onClick={() => onBook(caregiver)}>Request a slot</button>}
      </div>
    </article>
  );
}
