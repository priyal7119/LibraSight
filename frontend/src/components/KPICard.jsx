import React from "react";
import { BookOpen } from "lucide-react";

function KPICard({ title, value, description, icon, badge, trend }) {
    const formattedValue =
        typeof value === "number"
            ? value.toLocaleString()
            : value !== undefined && value !== null
            ? String(value)
            : "0";

    return (
        <div className="kpi-card">
            <div className="kpi-card__header">
                <div className="kpi-card__icon-wrapper">
                    {icon || <BookOpen size={20} />}
                </div>
                {badge && <span className="kpi-card__badge">{badge}</span>}
            </div>

            <div className="kpi-card__body">
                <span className="kpi-card__label">{title}</span>
                <h3 className="kpi-card__value">{formattedValue}</h3>
            </div>

            {(description || trend) && (
                <div className="kpi-card__footer">
                    {trend && (
                        <span className={`kpi-card__trend kpi-card__trend--${trend.type || "up"}`}>
                            {trend.label}
                        </span>
                    )}
                    {description && <span className="kpi-card__desc">{description}</span>}
                </div>
            )}
        </div>
    );
}

export default KPICard;