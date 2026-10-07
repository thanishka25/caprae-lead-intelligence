import React, {useEffect, useMemo, useState} from "react";
import {createRoot} from "react-dom/client";
import {Search, Download, SlidersHorizontal, ArrowUpRight, Zap, Target, Database, Sparkles} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function App(){
  const [leads,setLeads]=useState([]);
  const [stats,setStats]=useState({total:0,high_priority:0,industries:[]});
  const [industry,setIndustry]=useState("All");
  const [location,setLocation]=useState("");
  const [minScore,setMinScore]=useState(0);
  const [sort,setSort]=useState("score_desc");
  const [loading,setLoading]=useState(false);
  const [selected,setSelected]=useState(null);

  const load = async ()=>{
    setLoading(true);
    const p = new URLSearchParams({sort, min_score:String(minScore)});
    if(industry!=="All") p.set("industry",industry);
    if(location) p.set("location",location);
    const [a,b] = await Promise.all([fetch(`${API}/leads?${p}`),fetch(`${API}/stats`)]);
    setLeads(await a.json()); setStats(await b.json()); setLoading(false);
  };
  useEffect(()=>{load()},[industry,location,minScore,sort]);

  const industries = useMemo(()=>["All",...stats.industries.map(x=>x.name)], [stats]);

  return <div className="app">
    <header className="topbar">
      <div className="brand"><div className="logo">C</div><div><strong>CAPRAE</strong><span>LEAD INTELLIGENCE</span></div></div>
      <div className="header-note"><span className="dot"/> Demo workspace · synthetic data</div>
    </header>

    <main>
      <section className="hero">
        <div>
          <div className="eyebrow"><Sparkles size={14}/> OUTREACH PRIORITIZATION</div>
          <h1>Find the leads worth<br/><em>calling first.</em></h1>
          <p>Turn a broad prospect list into an explainable, ranked outreach queue using firmographic fit and growth signals.</p>
        </div>
        <a className="export" href={`${API}/export.csv?min_score=${minScore}`}><Download size={17}/> Export CSV</a>
      </section>

      <section className="metrics">
        <Metric icon={<Database/>} label="TOTAL LEADS" value={stats.total}/>
        <Metric icon={<Target/>} label="HIGH PRIORITY" value={stats.high_priority}/>
        <Metric icon={<Zap/>} label="VISIBLE NOW" value={leads.length}/>
      </section>

      <section className="panel filters">
        <div className="filter-title"><SlidersHorizontal size={18}/> ICP filters</div>
        <div className="fields">
          <label>Industry<select value={industry} onChange={e=>setIndustry(e.target.value)}>{industries.map(i=><option key={i}>{i}</option>)}</select></label>
          <label>Location<input value={location} onChange={e=>setLocation(e.target.value)} placeholder="e.g. Texas"/></label>
          <label>Minimum score<input type="range" min="0" max="100" step="5" value={minScore} onChange={e=>setMinScore(e.target.value)}/><b>{minScore}</b></label>
          <label>Sort<select value={sort} onChange={e=>setSort(e.target.value)}>
            <option value="score_desc">Lead score</option><option value="growth_desc">Growth</option>
            <option value="revenue_desc">Revenue</option><option value="employees_desc">Employees</option>
          </select></label>
        </div>
      </section>

      <section className="panel">
        <div className="table-head"><div><h2>Priority queue</h2><span>{loading?"Refreshing…":`${leads.length} leads match your criteria`}</span></div><div className="search-pill"><Search size={15}/> Ranked by fit</div></div>
        <div className="table-wrap"><table><thead><tr>
          <th>Company</th><th>Industry</th><th>Location</th><th>Size</th><th>Growth</th><th>Score</th><th></th>
        </tr></thead><tbody>
        {leads.map(l=><tr key={l.id} onClick={()=>setSelected(l)}>
          <td><div className="company"><div className="avatar">{l.company[0]}</div><div><strong>{l.company}</strong><small>{l.domain}</small></div></div></td>
          <td>{l.industry}</td><td>{l.location}</td><td>{l.employees.toLocaleString()}</td><td><span className="growth">+{l.growth_pct}%</span></td>
          <td><span className={`score ${l.score>=70?"hot":l.score>=50?"warm":""}`}>{l.score}</span></td>
          <td><ArrowUpRight size={17}/></td>
        </tr>)}
        </tbody></table></div>
      </section>

      <section className="insight"><div className="insight-icon"><Sparkles/></div><div><strong>Why this approach?</strong><p>The scoring model is deterministic and explainable: fit, revenue, growth, priority industries and technology signals each contribute to a lead score. That makes the queue useful for sales decisions without hiding the logic behind a black box.</p></div></section>
    </main>

    {selected && <div className="modal-bg" onClick={()=>setSelected(null)}><div className="modal" onClick={e=>e.stopPropagation()}>
      <button className="close" onClick={()=>setSelected(null)}>×</button>
      <div className="modal-top"><div className="avatar big">{selected.company[0]}</div><div><div className="eyebrow">LEAD PROFILE</div><h2>{selected.company}</h2><p>{selected.domain}</p></div><span className="score hot bigscore">{selected.score}</span></div>
      <div className="grid"><Info label="Industry" value={selected.industry}/><Info label="Location" value={selected.location}/><Info label="Employees" value={selected.employees}/><Info label="Est. revenue" value={`$${selected.revenue_m}M`}/><Info label="Decision maker" value={selected.decision_maker}/><Info label="Technology signal" value={selected.tech_signal}/></div>
      <div className="reason"><strong>Why prioritize this lead</strong><p>{selected.reason}</p></div>
      <a className="contact" href={`mailto:${selected.email}`}>Email {selected.decision_maker} →</a>
    </div></div>}
  </div>
}

function Metric({icon,label,value}){return <div className="metric"><div className="metric-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong></div></div>}
function Info({label,value}){return <div><small>{label}</small><strong>{value}</strong></div>}

createRoot(document.getElementById("root")).render(<App/>);