from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, String, Integer, Float, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import csv
import io
import re

DATABASE_URL = "sqlite:///./leads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(120), index=True)
    domain: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    industry: Mapped[str] = mapped_column(String(80), index=True)
    location: Mapped[str] = mapped_column(String(100), index=True)
    employees: Mapped[int] = mapped_column(Integer, index=True)
    revenue_m: Mapped[float] = mapped_column(Float)
    growth_pct: Mapped[float] = mapped_column(Float)
    tech_signal: Mapped[str] = mapped_column(String(120))
    decision_maker: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160))
    linkedin: Mapped[str] = mapped_column(String(240))
    score: Mapped[int] = mapped_column(Integer, index=True)
    reason: Mapped[str] = mapped_column(String(500))

Base.metadata.create_all(engine)

DEMO = [
("Northstar Medical","northstarmedical.example","Healthcare","Austin, TX",185,42.0,18.5,"Cloud + analytics","CEO","alex@northstarmedical.example"),
("BluePeak Logistics","bluepeaklogistics.example","Logistics","Dallas, TX",310,68.0,24.2,"ERP + API","Founder","maya@bluepeaklogistics.example"),
("CedarWorks Dental","cedarworksdental.example","Healthcare","Phoenix, AZ",92,16.5,9.1,"Cloud practice software","Owner","sam@cedarworksdental.example"),
("Summit Industrial","summitindustrial.example","Manufacturing","Chicago, IL",540,120.0,12.8,"ERP + automation","President","jordan@summitindustrial.example"),
("Harbor IT Services","harborit.example","IT Services","Tampa, FL",74,11.0,21.4,"AWS + Microsoft 365","CEO","casey@harborit.example"),
("Redwood Security","redwoodsecurity.example","Cybersecurity","Denver, CO",155,35.0,31.6,"Cloud security stack","Founder","riley@redwoodsecurity.example"),
("Atlas Accounting","atlasaccounting.example","Business Services","Atlanta, GA",118,22.0,15.2,"QuickBooks + cloud","Managing Partner","taylor@atlasaccounting.example"),
("Evergreen Facilities","evergreenfacilities.example","Business Services","Seattle, WA",260,51.0,17.9,"ERP + field ops","Owner","jamie@evergreenfacilities.example"),
("Lighthouse Testing","lighthousetesting.example","Healthcare","Boston, MA",205,47.0,27.5,"LIMS + cloud","CEO","morgan@lighthousetesting.example"),
("IronGate Components","irongatecomponents.example","Manufacturing","Detroit, MI",430,96.0,8.7,"ERP + robotics","President","drew@irongatecomponents.example"),
("Pinecrest Staffing","pinecreststaffing.example","Business Services","Charlotte, NC",67,14.0,26.1,"ATS + CRM","Founder","lee@pinecreststaffing.example"),
("Clearwater HVAC","clearwaterhvac.example","Home Services","Orlando, FL",145,29.0,22.7,"Field service SaaS","Owner","pat@clearwaterhvac.example"),
("Vertex Packaging","vertexpackaging.example","Manufacturing","Columbus, OH",385,81.0,14.4,"ERP + MES","CEO","dev@vertexpackaging.example"),
("Oak & Stone Wealth","oakstonewealth.example","Financial Services","New York, NY",58,13.0,7.4,"CRM + analytics","Managing Partner","erin@oakstonewealth.example"),
("Silverline Freight","silverlinefreight.example","Logistics","Memphis, TN",225,44.0,19.8,"TMS + API","Founder","chris@silverlinefreight.example"),
("BrightPath Pediatrics","brightpathpediatrics.example","Healthcare","Raleigh, NC",130,26.0,16.3,"Cloud EHR","Owner","kim@brightpathpediatrics.example"),
("WestBridge Consulting","westbridgeconsulting.example","Business Services","San Diego, CA",83,18.0,29.3,"Cloud CRM","Founder","avery@westbridgeconsulting.example"),
("Granite Energy Services","graniteenergy.example","Energy","Houston, TX",620,145.0,11.2,"ERP + IoT","CEO","robin@graniteenergy.example"),
("Metro Fleet Repair","metrofleetrepair.example","Automotive","Kansas City, MO",96,19.0,23.5,"Fleet management SaaS","Owner","quinn@metrofleetrepair.example"),
("Cobalt Data Systems","cobaltdata.example","IT Services","San Jose, CA",245,59.0,34.2,"AWS + data platform","Founder","blake@cobaltdata.example"),
]

def score_lead(x):
    score = 0
    reasons = []
    # Fit: targetable lower-middle-market style profile
    if 50 <= x.employees <= 500:
        score += 20; reasons.append("50–500 employees")
    elif x.employees <= 800:
        score += 10
    if x.revenue_m >= 20:
        score += 20; reasons.append(">$20M estimated revenue")
    elif x.revenue_m >= 10:
        score += 10
    if x.growth_pct >= 20:
        score += 25; reasons.append("20%+ growth signal")
    elif x.growth_pct >= 10:
        score += 12
    if x.industry in {"Healthcare","Manufacturing","Business Services","Logistics","IT Services"}:
        score += 15; reasons.append("priority industry")
    if any(k in x.tech_signal.lower() for k in ["cloud","api","automation","analytics"]):
        score += 10; reasons.append("technology/modernization signal")
    return min(score, 100), " • ".join(reasons[:4]) or "Baseline fit"

def seed():
    with Session(engine) as s:
        if s.scalar(select(func.count()).select_from(Lead)):
            return
        for i, row in enumerate(DEMO, 1):
            company, domain, industry, location, employees, revenue, growth, tech, dm, email = row
            obj = Lead(id=i, company=company, domain=domain, industry=industry, location=location,
                       employees=employees, revenue_m=revenue, growth_pct=growth, tech_signal=tech,
                       decision_maker=dm, email=email,
                       linkedin="https://www.linkedin.com/search/results/people/?keywords="+company.replace(" ","%20"))
            obj.score, obj.reason = score_lead(obj)
            s.add(obj)
        s.commit()

seed()

app = FastAPI(title="Caprae Lead Intelligence API", version="1.0.0")

def normalize_domain(value):
    return re.sub(r"^www\.", "", value.strip().lower())

@app.get("/api/health")
def health():
    return {"status":"ok","service":"caprae-lead-intelligence"}

@app.get("/api/stats")
def stats():
    with Session(engine) as s:
        total = s.scalar(select(func.count()).select_from(Lead))
        high = s.scalar(select(func.count()).select_from(Lead).where(Lead.score >= 70))
        industries = s.execute(select(Lead.industry, func.count()).group_by(Lead.industry).order_by(func.count().desc())).all()
        return {"total": total, "high_priority": high, "industries": [{"name":a,"count":b} for a,b in industries]}

@app.get("/api/leads")
def leads(
    industry: str | None = None,
    location: str | None = None,
    min_employees: int | None = None,
    max_employees: int | None = None,
    min_revenue: float | None = None,
    min_score: int | None = None,
    sort: str = Query("score_desc", pattern="^(score_desc|growth_desc|revenue_desc|employees_desc)$"),
    limit: int = Query(100, le=200)
):
    with Session(engine) as s:
        q = select(Lead)
        if industry and industry != "All":
            q = q.where(Lead.industry == industry)
        if location:
            q = q.where(Lead.location.ilike(f"%{location}%"))
        if min_employees is not None: q = q.where(Lead.employees >= min_employees)
        if max_employees is not None: q = q.where(Lead.employees <= max_employees)
        if min_revenue is not None: q = q.where(Lead.revenue_m >= min_revenue)
        if min_score is not None: q = q.where(Lead.score >= min_score)
        order = {
            "score_desc": Lead.score.desc(),
            "growth_desc": Lead.growth_pct.desc(),
            "revenue_desc": Lead.revenue_m.desc(),
            "employees_desc": Lead.employees.desc()
        }[sort]
        rows = s.scalars(q.order_by(order).limit(limit)).all()
        return [{
            "id":r.id,"company":r.company,"domain":normalize_domain(r.domain),"industry":r.industry,
            "location":r.location,"employees":r.employees,"revenue_m":r.revenue_m,
            "growth_pct":r.growth_pct,"tech_signal":r.tech_signal,"decision_maker":r.decision_maker,
            "email":r.email,"linkedin":r.linkedin,"score":r.score,"reason":r.reason
        } for r in rows]

@app.get("/api/leads/{lead_id}")
def lead_detail(lead_id: int):
    with Session(engine) as s:
        r = s.get(Lead, lead_id)
        if not r:
            return {"error":"Lead not found"}
        return {"id":r.id,"company":r.company,"domain":normalize_domain(r.domain),"industry":r.industry,
                "location":r.location,"employees":r.employees,"revenue_m":r.revenue_m,
                "growth_pct":r.growth_pct,"tech_signal":r.tech_signal,"decision_maker":r.decision_maker,
                "email":r.email,"linkedin":r.linkedin,"score":r.score,"reason":r.reason}

@app.get("/api/export.csv")
def export_csv(
    min_score: int = 0,
):
    with Session(engine) as s:
        rows = s.scalars(select(Lead).where(Lead.score >= min_score).order_by(Lead.score.desc())).all()
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["company","domain","industry","location","employees","revenue_m","growth_pct",
                         "tech_signal","decision_maker","email","score","reason"])
        for r in rows:
            writer.writerow([r.company,normalize_domain(r.domain),r.industry,r.location,r.employees,
                             r.revenue_m,r.growth_pct,r.tech_signal,r.decision_maker,r.email,r.score,r.reason])
        out.seek(0)
        return StreamingResponse(iter([out.getvalue()]), media_type="text/csv",
                                 headers={"Content-Disposition":"attachment; filename=prioritized_leads.csv"})