import React from "react";

function StatusBadge({ status, type }) {
    if (!status) return <span className="null-val">N/A</span>;

    const normalized = String(status).trim().toUpperCase();

    let variant = "neutral";

    if (
        normalized === "RETURNED" ||
        normalized === "HEALTHY" ||
        normalized === "PASS" ||
        normalized === "ACTIVE" ||
        normalized === "EXCELLENT"
    ) {
        variant = "success";
    } else if (
        normalized === "CHECK" ||
        normalized === "WARNING" ||
        normalized === "NORMAL" ||
        normalized === "HIGH DEMAND" ||
        normalized === "STUDENT"
    ) {
        variant = "warning";
    } else if (
        normalized === "OVERDUE" ||
        normalized === "FAIL" ||
        normalized === "REJECTED" ||
        normalized === "LOST" ||
        normalized === "OUT OF STOCK"
    ) {
        variant = "danger";
    } else if (
        normalized === "ADULT" ||
        normalized === "SENIOR" ||
        normalized === "RESEARCHER"
    ) {
        variant = "info";
    }

    return (
        <span className={`status-badge status-badge--${variant}`}>
            <span className="status-badge__dot" />
            {status}
        </span>
    );
}

export default StatusBadge;
