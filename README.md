# 📊 Real-Time AI Stock Sentiment Dashboard

An end-to-end system that combines **live stock market data** with **AI-driven sentiment & emotion analysis** from financial news and social media.\
Built to demonstrate **full-stack engineering**, **streaming pipelines**, and **applied AI/ML in finance**.

---

## 🚀 Features

### MVP

- Manage stock watchlists & thresholds
- Real-time(ish) price polling (yfinance/Polygon/IEX)
- Intraday min/max & rolling averages
- Threshold alerts with WebSocket updates
- Interactive React dashboard (sparklines, alert toasts)

### V1 – AI Insights

- Ingest financial news, Reddit, and X (Twitter) posts
- Deduplicate & classify relevance per ticker
- Hugging Face sentiment (polarity) + emotion tagging
- LangChain-powered daily per-ticker news summaries
- Timeline view aligning news sentiment with price movement

### V2 – Advanced

- Real-time pipelines (Kafka/Redis Streams)
- Backtesting signals against historical data
- Paper trading with PnL tracking
- Explainable AI rationales (e.g. “Positive headline ↑ before price ↑”)

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, LangChain, Hugging Face
- **Streaming**: Kafka / Redpanda (or Redis Pub/Sub/WebSockets)
- **Frontend**: React + Vite/Next.js, Recharts/Chart.js
- **Database**: PostgreSQL + TimescaleDB (time-series)
- **Infra**: Docker Compose, GitHub Actions CI, optional cloud deploy (Fly.io/Render)

---

## 🏗️ Architecture

```
[Sources: Prices | Reddit | X | News]
        │
        ▼
   Ingestion Jobs / Streams (pollers, RSS, scrapers)
        │
        ▼
 Message Bus (Kafka/Redis Streams) ── fallback: in-proc queues
        │
        ├─► NLP Workers (HF/LangChain): relevance → sentiment → emotion → summary
        ├─► Signal Engine: price deltas × sentiment spikes → alerts
        └─► Storage (Postgres/Timescale)
                    │
                    ▼
            FastAPI (REST + WebSockets)
                    │
                    ▼
               React Dashboard
```

---

## 📂 Project Structure

```
/project
  ├── api/        # FastAPI backend
  ├── workers/    # Ingestion + NLP workers
  ├── web/        # React dashboard
  ├── docker/     # Docker Compose, configs
  ├── docs/       # Diagrams, SRS, notes
```

---

## 📈 Roadmap

- **Week 1**: Price polling + alerts + basic dashboard
- **Week 2**: Content ingestion (RSS/news)
- **Week 3**: NLP insights (HF + LangChain)
- **Week 4**: Signals + event/price correlation
- **Week 5**: WebSockets + live dashboard
- **Week 6**: Backtesting + paper trading
- **Week 7**: CI/CD, deploy, polish

---

## 📚 Learn-as-You-Go Curriculum

- **Week 1**: FastAPI & WebSockets basics
- **Week 2**: SQL modeling & TimescaleDB
- **Week 3**: Hugging Face pipelines + LangChain
- **Week 4**: Kafka/Redis streaming concepts
- **Week 5**: React data-viz, WebSocket client integration
- **Week 6**: Backtesting basics & quant metrics
- **Week 7**: CI/CD, monitoring, deployment

---

## 🎯 Use Cases

- **Full-Stack SWE** → Showcases real-time APIs, React UI, FastAPI backend
- **ML/AI Engineer** → Integrates Hugging Face & LangChain into production pipelines
- **Cloud/Infra Engineer** → Event-driven design with Kafka, Docker, CI/CD, observability

---

## ▶️ Getting Started

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/stock-sentiment-dashboard.git
   cd stock-sentiment-dashboard
   ```

2. Start services with Docker Compose:

   ```bash
   docker-compose up --build
   ```

3. Access dashboard:

   ```
   http://localhost:3000
   ```

4. API available at:

   ```
   http://localhost:8000/docs
   ```

---

## 📊 Demo

*(Add screenshots/GIFs of dashboard, alerts, sentiment charts, and PnL graphs once implemented)*

---

## 🔮 Future Enhancements

- Multi-tenant authentication & user preferences
- Ensemble sentiment models (finance-tuned + zero-shot)
- Anomaly detection on volume & volatility
- LLM-generated explanations with source links
- Notebook exports for analysts

---

## 📜 License

MIT License – free to use and modify.

