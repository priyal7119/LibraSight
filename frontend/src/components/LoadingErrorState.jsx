import React from "react";
import { CircleAlert, RotateCcw, FolderOpen } from "lucide-react";

export function LoadingSkeleton({ count = 4, height = 120 }) {
    return (
        <div className="skeleton-grid" style={{ "--skeleton-count": count }}>
            {Array.from({ length: count }).map((_, i) => (
                <div
                    key={i}
                    className="skeleton-card"
                    style={{ minHeight: `${height}px` }}
                >
                    <div className="skeleton-line skeleton-line--short" />
                    <div className="skeleton-line skeleton-line--thick" />
                    <div className="skeleton-line skeleton-line--medium" />
                </div>
            ))}
        </div>
    );
}

export function ErrorMessage({ message, onRetry }) {
    return (
        <div className="error-banner">
            <div className="error-banner__icon">
                <CircleAlert size={22} />
            </div>
            <div className="error-banner__content">
                <h4>Unable to load analytics</h4>
                <p>{message || "Unable to load analytics. Please try again."}</p>
            </div>
            {onRetry && (
                <button className="retry-btn" onClick={onRetry} aria-label="Retry loading data">
                    <RotateCcw size={15} />
                    Retry
                </button>
            )}
        </div>
    );
}

export function EmptyState({
    title = "No data available",
    message = "No data available for the selected filters.",
}) {
    return (
        <div className="empty-state">
            <div className="empty-state__icon">
                <FolderOpen size={36} />
            </div>
            <h4>{title}</h4>
            <p>{message}</p>
        </div>
    );
}
