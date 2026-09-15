import React, { useEffect, useState, useMemo } from "react";
import { Users } from "lucide-react";
import DataTable from "../components/DataTable";
import ChartCard from "../components/ChartCard";
import StatusBadge from "../components/StatusBadge";
import { LoadingSkeleton, ErrorMessage } from "../components/LoadingErrorState";
import { getReaders, getReaderTypes, getReaderActivity } from "../services/api";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

function Readers() {
    const [readers, setReaders] = useState([]);
    const [readerTypes, setReaderTypes] = useState([]);
    const [activity, setActivity] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [readersRes, typesRes, activityRes] = await Promise.all([
                getReaders(),
                getReaderTypes(),
                getReaderActivity(),
            ]);
            setReaders(readersRes.data.items ?? readersRes.data);
            setReaderTypes(typesRes.data);
            setActivity(activityRes.data);
        } catch (err) {
            console.error("Readers load error:", err);
            setError("Unable to load reader data from the backend.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const normalizedTypes = useMemo(() => {
        const merged = {};
        readerTypes.forEach((rt) => {
            const key = String(rt.reader_type || "Unknown").trim().toLowerCase();
            const label = key.charAt(0).toUpperCase() + key.slice(1);
            merged[label] = (merged[label] || 0) + Number(rt.transaction_count || 0);
        });
        return Object.entries(merged)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count);
    }, [readerTypes]);

    if (loading) {
        return (
            <div>
                <div className="page-header"><div><h1>Readers</h1><p>Loading reader data...</p></div></div>
                <LoadingSkeleton count={4} height={100} />
                <LoadingSkeleton count={1} height={320} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Readers</h1><p>Reader activity &amp; membership</p></div></div>
                <ErrorMessage message={error} onRetry={loadData} />
            </div>
        );
    }

    const activityColumns = [
        { key: "reader_id", label: "Reader ID" },
        {
            key: "reader_name",
            label: "Name",
            render: (v) => v || <span className="null-val">N/A</span>,
        },
        {
            key: "reader_type",
            label: "Type",
            render: (t) => <StatusBadge status={t} />,
        },
        {
            key: "transaction_count",
            label: "Transactions",
            render: (c) => <strong>{c}</strong>,
        },
        {
            key: "total_fine",
            label: "Total Fine",
            render: (f) => {
                const num = parseFloat(f) || 0;
                return (
                    <span style={{ color: num > 0 ? "var(--danger)" : "var(--text-secondary)" }}>
                        ₹{num.toFixed(2)}
                    </span>
                );
            },
        },
    ];

    const readerColumns = [
        { key: "reader_id", label: "Reader ID" },
        {
            key: "reader_name",
            label: "Name",
            render: (v) => v || <span className="null-val">N/A</span>,
        },
        {
            key: "age",
            label: "Age",
            render: (v) => v !== null && v !== undefined ? v : <span className="null-val">N/A</span>,
        },
        {
            key: "gender",
            label: "Gender",
            render: (v) => v || <span className="null-val">N/A</span>,
        },
        {
            key: "reader_type",
            label: "Type",
            render: (t) => <StatusBadge status={t} />,
        },
        { key: "membership_date", label: "Member Since" },
        { key: "home_branch_id", label: "Home Branch" },
    ];

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Readers</h1>
                    <p>Reader demographics, activity metrics, and membership records</p>
                </div>
                <StatusBadge status={`${readers.length} Members`} />
            </div>

            {/* Reader Type Distribution Chart + Top Activity */}
            <div className="analytics-grid">
                <ChartCard
                    title="Reader Type — Transaction Volume"
                    subtitle="Circulation counts broken down by membership category"
                >
                    <div style={{ width: "100%", height: 280 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={normalizedTypes}
                                margin={{ top: 10, right: 20, left: -10, bottom: 0 }}
                                layout="vertical"
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" horizontal={false} />
                                <XAxis type="number" stroke="var(--chart-axis)" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis dataKey="name" type="category" stroke="var(--chart-axis)" fontSize={12} tickLine={false} axisLine={false} width={90} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "var(--chart-tooltip-bg)",
                                        borderRadius: "12px",
                                        border: "1px solid var(--chart-tooltip-border)",
                                        boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                                        color: "var(--chart-tooltip-text)",
                                        fontSize: "13px",
                                    }}
                                    formatter={(v) => [`${v} Transactions`, "Volume"]}
                                />
                                <Bar dataKey="count" fill="var(--primary)" radius={[0, 6, 6, 0]} maxBarSize={32} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>

                <ChartCard
                    title="Most Active Readers"
                    subtitle="Top readers by total circulation activity"
                >
                    <DataTable
                        columns={activityColumns}
                        data={activity.slice(0, 8)}
                        showSearch={false}
                        showPagination={false}
                    />
                </ChartCard>
            </div>

            {/* Full Readers Table */}
            <div className="table-container">
                <div className="table-toolbar">
                    <h3 className="chart-card__title" style={{ margin: 0 }}>
                        Reader Directory
                    </h3>
                    <span className="table-count">{readers.length} registered members</span>
                </div>
                <DataTable
                    columns={readerColumns}
                    data={readers}
                    searchPlaceholder="Search reader name, ID, type..."
                    pageSize={12}
                />
            </div>
        </div>
    );
}

export default Readers;
