# 2-Minute Video Walkthrough Script

## 0:00–0:15 — Problem
"Hi, I'm Thanishka. For the Caprae Full Stack Developer pre-work, I focused on one high-impact
problem: turning a broad set of potential prospects into a prioritized outreach queue.

SaaSquatch already provides company search, enrichment, filtering and export capabilities. My
goal was not to rebuild the whole platform in five hours, but to add a layer that helps a user
decide which leads are worth contacting first."

## 0:15–0:45 — Product demo
"Here is the dashboard. The top metrics show the total leads, high-priority leads and the number
currently visible.

I can filter by industry, search by location, set a minimum lead score, and change the sorting
logic. The table immediately updates and shows the company, industry, location, size, growth and
score.

I'll click a lead to open the profile. The important part here is that the score is explainable:
the user can see why a company was prioritized instead of receiving an unexplained AI number."

## 0:45–1:15 — Technical decisions
"On the frontend I used React with Vite. The backend is FastAPI with Pydantic-style API contracts,
and the data layer uses SQLAlchemy with SQLite for this time-boxed prototype.

The API performs server-side filtering and sorting so the browser doesn't have to process the
entire dataset. I also added database indexes on common filtering and ranking fields.

For production, I would move to PostgreSQL, introduce Redis for repeated queries and enrichment
caching, and run enrichment jobs asynchronously so third-party API calls don't block the user."

## 1:15–1:40 — Business value
"The scoring model combines company size, estimated revenue, growth, industry fit and technology
signals. It is deliberately deterministic and explainable.

That means a sales or search-fund team can quickly focus on high-fit accounts, understand the
reason behind the ranking, and export the prioritized queue into their existing workflow."

## 1:40–2:00 — Closing
"I intentionally chose quality over quantity because the handbook limits development time to five
hours. The result is a focused workflow rather than a large collection of unfinished features.

If I had more time, my next steps would be real data-source connectors, stronger deduplication and
enrichment, provenance tracking, async jobs, CRM integration and production authentication.

Thank you."