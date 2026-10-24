from __future__ import annotations
import os, re
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import joblib

BASE=Path(__file__).resolve().parent
MODEL=Path(os.getenv("SWASTHYAAI_MODEL_PATH",BASE/"models"/"urgency_model.joblib"))
app=FastAPI(title="SwasthyaAI Agent v2",version="2.0.0",description="Experimental care navigation prototype; not a diagnostic tool.")

# This conservative phrase list is an adjunct only, not a complete emergency screen.
RED_FLAGS={
 "possible_chest_pain":[r"\bchest pain\b",r"\bpain in (?:my |the )?chest\b",r"सीने में दर्द",r"chhati mein dard"],
 "possible_breathing_emergency":[r"\bcan't breathe\b",r"\bcannot breathe\b",r"\bdifficulty breathing\b",r"\bshortness of breath\b",r"सांस लेने में दिक्कत",r"saans nahi aa rahi"],
 "possible_stroke":[r"\bface droop(?:ing)?\b",r"\bslurred speech\b",r"\bstroke\b",r"चेहरा टेढ़ा",r"बोलने में दिक्कत"],
 "unconsciousness":[r"\bunconscious\b",r"\bunresponsive\b",r"\bpassed out\b",r"\bbehosh\b",r"बेहोश"],
 "severe_bleeding":[r"\bsevere bleeding\b",r"\bbleeding (?:won't|will not|is not) stop\b",r"खून नहीं रुक"],
 "seizure":[r"\bseizure\b",r"\bconvulsion\b",r"\bdaura\b",r"दौरा"],
 "self_harm_risk":[r"\bsuicid(?:e|al)\b",r"\bkill myself\b",r"\bend my life\b",r"\bself[- ]harm\b",r"आत्महत्या",r"khudkushi"]
}
NEG=re.compile(r"(?:\bno\b|\bnot having\b|\bwithout\b|\bdenies\b|नहीं|नही)\s*$",re.I)

def detect_red_flags(text:str)->list[str]:
    s=" ".join(text.casefold().split()); found=[]
    for flag,patterns in RED_FLAGS.items():
        for pattern in patterns:
            m=re.search(pattern,s,re.I)
            if m:
                before=s[max(0,m.start()-24):m.start()]
                after=s[m.end():m.end()+20]
                if NEG.search(before) or re.match(r"\s*(?:is )?(?:absent|resolved|gone)",after,re.I): continue
                found.append(flag); break
    return found

def predict_urgency(text:str):
    if not MODEL.is_file():
        return {"status":"unavailable","label":None,"notice":"Experimental model has not been trained; see README."}
    try:
        model=joblib.load(MODEL)
        return {"status":"experimental","label":str(model.predict([text])[0]),
                "notice":"Predicts dataset labels only; not validated clinical triage."}
    except Exception:
        return {"status":"unavailable","label":None,"notice":"Model unavailable; human review required."}

class Intake(BaseModel):
    message:str=Field(min_length=1,max_length=3000)
    language:str=Field(default="auto",max_length=32)

def demo_caregivers():
    # Fictional demo profiles only. Never present as real available clinicians.
    return [
      {"id":"DEMO-NURSE-01","qualification":"Registered nurse (fictional demo)","skills":["nursing","wound care"],"languages":["English","Hindi"],"available":True,"rating":4.8,"distance_km":2.4},
      {"id":"DEMO-PARAMEDIC-02","qualification":"Paramedic (fictional demo)","skills":["first aid","assessment"],"languages":["English","Hinglish"],"available":True,"rating":4.6,"distance_km":4.1},
      {"id":"DEMO-TELE-03","qualification":"Teleconsultation provider (fictional demo)","skills":["teleconsultation"],"languages":["English","Hindi","Hinglish"],"available":True,"rating":4.7,"distance_km":None}
    ]

@app.get("/api/health")
def health():
    return {"ok":True,"model_available":MODEL.is_file(),"service":"swasthyaai-agent-v2"}

@app.post("/api/agent")
def agent(q:Intake):
    flags=detect_red_flags(q.message)
    # Emergency path deliberately returns before model inference or caregiver matching.
    if flags:
        return {"status":"emergency_review","safety_flags":flags,"urgency_prediction":None,"follow_up_question":None,"caregivers":[],
          "response":"A possible emergency warning sign was detected. Contact your local emergency number now; do not wait for this app. Automated checks can miss emergencies.",
          "needs_human_review":True}
    if len(q.message.split())<5:
        return {"status":"needs_follow_up","safety_flags":[],"urgency_prediction":None,
          "follow_up_question":"What symptoms do you have, when did they start, and are they getting worse?","caregivers":[],
          "response":"Please provide more detail. Do not delay urgent care to answer.","needs_human_review":True}
    prediction=predict_urgency(q.message)
    lang=q.language if q.language in ("English","Hindi","Hinglish") else "English"
    matches=[c for c in demo_caregivers() if c["available"] and lang in c["languages"]]
    matches.sort(key=lambda c:c["rating"],reverse=True)
    return {"status":"decision_support","safety_flags":[],"urgency_prediction":prediction,"follow_up_question":None,
      "caregivers":matches,"response":"Experimental navigation support only. A qualified healthcare professional must assess your situation. Seek urgent help for severe, sudden, or worsening symptoms.",
      "needs_human_review":True}

@app.get("/",response_class=HTMLResponse)
def index():
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SwasthyaAI Care Navigation</title><style>
:root{color-scheme:dark;--bg:#091522;--line:#284459;--text:#f3f7fb;--muted:#afc2d1;--mint:#74f0c0;--pink:#ff8f9b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#173b51,transparent 35%),var(--bg);font:16px/1.5 system-ui;color:var(--text)}main{max-width:900px;margin:auto;padding:30px 18px 55px}.brand{color:var(--mint);font-weight:800;letter-spacing:.1em}h1{font-size:clamp(2rem,7vw,4rem);line-height:1.04}.panel{background:linear-gradient(145deg,#132c40,#0c1e2e);border:1px solid var(--line);border-radius:20px;padding:22px;margin:18px 0}.notice{border-left:3px solid var(--pink);background:#3a2028;padding:12px;border-radius:8px}label{display:block;font-weight:700;margin:14px 0 7px}textarea,select{width:100%;background:#081725;color:white;border:1px solid #36536a;border-radius:12px;padding:13px;font:inherit}textarea{min-height:140px}button{background:var(--mint);color:#08201a;font-weight:800;border:0;border-radius:12px;padding:13px 18px;margin-top:15px;cursor:pointer}.muted{color:var(--muted)}.card{border:1px solid var(--line);border-radius:12px;padding:12px;margin:10px 0}footer{font-size:.85rem;color:var(--muted)}
</style><main><div class="brand">SWASTHYAAI / CARE NAVIGATION</div><h1>Care starts with<br>being heard.</h1><p class="muted">Experimental navigation support in English, Hindi, or Hinglish. Not a diagnosis or prescription.</p><div class="notice">If this may be an emergency, call your local emergency number now. Do not wait for this app.</div>
<section class="panel"><form id="f"><label for="m">Describe what is happening</label><textarea id="m" required maxlength="3000" placeholder="Symptoms, when they began, and whether they are worsening…"></textarea><label for="l">Language</label><select id="l"><option>English</option><option>Hindi</option><option>Hinglish</option><option>auto</option></select><button id="b">Review safely →</button></form></section>
<section class="panel" id="out" hidden><h2>Agent response</h2><p id="r"></p><div id="d"></div></section><footer>Prototype only · Demo caregiver profiles are fictional · Labels are not clinically validated · Never enter real patient information.</footer></main>
<script>const f=document.querySelector('#f'),b=document.querySelector('#b'),out=document.querySelector('#out'),r=document.querySelector('#r'),d=document.querySelector('#d');f.onsubmit=async e=>{e.preventDefault();b.disabled=true;out.hidden=false;r.textContent='Checking…';d.replaceChildren();try{let res=await fetch('/api/agent',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:document.querySelector('#m').value,language:document.querySelector('#l').value})});let x=await res.json();r.textContent=x.response+'\n\nStatus: '+x.status+'\nSafety flags: '+(x.safety_flags.join(', ')||'None detected; this does not rule out an emergency')+'\nUrgency experiment: '+(x.urgency_prediction?.label??'Not run');if(x.follow_up_question){let p=document.createElement('p');p.textContent='Follow-up: '+x.follow_up_question;d.append(p)}for(let c of x.caregivers||[]){let el=document.createElement('div');el.className='card';el.textContent=c.qualification+' · '+c.languages.join(', ')+' · demo rating '+c.rating;d.append(el)}}catch(e){r.textContent='API unavailable. Try later; seek professional or emergency care when needed.'}finally{b.disabled=false}};</script></html>"""

