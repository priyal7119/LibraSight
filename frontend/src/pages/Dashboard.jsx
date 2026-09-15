import React, { useEffect, useState, useCallback } from "react";
import {
    TrendingUp,
    BookOpen,
    Users,
    Building2,
    Bookmark,
    IndianRupee,
    LibraryBig,
    Layers,
    PieChart as PieIcon,
    BarChart3,
    ArrowUpRight,
} from "lucide-react";
import KPICard from "../components/KPICard";
import ChartCard from "../components/ChartCard";
import DataTable from "../components/DataTable";
import StatusBadge from "../components/StatusBadge";
import FilterPanel from "../components/FilterPanel";
import { LoadingSkeleton, ErrorMessage, EmptyState } from "../components/LoadingErrorState";
import MonthlyTrendsChart from "../charts/MonthlyTrendsChart";
import StatusDistributionChart from "../charts/StatusDistributionChart";
import YearComparisonChart from "../charts/YearComparisonChart";
import GenreDistributionChart from "../charts/GenreDistributionChart";
import {
    getDashboardSummary,
    getDashboardTrends,
    getDashboardStatus,
    getDashboardAnalytics,
} from "../services/api";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend,
} from "recharts";

const CHECKOUT_COLORS = {
    Counter: "#7c3aed",
    "Self-Service": "#3b82f6",
    "Mobile App": "#10b981",
    Online: "#f59e0b",
};

function Dashboard() {
    const [filters, setFilters] = useState({});
    const [summary, setSummary] = useState(null);
    const [trends, setTrends] = useState([]);
    const [statusData, setStatusData] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadDashboardData = useCallback(async (currentFilters = {}) => {
        try {
            setLoading(true);
            setError("");

            const [summaryRes, trendsRes, statusRes, analyticsRes] = await Promise.all([
                getDashboardSummary(currentFilters),
                getDashboardTrends(currentFilters),
                getDashboardStatus(currentFilters),
                getDashboardAnalytics(currentFilters),
            ]);

            setSummary(summaryRes.data);
            setTrends(trendsRes.data);
            setStatusData(statusRes.data);
            setAnalytics(analyticsRes.data);
        } catch (err) {
            console.error("Dashboard data load error:", err);
            setError("Unable to load library analytics data from FastAPI backend.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadDashboardData(filters);
    }, [filters, loadDashboardData]);

    const handleApplyFilters = (newFilters) => {
        setFilters(newFilters);
    };

    const handleResetFilters = () => {
        setFilters({});
    };

    const topBooksColumns = [
        { key: "book_title", label: "Title" },
        { key: "author", label: "Author" },
        {
            key: "genre",
            label: "Genre",
            render: (genre) => <StatusBadge status={genre} />,
        },
        {
            key: "transaction_count",
            label: "Circulations",
            render: (count) => (
                <span style={{ fontWeight: 700, color: "var(--primary)" }}>{count}</span>
            ),
        },
    ];

    // Prepare branch chart data
    const branchChartData = (analytics?.branches || []).map((b) => ({
        name: b.branch_name && b.branch_name.length > 18
            ? b.branch_name.substring(0, 16) + "…"
            : b.branch_name || b.branch_id,
        count: Number(b.transaction_count) || 0,
    }));

    // Prepare reader types chart data
    const readerChartData = (analytics?.reader_types || []).map((r) => ({
        name: r.reader_type,
        count: Number(r.transaction_count) || 0,
    }));

    // Prepare checkout methods data
    const checkoutMethodData = (analytics?.checkout_methods || []).map((m) => ({
        name: m.checkout_method,
        value: Number(m.transaction_count) || 0,
    }));

    // Prepare fine trends data
    const fineTrendData = (analytics?.fine_trend || []).map((f) => ({
        displayDate: `${(f.month_name || "").substring(0, 3)} '${String(f.year).slice(-2)}`,
        fine: parseFloat(f.total_fine) || 0,
    }));

    const collHealth = analytics?.collection_health || {};
    const resSummary = analytics?.reservation_summary || {};

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Library Dashboard</h1>
                    <p>Circulation metrics, reader engagement, and repository overview</p>
                </div>
            </div>

            {/* Filter Panel */}
            <FilterPanel
                filters={filters}
                onApplyFilters={handleApplyFilters}
                onResetFilters={handleResetFilters}
            />

            {error && <ErrorMessage message={error} onRetry={() => loadDashboardData(filters)} />}

            {loading ? (
                <>
                    <LoadingSkeleton count={4} height={120} />
                    <div className="analytics-grid">
                        <LoadingSkeleton count={1} height={320} />
                        <LoadingSkeleton count={1} height={320} />
                    </div>
                    <div className="analytics-grid">
                        <LoadingSkeleton count={1} height={320} />
                        <LoadingSkeleton count={1} height={320} />
                    </div>
                </>
            ) : (
                <>
                    {/* Primary 4 KPI Cards */}
                    <div className="kpi-grid">
                        <KPICard
                            title="Total Transactions"
                            value={summary?.total_transactions ?? 0}
                            description="Checkout & return activity"
                            icon={<TrendingUp size={20} />}
                        />

                        <KPICard
                            title="Cataloged Books"
                            value={summary?.total_books ?? 0}
                            description="Active titles in filtered scope"
                            icon={<BookOpen size={20} />}
                        />

                        <KPICard
                            title="Active Readers"
                            value={summary?.total_readers ?? 0}
                            description="Members with circulation activity"
                            icon={<Users size={20} />}
                        />

                        <KPICard
                            title="Branches Active"
                            value={summary?.total_branches ?? 0}
                            description="Participating library centers"
                            icon={<Building2 size={20} />}
                        />
                    </div>

                    {/* Check if no transactions match filters */}
                    {summary?.total_transactions === 0 ? (
                        <EmptyState
                            title="No Results Matching Active Filters"
                            message="No library checkout records match your selected combination of Year, Branch, Genre, or Date Range. Try clicking Reset to clear active filters."
                        />
                    ) : (
                        <>
                            {/* 1. Monthly Transaction Trend (Full Width) */}
                            <ChartCard
                                title="Monthly Transaction Trend"
                                subtitle="Chronological checkout volume across library branches"
                                className="chart-card--full"
                            >
                                <MonthlyTrendsChart data={trends} />
                            </ChartCard>

                            <div style={{ marginBottom: 28 }} />

                            {/* 2. Year Comparison & Status Distribution */}
                            <div className="analytics-grid">
                                <ChartCard
                                    title="Year Comparison"
                                    subtitle="Annual circulation totals from star schema"
                                >
                                    <YearComparisonChart data={trends} />
                                </ChartCard>

                                <ChartCard
                                    title="Transaction Status Distribution"
                                    subtitle="Current state breakdown of checked out titles"
                                >
                                    <StatusDistributionChart data={statusData} />
                                </ChartCard>
                            </div>

                            {/* 3. Genre Activity & Branch Performance */}
                            <div className="analytics-grid">
                                <ChartCard
                                    title="Transactions by Genre"
                                    subtitle="Borrow volume across reader interest categories"
                                >
                                    <GenreDistributionChart data={analytics?.genres || []} />
                                </ChartCard>

                                <ChartCard
                                    title="Branch Performance"
                                    subtitle="Circulation volume handled per branch location"
                                >
                                    {branchChartData.length === 0 ? (
                                        <EmptyState message="No branch records available." />
                                    ) : (
                                        <div style={{ width: "100%", height: 300 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <BarChart
                                                    data={branchChartData}
                                                    layout="vertical"
                                                    margin={{ top: 10, right: 20, left: 10, bottom: 0 }}
                                                >
                                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" horizontal={false} />
                                                    <XAxis type="number" stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                                                    <YAxis dataKey="name" type="category" stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={false} width={100} />
                                                    <Tooltip
                                                        contentStyle={{
                                                            backgroundColor: "var(--chart-tooltip-bg)",
                                                            borderRadius: "12px",
                                                            border: "1px solid var(--chart-tooltip-border)",
                                                            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                                                            color: "var(--chart-tooltip-text)",
                                                            fontSize: "13px",
                                                        }}
                                                        formatter={(v) => [`${v} Checkouts`, "Transactions"]}
                                                    />
                                                    <Bar dataKey="count" fill="var(--primary)" radius={[0, 6, 6, 0]} maxBarSize={28} />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}
                                </ChartCard>
                            </div>

                            {/* 4. Reader Type Activity & Top Books */}
                            <div className="analytics-grid">
                                <ChartCard
                                    title="Reader Type Activity"
                                    subtitle="Circulations broken down by cardholder membership tier"
                                >
                                    {readerChartData.length === 0 ? (
                                        <EmptyState message="No reader activity available." />
                                    ) : (
                                        <div style={{ width: "100%", height: 300 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <BarChart
                                                    data={readerChartData}
                                                    margin={{ top: 10, right: 20, left: -10, bottom: 0 }}
                                                >
                                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                                                    <XAxis dataKey="name" stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={{ stroke: "var(--border)" }} />
                                                    <YAxis stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                                                    <Tooltip
                                                        contentStyle={{
                                                            backgroundColor: "var(--chart-tooltip-bg)",
                                                            borderRadius: "12px",
                                                            border: "1px solid var(--chart-tooltip-border)",
                                                            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                                                            color: "var(--chart-tooltip-text)",
                                                            fontSize: "13px",
                                                        }}
                                                        formatter={(v) => [`${v} Transactions`, "Activity"]}
                                                    />
                                                    <Bar dataKey="count" fill="#8b5cf6" radius={[6, 6, 0, 0]} maxBarSize={36} />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}
                                </ChartCard>

                                <ChartCard
                                    title="Top 5 Borrowed Titles"
                                    subtitle="Most requested book titles in current scope"
                                >
                                    <DataTable
                                        columns={topBooksColumns}
                                        data={analytics?.top_books || []}
                                        showSearch={false}
                                        showPagination={false}
                                    />
                                </ChartCard>
                            </div>

                            {/* 5. Checkout Methods & Reservation Activity */}
                            <div className="analytics-grid">
                                <ChartCard
                                    title="Checkout Methods"
                                    subtitle="Transaction distribution across checkout channels"
                                >
                                    {checkoutMethodData.length === 0 ? (
                                        <EmptyState message="No checkout method data." />
                                    ) : (
                                        <div style={{ width: "100%", height: 280 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <PieChart>
                                                    <Pie
                                                        data={checkoutMethodData}
                                                        cx="50%"
                                                        cy="50%"
                                                        innerRadius={60}
                                                        outerRadius={90}
                                                        paddingAngle={3}
                                                        dataKey="value"
                                                    >
                                                        {checkoutMethodData.map((entry) => (
                                                            <Cell
                                                                key={entry.name}
                                                                fill={CHECKOUT_COLORS[entry.name] || "#a855f7"}
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
                                                            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                                                            color: "var(--chart-tooltip-text)",
                                                            fontSize: "13px",
                                                        }}
                                                        formatter={(v) => [`${v} Transactions`, "Checkouts"]}
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
                                    )}
                                </ChartCard>

                                <ChartCard
                                    title="Reservation Activity"
                                    subtitle="Hold requests and reader queue metrics"
                                >
                                    <div style={{ display: "flex", flexDirection: "column", gap: 16, paddingTop: 10 }}>
                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)" }}>
                                            <div className="kpi-card__header">
                                                <div className="kpi-card__icon-wrapper" style={{ background: "rgba(124, 58, 237, 0.1)", color: "var(--primary)" }}>
                                                    <Bookmark size={18} />
                                                </div>
                                                <span className="kpi-card__badge">Star Schema Fact</span>
                                            </div>
                                            <div className="kpi-card__body">
                                                <span className="kpi-card__label">Total Hold Reservations</span>
                                                <h3 className="kpi-card__value">{Number(resSummary.total_reservations || 0).toLocaleString()}</h3>
                                            </div>
                                            <div className="kpi-card__footer">
                                                <span className="kpi-card__desc">Aggregated reader hold requests</span>
                                            </div>
                                        </div>

                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)" }}>
                                            <div className="kpi-card__header">
                                                <div className="kpi-card__icon-wrapper" style={{ background: "rgba(16, 185, 129, 0.1)", color: "#10b981" }}>
                                                    <ArrowUpRight size={18} />
                                                </div>
                                                <span className="kpi-card__badge">Hold Rate</span>
                                            </div>
                                            <div className="kpi-card__body">
                                                <span className="kpi-card__label">Transactions with Hold Flags</span>
                                                <h3 className="kpi-card__value">
                                                    {Number(resSummary.transactions_with_reservations || 0).toLocaleString()}{" "}
                                                    <span style={{ fontSize: "1rem", fontWeight: 500, color: "var(--text-muted)" }}>
                                                        ({summary?.total_transactions ? ((resSummary.transactions_with_reservations / summary.total_transactions) * 100).toFixed(1) : 0}%)
                                                    </span>
                                                </h3>
                                            </div>
                                            <div className="kpi-card__footer">
                                                <span className="kpi-card__desc">Checkouts involving pre-reservations</span>
                                            </div>
                                        </div>
                                    </div>
                                </ChartCard>
                            </div>

                            {/* 6. Fine Trend & Collection Health */}
                            <div className="analytics-grid">
                                <ChartCard
                                    title="Fine Collection Trend"
                                    subtitle="Monthly overdue penalty amounts assessed (₹)"
                                >
                                    {fineTrendData.length === 0 ? (
                                        <EmptyState message="No fine records available." />
                                    ) : (
                                        <div style={{ width: "100%", height: 280 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <BarChart data={fineTrendData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                                                    <XAxis dataKey="displayDate" stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={{ stroke: "var(--border)" }} />
                                                    <YAxis stroke="var(--chart-axis)" fontSize={11} tickLine={false} axisLine={false} />
                                                    <Tooltip
                                                        contentStyle={{
                                                            backgroundColor: "var(--chart-tooltip-bg)",
                                                            borderRadius: "12px",
                                                            border: "1px solid var(--chart-tooltip-border)",
                                                            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
                                                            color: "var(--chart-tooltip-text)",
                                                            fontSize: "13px",
                                                        }}
                                                        formatter={(v) => [`₹${parseFloat(v).toFixed(2)}`, "Total Fines"]}
                                                    />
                                                    <Bar dataKey="fine" fill="#ec4899" radius={[6, 6, 0, 0]} maxBarSize={32} />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}
                                </ChartCard>

                                <ChartCard
                                    title="Collection Health & Stock"
                                    subtitle="Inventory copy counts recorded in transaction facts"
                                >
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, paddingTop: 6 }}>
                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)", padding: "16px" }}>
                                            <span className="kpi-card__label">Total Copies</span>
                                            <h3 className="kpi-card__value" style={{ fontSize: "1.4rem" }}>
                                                {Number(collHealth.total_copies || 0).toLocaleString()}
                                            </h3>
                                            <span className="kpi-card__desc">Fact copy volume</span>
                                        </div>
                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)", padding: "16px" }}>
                                            <span className="kpi-card__label">Available Copies</span>
                                            <h3 className="kpi-card__value" style={{ fontSize: "1.4rem", color: "#10b981" }}>
                                                {Number(collHealth.available_copies || 0).toLocaleString()}
                                            </h3>
                                            <span className="kpi-card__desc">In stock during tx</span>
                                        </div>
                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)", padding: "16px" }}>
                                            <span className="kpi-card__label">Unavailable Copies</span>
                                            <h3 className="kpi-card__value" style={{ fontSize: "1.4rem", color: "var(--primary)" }}>
                                                {Number(collHealth.unavailable_copies || 0).toLocaleString()}
                                            </h3>
                                            <span className="kpi-card__desc">Checked out / hold</span>
                                        </div>
                                        <div className="kpi-card" style={{ boxShadow: "none", border: "1px solid var(--border)", padding: "16px" }}>
                                            <span className="kpi-card__label">Zero Stock Records</span>
                                            <h3 className="kpi-card__value" style={{ fontSize: "1.4rem", color: "#ef4444" }}>
                                                {Number(collHealth.zero_available_count || 0)}
                                            </h3>
                                            <span className="kpi-card__desc">Transactions at 0 stock</span>
                                        </div>
                                    </div>
                                </ChartCard>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}

export default Dashboard;