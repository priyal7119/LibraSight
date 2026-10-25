import React from "react";
import {
    ArrowRight,
    Database,
    FileText,
    CheckCheck,
    Sparkles,
    Warehouse,
    BarChart3,
    ShieldAlert,
} from "lucide-react";

const sources = [
    { name: "Library CSV", detail: "data/raw/library_raw_data.csv" },
    { name: "Quality output", detail: "data/quality/data_quality_report.csv" },
    { name: "Rejected records", detail: "data/quality/rejected_records.csv" },
];

const stages = [
    {
        title: "Source data",
        detail: "Raw transaction file is loaded from the library dataset.",
        icon: <FileText size={18} />,
    },
    {
        title: "Ingestion",
        detail: "CSV is read through the ingestion layer and required columns are checked.",
        icon: <Database size={18} />,
    },
    {
        title: "Validation",
        detail: "Dates, numbers, duplicates, empty rows, and schema rules are validated.",
        icon: <ShieldAlert size={18} />,
    },
    {
        title: "Cleaning",
        detail: "Invalid transaction IDs are removed, strings are trimmed, dates are normalized, and bad rows are filtered out.",
        icon: <CheckCheck size={18} />,
    },
    {
        title: "Transform",
        detail: "The cleaned data becomes a standardized Parquet dataset for analytics processing.",
        icon: <Sparkles size={18} />,
    },
    {
        title: "Spark + Warehouse",
        detail: "PySpark aggregates results, then the cleaned facts are loaded into PostgreSQL.",
        icon: <Warehouse size={18} />,
    },
    {
        title: "Dashboard",
        detail: "The API serves analytics to the frontend dashboards and reports.",
        icon: <BarChart3 size={18} />,
    },
];

function DataPipeline() {
    return (
        <div className="pipeline-page">
            <div className="page-header">
                <div>
                    <h1>Data Pipeline</h1>
                    <p>From raw library transactions to validated analytics and reporting</p>
                </div>
            </div>

            <div className="pipeline-sources">
                {sources.map((source) => (
                    <div key={source.name} className="pipeline-source-card">
                        <div className="pipeline-source-card__icon">
                            <Database size={16} />
                        </div>
                        <div>
                            <div className="pipeline-source-card__title">{source.name}</div>
                            <div className="pipeline-source-card__detail">{source.detail}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="pipeline-flow">
                {stages.map((stage, index) => (
                    <React.Fragment key={stage.title}>
                        <div className="pipeline-stage">
                            <div className="pipeline-stage__icon">{stage.icon}</div>
                            <h3>{stage.title}</h3>
                            <p>{stage.detail}</p>
                        </div>
                        {index < stages.length - 1 && (
                            <div className="pipeline-arrow" aria-hidden="true">
                                <ArrowRight size={18} />
                            </div>
                        )}
                    </React.Fragment>
                ))}
            </div>

            <div className="pipeline-summary">
                <div className="pipeline-summary__card">
                    <span className="pipeline-summary__label">Load</span>
                    <p>Raw records are imported from the source CSV into the ingestion layer for the first pass.</p>
                </div>
                <div className="pipeline-summary__card">
                    <span className="pipeline-summary__label">Validate</span>
                    <p>The system checks column names, duplicate rows, missing values, numeric fields, and date formats.</p>
                </div>
                <div className="pipeline-summary__card">
                    <span className="pipeline-summary__label">Clean</span>
                    <p>Bad transactions are rejected, dates are normalized, values are trimmed, and only valid records are kept.</p>
                </div>
            </div>

            <div className="pipeline-summary pipeline-summary--wide">
                <div className="pipeline-summary__card">
                    <span className="pipeline-summary__label">Transform</span>
                    <p>The valid rows are written to the processed Parquet dataset and then used by Spark for calculations and aggregated business metrics.</p>
                </div>
                <div className="pipeline-summary__card">
                    <span className="pipeline-summary__label">Deliver</span>
                    <p>PostgreSQL stores the warehouse-ready tables, and the frontend consumes the cleaned analytics through the FastAPI backend.</p>
                </div>
            </div>
        </div>
    );
}

export default DataPipeline;
