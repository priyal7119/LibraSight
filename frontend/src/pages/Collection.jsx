import React, { useEffect, useState } from "react";
import { LibraryBig, TrendingUp, BookOpen, AlertTriangle } from "lucide-react";
import ChartCard from "../components/ChartCard";
import DataTable from "../components/DataTable";
import { LoadingSkeleton, ErrorMessage, EmptyState } from "../components/LoadingErrorState";
import { getCollectionSummary } from "../services/api";

function Collection() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const res = await getCollectionSummary();
            setData(res.data);
        } catch (err) {
            console.error("Collection load error:", err);
            setError("Unable to load collection data from the backend.");
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
                <div className="page-header"><div><h1>Collection</h1><p>Loading collection data...</p></div></div>
                <LoadingSkeleton count={3} height={120} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Collection</h1><p>Collection health &amp; availability</p></div></div>
                <ErrorMessage message={error} onRetry={loadData} />
            </div>
        );
    }

    const lowStockColumns = [
        { key: "book_id", label: "Book ID" },
        { key: "book_title", label: "Title" },
        { key: "author", label: "Author" },
        { key: "genre", label: "Genre" },
        {
            key: "available_copies",
            label: "Available",
            render: (v) => (
                <span style={{
                    fontWeight: 700,
                    color: "var(--danger)",
                    background: "var(--danger-bg)",
                    borderRadius: 6,
                    padding: "2px 8px",
                    fontSize: "0.82rem",
                }}>
                    {v} copies
                </span>
            ),
        },
        { key: "total_copies", label: "Total Copies" },
        {
            key: "reservation_count",
            label: "Reservations",
            render: (v) => <strong>{v || 0}</strong>,
        },
    ];

    const reservationColumns = [
        { key: "book_id", label: "Book ID" },
        { key: "book_title", label: "Title" },
        { key: "author", label: "Author" },
        { key: "genre", label: "Genre" },
        {
            key: "total_reservations",
            label: "Total Reservations",
            render: (v) => (
                <span style={{
                    fontWeight: 700,
                    color: "var(--primary)",
                    background: "var(--primary-light)",
                    borderRadius: 6,
                    padding: "2px 10px",
                }}>
                    {v}
                </span>
            ),
        },
        { key: "transaction_count", label: "Circulations" },
        {
            key: "avg_available",
            label: "Avg. Available",
            render: (v) => v !== null && v !== undefined ? parseFloat(v).toFixed(1) : "N/A",
        },
    ];

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Collection</h1>
                    <p>Collection health, stock availability, and high-demand titles</p>
                </div>
                <span style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "5px 12px",
                    borderRadius: 9999,
                    background: "var(--success-bg)",
                    color: "var(--success)",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                }}>
                    <span style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--success)", display: "inline-block" }} />
                    {data?.collection_status || "Healthy"}
                </span>
            </div>

            {/* Collection Health KPI Row */}
            <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 28 }}>
                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper">
                            <TrendingUp size={20} />
                        </div>
                        <span className="kpi-card__badge">{data?.collection_status}</span>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Total Transactions</span>
                        <h3 className="kpi-card__value">{(data?.total_transactions || 0).toLocaleString()}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">All checkout records in warehouse</span></div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper">
                            <BookOpen size={20} />
                        </div>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Avg. Available Copies</span>
                        <h3 className="kpi-card__value">{parseFloat(data?.avg_available_copies || 0).toFixed(1)}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">Average per transaction record</span></div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-card__header">
                        <div className="kpi-card__icon-wrapper" style={{ background: "var(--danger-bg)", color: "var(--danger)" }}>
                            <AlertTriangle size={20} />
                        </div>
                    </div>
                    <div className="kpi-card__body">
                        <span className="kpi-card__label">Zero Availability Records</span>
                        <h3 className="kpi-card__value" style={{ color: "var(--danger)" }}>{data?.zero_available_count || 0}</h3>
                    </div>
                    <div className="kpi-card__footer"><span className="kpi-card__desc">Transaction records with 0 copies</span></div>
                </div>
            </div>

            {/* Low Stock Alerts Table */}
            <ChartCard
                title="Low Stock Alerts"
                subtitle="Cataloged titles where available copies = 0 in checkout transactions"
            >
                {!data?.low_stock_alerts || data.low_stock_alerts.length === 0 ? (
                    <EmptyState title="No Low Stock Issues" message="All tracked books have available copies in the warehouse." />
                ) : (
                    <DataTable
                        columns={lowStockColumns}
                        data={data.low_stock_alerts}
                        searchPlaceholder="Search low-stock titles..."
                        pageSize={8}
                    />
                )}
            </ChartCard>

            <div style={{ marginBottom: 28 }} />

            {/* Reservation-Heavy Titles Table */}
            <ChartCard
                title="High-Demand Reservation Titles"
                subtitle="Books with highest hold queue demand from transaction facts"
            >
                {!data?.reservation_heavy || data.reservation_heavy.length === 0 ? (
                    <EmptyState title="No Reservation Data" message="No reservation records found in the current dataset." />
                ) : (
                    <DataTable
                        columns={reservationColumns}
                        data={data.reservation_heavy}
                        searchPlaceholder="Search high-demand titles..."
                        pageSize={10}
                        showPagination={false}
                    />
                )}
            </ChartCard>
        </div>
    );
}

export default Collection;