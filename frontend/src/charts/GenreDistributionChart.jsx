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

const PURPLE_PALETTE = [
    "#7c3aed",
    "#9333ea",
    "#a855f7",
    "#c084fc",
    "#6366f1",
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ec4899",
    "#14b8a6",
];

function GenreDistributionChart({ data = [] }) {
    if (!data || data.length === 0) {
        return <EmptyState title="No Genre Data" message="No transaction records match the active filter criteria." />;
    }

    const chartData = data
        .map((d) => ({
            name: d.genre,
            value: Number(d.transaction_count) || 0,
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
                        {chartData.map((_, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={PURPLE_PALETTE[index % PURPLE_PALETTE.length]}
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
                        formatter={(val) => [`${val} Transactions`, "Circulation"]}
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

export default GenreDistributionChart;
