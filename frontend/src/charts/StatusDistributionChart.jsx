import React from "react";
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { EmptyState } from "../components/LoadingErrorState";

const STATUS_COLORS = {
    ACTIVE: "#7c3aed",
    AUDIOBOOK_LISTEN: "#9b5de5",
    CATALOG_VIEW: "#3b82f6",
    EBOOK_READ: "#10b981",
    OVERDUE: "#ef4444",
    RENEWAL_REQUEST: "#f59e0b",
    RESERVATION_REQUEST: "#8b5cf6",
    RETURNED: "#10b981",
    REVIEW_SUBMITTED: "#14b8a6",
    WISHLIST_ADD: "#a78bfa",
    LOST: "#64748b",
};

const STATUS_LABELS = {
    ACTIVE: "Active",
    AUDIOBOOK_LISTEN: "Audiobook Listen",
    CATALOG_VIEW: "Catalog View",
    EBOOK_READ: "E-book Read",
    OVERDUE: "Overdue",
    RENEWAL_REQUEST: "Renewal Request",
    RESERVATION_REQUEST: "Reservation Request",
    RETURNED: "Returned",
    REVIEW_SUBMITTED: "Review Submitted",
    WISHLIST_ADD: "Wishlist Add",
    LOST: "Lost",
};

function StatusDistributionChart({ data = [] }) {
    if (!data || data.length === 0) {
        return <EmptyState title="No Status Data" message="No transaction records match the active filter criteria." />;
    }

    // Normalize casing for grouping
    const normalized = {};
    data.forEach((d) => {
        const key = String(d.status || "").trim().toUpperCase();
        if (key) {
            normalized[key] = (normalized[key] || 0) + Number(d.count || 0);
        }
    });

    const chartData = Object.entries(normalized)
        .map(([name, value]) => ({
            name,
            value,
            label: STATUS_LABELS[name] || name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        }))
        .filter((d) => d.value > 0)
        .sort((a, b) => b.value - a.value);

    return (
        <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={3}
                        dataKey="value"
                    >
                        {chartData.map((entry) => (
                            <Cell
                                key={entry.name}
                                fill={STATUS_COLORS[entry.name] || "#8b5cf6"}
                                stroke="var(--surface)"
                                strokeWidth={2}
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            backgroundColor: "var(--chart-tooltip-bg)",
                            borderRadius: "12px",
                            border: "1px solid var(--chart-tooltip-border)",
                            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
                            color: "var(--chart-tooltip-text)",
                            fontSize: "13px",
                        }}
                        formatter={(val) => [`${val} Transactions`, "Count"]}
                    />
                    <Legend
                        verticalAlign="bottom"
                        height={70}
                        iconType="circle"
                        wrapperStyle={{
                            paddingTop: 10,
                            display: "flex",
                            flexWrap: "wrap",
                            justifyContent: "center",
                            rowGap: 8,
                        }}
                        formatter={(val) => {
                            const matched = chartData.find((entry) => entry.name === val);
                            return (
                                <span style={{ color: "var(--text-secondary)", fontSize: "12px", marginRight: 10 }}>
                                    {matched?.label || val}
                                </span>
                            );
                        }}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}

export default StatusDistributionChart;
