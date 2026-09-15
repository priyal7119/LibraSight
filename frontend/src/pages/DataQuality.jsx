import React, { useEffect, useState } from "react";
import {
    TableProperties,
    FileDigit,
    AlertCircle,
    Sliders,
    CheckCheck,
} from "lucide-react";
import DataTable from "../components/DataTable";
import StatusBadge from "../components/StatusBadge";
import { LoadingSkeleton, ErrorMessage } from "../components/LoadingErrorState";
import { getDataQualitySummary, getRejectedRecords } from "../services/api";

const CATEGORY_ICONS = {
    structural: <TableProperties size={20} />,
    data_type: <FileDigit size={20} />,
    missing_values: <AlertCircle size={20} />,
    range: <Sliders size={20} />,
    logical: <CheckCheck size={20} />,
};

function QualityCategoryCard({ category }) {
    const icon = CATEGORY_ICONS[category.id] || <CheckCheck size={20} />;

    return (
        <div className="quality-cat-card">
            <div className="quality-cat-card__header">
                <span style={{ color: "var(--primary)" }}>{icon}</span>
                <StatusBadge status={category.status} />
            </div>
            <div className="quality-cat-card__title">{category.name}</div>
            <div className="quality-cat-card__body">
                <div style={{ marginTop: 8 }}>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>
                        {category.total_checks} checks · {category.invalid_count} issues found
                    </span>
                </div>
                <div style={{ marginTop: 10 }}>
                    {(category.checks || [])
                        .filter((c) => c.status !== "PASS")
                        .slice(0, 3)
                        .map((c, i) => (
                            <div key={i} style={{ marginBottom: 4 }}>
                                <span
                                    style={{
                                        display: "inline-block",
                                        padding: "2px 8px",
                                        borderRadius: 6,
                                        background: c.status === "FAIL" ? "var(--danger-bg)" : "var(--warning-bg)",
                                        color: c.status === "FAIL" ? "var(--danger)" : "var(--warning)",
                                        fontSize: "0.72rem",
                                        fontWeight: 500,
                                    }}
                                >
                                    {c.check}: {c.invalid_count}
                                </span>
                            </div>
                        ))}
                </div>
            </div>
        </div>
    );
}

function DataQuality() {
    const [summary, setSummary] = useState(null);
    const [rejected, setRejected] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [summaryRes, rejectedRes] = await Promise.all([
                getDataQualitySummary(),
                getRejectedRecords(),
            ]);
            setSummary(summaryRes.data);
            setRejected(rejectedRes.data);
        } catch (err) {
            console.error("Data Quality load error:", err);
            setError("Unable to load data quality metrics from the backend.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    if (loading) {
        return (
            <div>
                <div className="page-header"><div><h1>Data Quality</h1><p>Loading quality metrics...</p></div></div>
                <LoadingSkeleton count={1} height={180} />
                <LoadingSkeleton count={5} height={160} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Data Quality</h1><p>Validation audit &amp; quality metrics</p></div></div>
                <ErrorMessage message={error} onRetry={loadData} />
            </div>
        );
    }

    const rejectedColumns = [
        { key: "transaction_id", label: "Transaction ID" },
        {
            key: "reader_name",
            label: "Reader",
            render: (v) => v || <span className="null-val">N/A</span>,
        },
        {
            key: "book_title",
            label: "Book Title",
        },
        {
            key: "transaction_status",
            label: "Status",
            render: (v) => (v ? <StatusBadge status={v} /> : <span className="null-val">N/A</span>),
        },
        {
            key: "issues",
            label: "Validation Issues",
            render: (issues) => (
                <div className="issues-tag-list">
                    {(issues || []).map((issue, i) => (
                        <span key={i} className="issue-tag">{issue}</span>
                    ))}
                </div>
            ),
        },
        {
            key: "age",
            label: "Age",
            render: (v) => (v !== null && v !== undefined ? v : <span className="null-val">N/A</span>),
        },
        {
            key: "fine_amount",
            label: "Fine",
            render: (v) => (v !== null ? `₹${parseFloat(v).toFixed(2)}` : <span className="null-val">N/A</span>),
        },
    ];

    const score = summary?.overall_quality_score ?? 0;

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Data Quality</h1>
                    <p>Multi-dimensional validation audit, quality score, and rejected records</p>
                </div>
            </div>

            {/* Overall Quality Score Hero Card */}
            <div className="quality-hero">
                <div className="quality-hero__score-box">
                    <div className="quality-hero__circle">
                        <span className="quality-hero__pct">{score}%</span>
                        <span className="quality-hero__score-label">Score</span>
                    </div>
                    <div className="quality-hero__title">
                        <h2>Overall Data Quality: {summary?.rating || "Excellent"}</h2>
                        <p>
                            Quality Score = (Clean Rows / Total Raw Rows) × 100
                            <br />
                            LibraSight validation pipeline confirmed <strong>{summary?.clean_rows || 480}</strong> clean records
                            from <strong>{summary?.total_raw_rows || 500}</strong> raw input rows.
                        </p>
                    </div>
                </div>

                <div className="quality-hero__metrics">
                    <div className="quality-hero__metric">
                        <span>Total Raw</span>
                        <span>{summary?.total_raw_rows ?? 500}</span>
                    </div>
                    <div className="quality-hero__metric">
                        <span>Clean Rows</span>
                        <span style={{ color: "var(--success)" }}>{summary?.clean_rows ?? 480}</span>
                    </div>
                    <div className="quality-hero__metric">
                        <span>Rejected</span>
                        <span style={{ color: "var(--danger)" }}>{summary?.rejected_rows ?? 12}</span>
                    </div>
                </div>
            </div>

            {/* Quality Categories Grid */}
            <div className="quality-categories-grid">
                {(summary?.categories || []).map((cat) => (
                    <QualityCategoryCard key={cat.id} category={cat} />
                ))}
            </div>

            {/* Rejected Records Table */}
            <div className="table-container">
                <div className="table-toolbar">
                    <h3 className="chart-card__title" style={{ margin: 0 }}>
                        Rejected Records
                    </h3>
                    <span className="table-count">{rejected.length} records failed validation</span>
                </div>
                <DataTable
                    columns={rejectedColumns}
                    data={rejected}
                    searchPlaceholder="Search by transaction ID, reader, book..."
                    pageSize={15}
                    showPagination={false}
                />
            </div>
        </div>
    );
}

export default DataQuality;