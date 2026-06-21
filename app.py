import os
import time
import glob
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import markdown

from fin_agent.tasks.research_tasks import run_crew
from fin_agent.output.formatter import format_report
from fin_agent.execution.alpaca_trader import parse_and_execute_strategy

# Initialize FastAPI
app = FastAPI(title="Finance Multi-Agent API")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
REPORTS_DIR = os.path.join(BASE_DIR, "output", "reports")

# Ensure directories exist
os.makedirs(FRONTEND_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

class AnalyzeRequest(BaseModel):
    ticker: str

@app.post("/api/analyze")
def analyze_ticker(req: AnalyzeRequest):
    ticker = req.ticker.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    try:
        analyst_out, strategy_out = run_crew(ticker)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        formatted_report = format_report(ticker, timestamp, analyst_out, strategy_out)
        
        filepath = os.path.join(REPORTS_DIR, f"{ticker}_{timestamp}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_report)
            
        # Execute paper trade if applicable
        trade_result = parse_and_execute_strategy(ticker, strategy_out)
        if trade_result.get("status") == "success":
            formatted_report += f"\n\n## Execution\n✅ Paper Trade Executed: {trade_result['side'].upper()} {trade_result['qty']} shares. Order ID: {trade_result['order_id']}"
            
        html_report = markdown.markdown(formatted_report)
        return {"status": "success", "ticker": ticker, "html": html_report, "markdown": formatted_report, "filename": f"{ticker}_{timestamp}.md"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def list_reports():
    try:
        files = glob.glob(os.path.join(REPORTS_DIR, "*.md"))
        reports = []
        for f in files:
            filename = os.path.basename(f)
            # Parse ticker and time
            parts = filename.replace(".md", "").split("_")
            ticker = parts[0]
            timestamp = "_".join(parts[1:]) if len(parts) > 1 else "Unknown"
            
            # get creation time
            ctime = os.path.getmtime(f)
            
            reports.append({
                "filename": filename,
                "ticker": ticker,
                "timestamp": timestamp,
                "ctime": ctime
            })
        
        reports.sort(key=lambda x: x["ctime"], reverse=True)
        return {"status": "success", "reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        html_content = markdown.markdown(content)
        return {"status": "success", "html": html_content, "markdown": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend not found. Please add index.html to frontend/</h1>"
