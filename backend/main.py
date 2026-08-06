from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from backend.pipeline import run_research_pipeline
from backend.database import (
    init_db,
    save_report,
    get_history,
    get_report_by_id,
    check_existing_report,
)

# ---------------- App Setup ----------------
app = FastAPI(title="ResearchMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Startup ----------------
@app.on_event("startup")
def startup_event():
    init_db()

# ---------------- Request Model ----------------
class ResearchRequest(BaseModel):
    topic: str
    use_cache: bool = True

# ---------------- Routes ----------------
@app.get("/")
def root():
    return {"message": "ResearchMind API is running"}

@app.post("/research")
def research(request: ResearchRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    # Check cache
    if request.use_cache:
        existing = check_existing_report(topic)
        if existing:
            existing["from_cache"] = True
            return existing

    # Run pipeline
    try:
        result = run_research_pipeline(topic)

    except Exception as e:
        print("\n" + "=" * 80)
        print("PIPELINE ERROR")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )

    # Save report
    new_id = save_report(
        topic=topic,
        search_results=result.get("search_results", ""),
        scraped_content=result.get("scraped_content", ""),
        report=result.get("report", ""),
        feedback=result.get("feedback", ""),
    )

    result["id"] = new_id
    result["topic"] = topic
    result["from_cache"] = False

    return result


@app.get("/history")
def history(limit: int = 20):
    return get_history(limit=limit)


@app.get("/report/{report_id}")
def report_detail(report_id: int):
    report = get_report_by_id(report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )