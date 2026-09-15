import React from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { EmptyState } from "../components/LoadingErrorState";

function MonthlyTrendsChart({ data = [] }) {
    if (!data || data.length === 0) {
        return <EmptyState title="No Trend Data" message="No transaction records match the active filter criteria." />;
    }

    // Chronological sort by year then month
    const sortedData = [...data].sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year;
        return a.month - b.month;
    });

    const chartData = sortedData.map((d) => ({
        ...d,
        displayDate: `${(d.month_name || "").substring(0, 3)} '${String(d.year).slice(-2)}`,
        count: Number(d.transaction_count) || 0,
    }));

    return (
        <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                    data={chartData}
                    margin={{ top: 12, right: 24, left: -10, bottom: 0 }}
                >
                    <defs>
                        <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                    <XAxis
                        dataKey="displayDate"
                        stroke="var(--chart-axis)"
                        fontSize={11}
                        tickLine={false}
                        axisLine={{ stroke: "var(--border)" }}
                        dy={6}
                    />
                    <YAxis
                        stroke="var(--chart-axis)"
                        fontSize={11}
                        tickLine={false}
                        axisLine={false}
                        allowDecimals={false}
                    />
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
                        labelFormatter={(_, items) => {
                            if (items && items[0]) {
                                const p = items[0].payload;
                                return `${p.month_name} ${p.year}`;
                            }
                            return "";
                        }}
                    />
                    <Area
                        type="monotone"
                        dataKey="count"
                        stroke="var(--primary)"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#purpleGradient)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

export default MonthlyTrendsChart;
