import { ChevronDown, FileCheck2, Info, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface ExplainabilityPanelProps {
  explanations: string[];
  title?: string;
}

export function ExplainabilityPanel({ explanations, title = 'Why this result?' }: ExplainabilityPanelProps) {
  const [expanded, setExpanded] = useState(false);
  return (
    <section className="explainability-panel">
      <button className="explainability-trigger" onClick={() => setExpanded((current) => !current)} aria-expanded={expanded}>
        <span className="explainability-icon"><FileCheck2 size={17}/></span><span className="explainability-title">{title}<small>Understand the factors behind this screen</small></span><ChevronDown className={expanded ? 'rotate-icon' : ''} size={17}/>
      </button>
      {expanded && <div className="explainability-body">{(explanations.length ? explanations : ['No explanation was returned by the connected agent.']).map((line, index) => <div className="explanation-line" key={`${line}-${index}`}><ShieldCheck size={15}/><span>{line}</span></div>)}<div className="explanation-footnote"><Info size={14}/> Explanations are based only on returned application data; they are not independent medical verification.</div></div>}
    </section>
  );
}
