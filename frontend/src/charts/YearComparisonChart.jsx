import React, { useMemo } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { EmptyState } from "../components/LoadingErrorState";

function YearComparisonChart({ data = [] }) {
    // Group transaction counts strictly by year
    const yearlyTotals = useMemo(() => {
        if (!data || data.length === 0) return [];
        const map = {};
        data.forEach((d) => {
            const y = d.year;
            if (y) {
                map[y] = (map[y] || 0) + Number(d.transaction_count || 0);
            }
        });
        return Object.entries(map)
            .map(([year, count]) => ({ year: String(year), count }))
            .sort((a, b) => Number(a.year) - Number(b.year));
    }, [data]);

    if (yearlyTotals.length === 0) {
        return <EmptyState title="No Yearly Data" message="No records available for the selected filters." />;
    }

    return (
        <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={yearlyTotals}
                    margin={{ top: 12, right: 24, left: -10, bottom: 0 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                    <XAxis
                        dataKey="year"
                        stroke="var(--chart-axis)"
                        fontSize={12}
                        tickLine={false}
                        axisLine={{ stroke: "var(--border)" }}
                    />
                    <YAxis
                        stroke="var(--chart-axis)"
                        fontSize={12}
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
                        formatter={(val) => [`${val} Transactions`, "Annual Circulation"]}
                    />
                    <Bar
                        dataKey="count"
                        fill="var(--primary)"
                        radius={[8, 8, 0, 0]}
                        maxBarSize={48}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

export default YearComparisonChart;
