import React, { useState } from "react";
import { FileText, Download, LoaderCircle } from "lucide-react";
import {
    downloadMonthlyPerformance,
    downloadReadingTrends,
    downloadCollectionAnalysis,
    downloadBranchPerformance,
    downloadDataQuality,
} from "../services/api";

const REPORTS = [
    {
        id: "monthly-performance",
        title: "Monthly Library Performance",
        description: "Comprehensive report of monthly transaction volumes, reader activity, top books, and branch productivity across all locations.",
        endpoint: downloadMonthlyPerformance,
        filename: "monthly_library_performance.pdf",
        category: "Operations",
    },
    {
        id: "reading-trends",
        title: "Reading Trends Report",
        description: "Multi-year circulation trends, genre popularity analysis, monthly progression, and seasonal reading patterns across the library network.",
        endpoint: downloadReadingTrends,
        filename: "reading_trends.pdf",
        category: "Analytics",
    },
    {
        id: "collection-analysis",
        title: "Collection Analysis Report",
        description: "Popular titles by borrow count, limited availability alerts, reservation demand analysis, and collection health summary.",
        endpoint: downloadCollectionAnalysis,
        filename: "collection_analysis.pdf",
        category: "Collection",
    },
    {
        id: "branch-performance",
        title: "Branch Performance Report",
        description: "Branch-level transaction volumes, fine totals, reader engagement by location, and overdue activity analysis.",
        endpoint: downloadBranchPerformance,
        filename: "branch_performance.pdf",
        category: "Branches",
    },
    {
        id: "data-quality",
        title: "Data Quality Audit Report",
        description: "Multi-dimensional quality validation matrix: structural checks, data type validation, missing values, range constraints, logical integrity, and rejected records.",
        endpoint: downloadDataQuality,
        filename: "data_quality_audit.pdf",
        category: "Quality",
    },
];

function ReportCard({ report }) {
    const [isLoading, setIsLoading] = useState(false);
    const [statusMsg, setStatusMsg] = useState("");

    const handleDownload = async () => {
        try {
            setIsLoading(true);
            setStatusMsg("");

            const response = await report.endpoint();

            const url = window.URL.createObjectURL(
                new Blob([response.data], { type: "application/pdf" })
            );

            const link = document.createElement("a");
            link.href = url;
            link.download = report.filename;
            document.body.appendChild(link);
            link.click();
            link.remove();

            setTimeout(() => window.URL.revokeObjectURL(url), 10000);

            setStatusMsg("Downloaded!");
            setTimeout(() => setStatusMsg(""), 3000);
        } catch (err) {
            console.error(`Report error [${report.id}]:`, err);
            setStatusMsg("Unable to generate this report. Please try again.");
            setTimeout(() => setStatusMsg(""), 6000);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="report-card">
            <div className="report-card__header">
                <div className="report-card__icon">
                    <FileText size={24} />
                </div>
                <div className="report-card__info">
                    <h3>{report.title}</h3>
                    <p>{report.description}</p>
                </div>
            </div>

            <div className="report-card__action">
                <span className="report-card__meta">
                    {statusMsg ? (
                        <span style={{
                            color: statusMsg.startsWith("Downloaded") ? "var(--success)" : "var(--danger)",
                            fontWeight: 600,
                            fontSize: "0.82rem",
                        }}>
                            {statusMsg}
                        </span>
                    ) : (
                        <span>PDF · Generated on-demand</span>
                    )}
                </span>
                <button
                    className="report-btn"
                    onClick={handleDownload}
                    disabled={isLoading}
                    aria-label={`Download ${report.title}`}
                >
                    {isLoading ? (
                        <>
                            <LoaderCircle size={15} style={{ animation: "spin 1s linear infinite" }} />
                            Generating...
                        </>
                    ) : (
                        <>
                            <Download size={15} />
                            Download PDF
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

function Reports() {
    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Reports</h1>
                    <p>On-demand analytical PDF reports generated live from the LibraSight data warehouse</p>
                </div>
                <span style={{
                    fontSize: "0.82rem",
                    color: "var(--text-secondary)",
                    fontWeight: 600,
                    padding: "5px 12px",
                    borderRadius: 9999,
                    background: "var(--surface-secondary)",
                    border: "1px solid var(--border)",
                }}>
                    {REPORTS.length} Verified Reports Available
                </span>
            </div>

            <div className="reports-grid">
                {REPORTS.map((report) => (
                    <ReportCard key={report.id} report={report} />
                ))}
            </div>

            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
}

export default Reports;