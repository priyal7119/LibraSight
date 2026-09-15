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
    RETURNED: "#10b981", // Emerald
    ACTIVE: "#7c3aed",   // Purple primary
    OVERDUE: "#ef4444",  // Red
    LOST: "#64748b",     // Slate
    RENEWED: "#3b82f6",  // Blue
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
        .map(([name, value]) => ({ name, value }))
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
                        height={36}
                        iconType="circle"
                        formatter={(val) => (
                            <span style={{ color: "var(--text-secondary)", fontSize: "12px", marginRight: 8 }}>
                                {val}
                            </span>
                        )}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}

export default StatusDistributionChart;
