import os
import json
import pytest
from pypdf import PdfReader
from sqlalchemy import text
from app.database import SessionLocal
from app.main import app
from fastapi.testclient import TestClient
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "generated"
DATA_QUALITY_JSON = PROJECT_ROOT / "data" / "quality" / "pdf_verification_report.json"
DATA_QUALITY_TXT = PROJECT_ROOT / "data" / "quality" / "pdf_verification_report.txt"

client = TestClient(app)

verification_results = {
    "overall_status": "PASS",
    "reports": {}
}

def extract_pdf_text(filepath):
    try:
        reader = PdfReader(filepath)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        return text_content
    except Exception as e:
        return ""

def write_reports():
    overall = "PASS"
    for r in verification_results["reports"].values():
        if r.get("status") == "FAIL":
            overall = "FAIL"
            break
    verification_results["overall_status"] = overall
    
    with open(DATA_QUALITY_JSON, "w") as f:
        json.dump(verification_results, f, indent=4)
        
    with open(DATA_QUALITY_TXT, "w") as f:
        f.write("LIBRASIGHT PDF VERIFICATION\n")
        f.write("============================\n\n")
        f.write(f"Overall Status: {overall}\n\n")
        
        for report_name, report_data in verification_results["reports"].items():
            f.write(f"{report_name.replace('_', ' ').upper()}\n")
            f.write("-" * len(report_name) + "\n")
            for check_name, check_result in report_data.get("checks", {}).items():
                f.write(f"{check_name}: {check_result}\n")
                if check_result == "FAIL":
                    err = report_data.get("errors", {}).get(check_name)
                    if err:
                        f.write(f"  -> {err}\n")
            f.write("\n")
            
def run_check(report_name, check_name, expected, text_content):
    if report_name not in verification_results["reports"]:
        verification_results["reports"][report_name] = {"status": "PASS", "checks": {}, "errors": {}}
    
    passed = expected in text_content
    status = "PASS" if passed else "FAIL"
    verification_results["reports"][report_name]["checks"][check_name] = status
    
    if not passed:
        verification_results["reports"][report_name]["status"] = "FAIL"
        verification_results["reports"][report_name]["errors"][check_name] = f"Expected '{expected}' not found in PDF."
        
    return passed

def run_check_exact(report_name, check_name, passed, err_msg=""):
    if report_name not in verification_results["reports"]:
        verification_results["reports"][report_name] = {"status": "PASS", "checks": {}, "errors": {}}
    
    status = "PASS" if passed else "FAIL"
    verification_results["reports"][report_name]["checks"][check_name] = status
    if not passed:
        verification_results["reports"][report_name]["status"] = "FAIL"
        verification_results["reports"][report_name]["errors"][check_name] = err_msg
    return passed

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    yield
    write_reports()
    overall = verification_results["overall_status"]
    if overall == "FAIL":
        pytest.fail("Verification failed, see report logs.")

def test_monthly_performance():
    db = SessionLocal()
    report_name = "monthly_library_performance"
    
    response = client.get("/reports/monthly")
    run_check_exact(report_name, "PDF Generated Endpoint", response.status_code == 200, "Endpoint failed")
    
    pdf_path = REPORTS_DIR / "monthly_library_performance.pdf"
    pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 0
    run_check_exact(report_name, "PDF Generated", pdf_exists, "PDF missing or empty")
    
    if pdf_exists:
        text_content = extract_pdf_text(pdf_path)
        run_check_exact(report_name, "PDF Readable", len(text_content) > 0, "PDF text empty")
        
        # total_transactions
        db_metrics = db.execute(text("SELECT COUNT(*) as total_transactions, COUNT(DISTINCT reader_key) as active_readers, COUNT(DISTINCT book_key) as books_borrowed, COUNT(DISTINCT branch_key) as branches FROM fact_library_transaction")).mappings().one()
        
        run_check(report_name, "Total Transactions", f"{db_metrics['total_transactions']:,}", text_content)
        run_check(report_name, "Active Readers", f"{db_metrics['active_readers']:,}", text_content)
        run_check(report_name, "Books Borrowed", f"{db_metrics['books_borrowed']:,}", text_content)
        run_check(report_name, "Active Branches", f"{db_metrics['branches']:,}", text_content)
        
        # monthly trend (just checking first row)
        trend = db.execute(text("SELECT month_name, COUNT(*) as c FROM fact_library_transaction JOIN dim_date ON fact_library_transaction.date_key = dim_date.date_key GROUP BY month_name, month ORDER BY month LIMIT 1")).mappings().one()
        run_check_exact(report_name, "Monthly Trend", trend['month_name'] in text_content and str(trend['c']) in text_content, "Trend missing")
        
        run_check_exact(report_name, "Transaction Status", "Status Breakdown" in text_content or "Returned" in text_content, "Status section missing")
        
    db.close()

def test_reading_trends():
    db = SessionLocal()
    report_name = "reading_trends"
    
    response = client.get("/reports/reading-trends")
    pdf_path = REPORTS_DIR / "reading_trends.pdf"
    pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 0
    run_check_exact(report_name, "PDF Generated", pdf_exists, "PDF missing or empty")
    
    if pdf_exists:
        text_content = extract_pdf_text(pdf_path)
        # Verify
        run_check_exact(report_name, "Yearly Trends", "Yearly Trends" in text_content, "Missing Yearly Trends")
        run_check_exact(report_name, "Monthly Trends", "Monthly Trends" in text_content, "Missing Monthly Trends")
        run_check_exact(report_name, "Genre Popularity", "Genre Trends" in text_content, "Missing Genre Trends")
        run_check_exact(report_name, "Format Usage", "Format Usage" in text_content, "Missing Format Usage")
        
    db.close()

def test_collection_analysis():
    db = SessionLocal()
    report_name = "collection_analysis"
    
    response = client.get("/reports/collection")
    pdf_path = REPORTS_DIR / "collection_analysis.pdf"
    pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 0
    run_check_exact(report_name, "PDF Generated", pdf_exists, "PDF missing or empty")
    
    if pdf_exists:
        text_content = extract_pdf_text(pdf_path)
        run_check_exact(report_name, "Top 10 Books", "Popular Books" in text_content, "Missing Popular Books")
        run_check_exact(report_name, "Availability", "Limited Availability" in text_content, "Missing Availability")
        run_check_exact(report_name, "Reservations", "Reservations" in text_content, "Missing Reservations")
    db.close()

def test_branch_performance():
    db = SessionLocal()
    report_name = "branch_performance"
    
    response = client.get("/reports/branch")
    pdf_path = REPORTS_DIR / "branch_performance.pdf"
    pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 0
    run_check_exact(report_name, "PDF Generated", pdf_exists, "PDF missing or empty")
    
    if pdf_exists:
        text_content = extract_pdf_text(pdf_path)
        run_check_exact(report_name, "Branch Circulation", "Branch Transactions" in text_content, "Missing Branch Transactions")
        run_check_exact(report_name, "Reader Reach", "Readers" in text_content, "Missing Readers")
        run_check_exact(report_name, "Fine Collection", "Total Fines" in text_content, "Missing Fines")
        run_check_exact(report_name, "Overdue Transactions", "Overdue Activity" in text_content, "Missing Overdue")
    db.close()

def test_data_quality():
    db = SessionLocal()
    report_name = "data_quality"
    
    response = client.get("/reports/data-quality")
    pdf_path = REPORTS_DIR / "data_quality.pdf"
    pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 0
    run_check_exact(report_name, "PDF Generated", pdf_exists, "PDF missing or empty")
    
    if pdf_exists:
        text_content = extract_pdf_text(pdf_path)
        
        # dynamic calculate
        raw_csv = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"
        df_raw = pd.read_csv(raw_csv)
        total_records = len(df_raw)
        
        db_metrics = db.execute(text("SELECT COUNT(*) as clean_records FROM fact_library_transaction")).mappings().one()
        clean_records = db_metrics['clean_records']
        
        rej_csv = PROJECT_ROOT / "data" / "quality" / "rejected_records.csv"
        if rej_csv.exists():
            df_rej = pd.read_csv(rej_csv)
            rejected_records = len(df_rej)
        else:
            rejected_records = 0
            
        quality_score = round((clean_records / total_records) * 100, 2)
        
        run_check(report_name, "Total Records", str(total_records), text_content)
        run_check(report_name, "Rejected Records", str(rejected_records), text_content)
        run_check(report_name, "Quality Score", f"{quality_score}%", text_content)
        
    db.close()
