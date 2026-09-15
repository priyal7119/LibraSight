import React, { useEffect, useState, useMemo } from "react";
import { TrendingUp, Calendar, BookOpen } from "lucide-react";
import ChartCard from "../components/ChartCard";
import { LoadingSkeleton, ErrorMessage } from "../components/LoadingErrorState";
import MonthlyTrendsChart from "../charts/MonthlyTrendsChart";
import GenreDistributionChart from "../charts/GenreDistributionChart";
import YearComparisonChart from "../charts/YearComparisonChart";
import { getDashboardTrends, getBookGenres } from "../services/api";

function ReadingTrends() {
    const [trends, setTrends] = useState([]);
    const [genres, setGenres] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [trendsRes, genreRes] = await Promise.all([
                getDashboardTrends(),
                getBookGenres(),
            ]);
            setTrends(trendsRes.data);
            setGenres(genreRes.data);
        } catch (err) {
            console.error("Reading Trends load error:", err);
            setError("Unable to load reading trend data from the backend.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const insights = useMemo(() => {
        if (!trends || trends.length === 0) return null;

        const totalTxns = trends.reduce((s, t) => s + Number(t.transaction_count || 0), 0);

        const byMonth = {};
        trends.forEach((t) => {
            const key = t.month_name;
            byMonth[key] = (byMonth[key] || 0) + Number(t.transaction_count || 0);
        });
        const busiest = Object.entries(byMonth).sort((a, b) => b[1] - a[1])[0];

        const byYear = {};
        trends.forEach((t) => {
            byYear[t.year] = (byYear[t.year] || 0) + Number(t.transaction_count || 0);
        });
        const years = Object.keys(byYear).sort();
        const latestYear = years[years.length - 1];
        const earliestYear = years[0];

        return {
            totalTxns,
            busiestMonth: busiest ? busiest[0] : "—",
            busiestMonthCount: busiest ? busiest[1] : 0,
            yearCount: years.length,
            latestYear,
            earliestYear,
        };
    }, [trends]);

    if (loading) {
        return (
            <div>
                <div className="page-header"><div><h1>Reading Trends</h1><p>Loading trend data...</p></div></div>
                <LoadingSkeleton count={3} height={120} />
                <LoadingSkeleton count={1} height={360} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Reading Trends</h1><p>Library circulation over time</p></div></div>
                <ErrorMessage message={error} onRetry={loadData} />
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Reading Trends</h1>
                    <p>Monthly circulation, year-over-year comparison, and genre distribution</p>
                </div>
            </div>

            {/* Key Insights Cards */}
            {insights && (
                <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 28 }}>
                    <div className="kpi-card">
                        <div className="kpi-card__header">
                            <div className="kpi-card__icon-wrapper">
                                <TrendingUp size={20} />
                            </div>
                        </div>
                        <div className="kpi-card__body">
                            <span className="kpi-card__label">Total Circulation</span>
                            <h3 className="kpi-card__value">{insights.totalTxns.toLocaleString()}</h3>
                        </div>
                        <div className="kpi-card__footer"><span className="kpi-card__desc">Across {insights.yearCount} year{insights.yearCount > 1 ? "s" : ""} ({insights.earliestYear}–{insights.latestYear})</span></div>
                    </div>
                    <div className="kpi-card">
                        <div className="kpi-card__header">
                            <div className="kpi-card__icon-wrapper">
                                <Calendar size={20} />
                            </div>
                        </div>
                        <div className="kpi-card__body">
                            <span className="kpi-card__label">Busiest Month</span>
                            <h3 className="kpi-card__value" style={{ fontSize: "1.7rem" }}>{insights.busiestMonth}</h3>
                        </div>
                        <div className="kpi-card__footer"><span className="kpi-card__desc">{insights.busiestMonthCount} transactions (all years)</span></div>
                    </div>
                    <div className="kpi-card">
                        <div className="kpi-card__header">
                            <div className="kpi-card__icon-wrapper">
                                <BookOpen size={20} />
                            </div>
                        </div>
                        <div className="kpi-card__body">
                            <span className="kpi-card__label">Top Genre</span>
                            <h3 className="kpi-card__value" style={{ fontSize: "1.5rem" }}>
                                {genres.length > 0 ? genres[0].genre : "—"}
                            </h3>
                        </div>
                        <div className="kpi-card__footer">
                            <span className="kpi-card__desc">
                                {genres.length > 0 ? `${genres[0].transaction_count} borrows` : "No genre data"}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Monthly Trends Chart */}
            <ChartCard
                title="Monthly Circulation Trends"
                subtitle="Chronological library checkout activity — correctly ordered by year and month"
                className="chart-card--full"
            >
                <MonthlyTrendsChart data={trends} />
            </ChartCard>

            <div style={{ marginBottom: 28 }} />

            {/* Year Comparison + Genre Distribution */}
            <div className="analytics-grid">
                <ChartCard
                    title="Year-Over-Year Circulation"
                    subtitle="Annual checkout volume comparison from warehouse star schema"
                >
                    <YearComparisonChart data={trends} />
                </ChartCard>

                <ChartCard
                    title="Genre Distribution"
                    subtitle="Circulation volumes across all book genres"
                >
                    <GenreDistributionChart data={genres} />
                </ChartCard>
            </div>
        </div>
    );
}

export default ReadingTrends;