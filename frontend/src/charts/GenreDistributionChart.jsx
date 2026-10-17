import React from "react";
import {
    BarChart,
    Bar,
    Cell,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { EmptyState } from "../components/LoadingErrorState";

const BAR_COLORS = [
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

    const totalGenreTransactions = chartData.reduce((sum, item) => sum + item.value, 0);
    const topGenre = chartData[0] || { name: "N/A", value: 0 };
    const avgGenreVolume = chartData.length ? Math.round(totalGenreTransactions / chartData.length) : 0;

    return (
        <div className="genre-chart-wrap">
            <div className="genre-chart-meta">
                <div className="genre-chart-stat">
                    <span className="genre-chart-stat__label">Top genre</span>
                    <strong>{topGenre.name}</strong>
                    <small>{topGenre.value} transactions</small>
                </div>
                <div className="genre-chart-stat">
                    <span className="genre-chart-stat__label">Avg. volume</span>
                    <strong>{avgGenreVolume}</strong>
                    <small>per genre</small>
                </div>
                <div className="genre-chart-stat">
                    <span className="genre-chart-stat__label">Total</span>
                    <strong>{totalGenreTransactions}</strong>
                    <small>circulations</small>
                </div>
            </div>

            <div className="genre-chart-visual">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 10, left: 8, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(148, 163, 184, 0.18)" />
                        <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#6b7280" }} />
                        <YAxis
                            type="category"
                            dataKey="name"
                            width={68}
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 11, fill: "#4b5563" }}
                        />
                        <Tooltip
                            cursor={{ fill: "rgba(124, 58, 237, 0.06)" }}
                            formatter={(value) => [`${value} transactions`, "Volume"]}
                            contentStyle={{
                                backgroundColor: "var(--chart-tooltip-bg)",
                                borderRadius: "12px",
                                border: "1px solid var(--chart-tooltip-border)",
                                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
                                color: "var(--chart-tooltip-text)",
                                fontSize: "12px",
                            }}
                        />
                        <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${entry.name}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default GenreDistributionChart;
