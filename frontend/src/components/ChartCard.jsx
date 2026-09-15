import React from "react";

function ChartCard({ title, subtitle, action, children, className = "" }) {
    return (
        <div className={`chart-card ${className}`.trim()}>
            <div className="chart-card__header">
                <div>
                    <h3 className="chart-card__title">{title}</h3>
                    {subtitle && <p className="chart-card__subtitle">{subtitle}</p>}
                </div>
                {action && <div className="chart-card__action">{action}</div>}
            </div>

            <div className="chart-card__content">
                {children}
            </div>
        </div>
    );
}

export default ChartCard;