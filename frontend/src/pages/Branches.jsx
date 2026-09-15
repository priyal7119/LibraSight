import React, { useEffect, useState } from "react";
import { Building2, TrendingUp, IndianRupee } from "lucide-react";
import DataTable from "../components/DataTable";
import ChartCard from "../components/ChartCard";
import StatusBadge from "../components/StatusBadge";
import { LoadingSkeleton, ErrorMessage } from "../components/LoadingErrorState";
import { getBranches, getBranchPerformance } from "../services/api";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

function Branches() {
    const [branches, setBranches] = useState([]);
    const [performance, setPerformance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [branchRes, perfRes] = await Promise.all([
                getBranches(),
                getBranchPerformance(),
            ]);
            setBranches(branchRes.data.items ?? branchRes.data);
            setPerformance(perfRes.data);
        } catch (err) {
            console.error("Branches load error:", err);
            setError("Unable to load branch data from the backend.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    if (loading) {
        return (
            <div>
                <div className="page-header"><div><h1>Branches</h1><p>Loading branch data...</p></div></div>
                <LoadingSkeleton count={3} height={100} />
                <LoadingSkeleton count={1} height={320} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Branches</h1><p>Branch performance &amp; information</p></div></div>
                <ErrorMessage message={error} onRetry={loadData} />
            </div>
        );
    }

    const chartData = performance.map((b) => ({
        name: b.branch_name && b.branch_name.length > 20
            ? b.branch_name.substring(0, 18) + "…"
            : b.branch_name || b.branch_id,
        transactions: Number(b.transaction_count) || 0,
        fines: parseFloat(b.total_fine) || 0,
    }));

    const perfColumns = [
        { key: "branch_id", label: "Branch ID" },
        { key: "branch_name", label: "Branch Name" },
        { key: "city", label: "City" },
        {
            key: "transaction_count",
            label: "Transactions",
            render: (c) => <strong>{c}</strong>,
        },
        {
            key: "total_fine",
            label: "Total Fines",
            render: (f) => {
                const num = parseFloat(f) || 0;
                return <span style={{ color: num > 0 ? "var(--danger)" : "var(--text-secondary)" }}>₹{num.toFixed(2)}</span>;
            },
        },
    ];

    const branchColumns = [
        { key: "branch_id", label: "Branch ID" },
        { key: "branch_name", label: "Name" },
        { key: "city", label: "City" },
        { key: "area", label: "Area" },
        {
            key: "library_type",
            label: "Type",
            render: (t) => <StatusBadge status={t} />,
        },
        { key: "branch_capacity", label: "Capacity" },
    ];

    const totalTransactions = performance.reduce((s, b) => s + Number(b.transaction_count || 0), 0);
    const totalFines = performance.reduce((s, b) => s + parseFloat(b.total_fine || 0), 0);

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Branches</h1>
                    <p>Branch performance analysis across all library locations</p>
                </div>
                <StatusBadge status={`${branches.length} Locations`} />
            </div>

            {/* Summary KPIs */}
            <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 28 }}>
                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper">
                            <Building2 size={20} />
                        </div>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Total Branches</span>
                        <h3 className="kpi-card__value">{branches.length}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">Library locations</span></div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper">
                            <TrendingUp size={20} />
                        </div>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Total Transactions</span>
                        <h3 className="kpi-card__value">{totalTransactions.toLocaleString()}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">All branch checkouts</span></div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper">
                            <IndianRupee size={20} />
                        </div>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Total Fines Collected</span>
                        <h3 className="kpi-card__value">₹{totalFines.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">Overdue penalties</span></div>
                </div>
            </div>

            {/* Charts */}
            <div className="analytics-grid">
                <ChartCard title="Branch Transaction Volume" subtitle="Circulations handled per branch location">
                    <div style={{ width: "100%", height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                                <XAxis dataKey="name" stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={{ stroke: "var(--border)" }} angle={-30} textAnchor="end" interval={0} />
                                <YAxis stroke="var(--chart-axis)" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                                <Tooltip contentStyle={{ backgroundColor: "var(--chart-tooltip-bg)", borderRadius: "12px", border: "1px solid var(--chart-tooltip-border)", boxShadow: "0 4px 20px rgba(0,0,0,0.15)", color: "var(--chart-tooltip-text)", fontSize: "13px" }} formatter={(v) => [`${v}`, "Transactions"]} />
                                <Bar dataKey="transactions" fill="var(--primary)" radius={[6, 6, 0, 0]} maxBarSize={44} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>

                <ChartCard title="Branch Performance Table" subtitle="Ranked by circulation volume">
                    <DataTable
                        columns={perfColumns}
                        data={performance}
                        showSearch={false}
                        showPagination={false}
                    />
                </ChartCard>
            </div>

            {/* Full Branch Table */}
            <div className="table-container">
                <div className="table-toolbar">
                    <h3 className="chart-card__title" style={{ margin: 0 }}>Branch Directory</h3>
                    <span className="table-count">{branches.length} branches</span>
                </div>
                <DataTable
                    columns={branchColumns}
                    data={branches}
                    searchPlaceholder="Search branch name, city, type..."
                    pageSize={10}
                />
            </div>
        </div>
    );
}

export default Branches;
