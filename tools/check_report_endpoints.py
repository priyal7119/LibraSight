from fastapi.testclient import TestClient
from app.main import app
from pypdf import PdfReader
from io import BytesIO
import json
from pathlib import Path

client = TestClient(app)

REPORT_ENDPOINTS = {
    "monthly_library_performance": "/reports/monthly-performance",
    "reading_trends": "/reports/reading-trends",
    "collection_analysis": "/reports/collection-analysis",
    "branch_performance": "/reports/branch-performance",
    "data_quality": "/reports/data-quality",
}

OUTPUT_JSON = Path("data/quality/frontend_report_endpoint_check.json")
OUTPUT_TXT = Path("data/quality/frontend_report_endpoint_check.txt")

results = {"overall_status": "PASS", "endpoints": {}}

for name, endpoint in REPORT_ENDPOINTS.items():
    entry = {"endpoint": endpoint}
    try:
        resp = client.get(endpoint)
        entry["status_code"] = resp.status_code
        entry["content_type"] = resp.headers.get("content-type")
        entry["content_length"] = len(resp.content)

        if resp.status_code != 200:
            entry["ok"] = False
            entry["error"] = f"Status {resp.status_code}"
            results["overall_status"] = "FAIL"
        else:
            # Try to parse as PDF
            try:
                reader = PdfReader(BytesIO(resp.content))
                pages = len(reader.pages)
                entry["pdf_pages"] = pages
                entry["ok"] = pages > 0
                if pages == 0:
                    entry["error"] = "PDF has no pages"
                    results["overall_status"] = "FAIL"
            except Exception as e:
                entry["ok"] = False
                entry["error"] = f"PDF parse error: {e}"
                results["overall_status"] = "FAIL"
    except Exception as e:
        entry["ok"] = False
        entry["error"] = str(e)
        results["overall_status"] = "FAIL"

    results["endpoints"][name] = entry

# Write outputs
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

with open(OUTPUT_TXT, "w") as f:
    f.write("FRONTEND REPORT ENDPOINT CHECK\n")
    f.write("=================================\n\n")
    f.write(f"Overall Status: {results['overall_status']}\n\n")
    for name, data in results["endpoints"].items():
        f.write(f"{name}:\n")
        for k, v in data.items():
            f.write(f"  {k}: {v}\n")
        f.write("\n")

print("Check complete. Summary:")
print(json.dumps(results, indent=2))
