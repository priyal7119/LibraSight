import React, { useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import ChartCard from "../components/ChartCard";
import StatusBadge from "../components/StatusBadge";
import { LoadingSkeleton, ErrorMessage } from "../components/LoadingErrorState";
import GenreDistributionChart from "../charts/GenreDistributionChart";
import { getBooks, getTopBooks, getBookGenres } from "../services/api";

function Books() {
    // Pagination, sorting, search state
    const [books, setBooks] = useState([]);
    const [totalBooks, setTotalBooks] = useState(0);
    const [page, setPage] = useState(1);
    const pageSize = 12;
    const [search, setSearch] = useState("");
    const [sortBy, setSortBy] = useState("");
    const [order, setOrder] = useState("asc");

    const [topBooks, setTopBooks] = useState([]);
    const [genres, setGenres] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Load paginated books list
    const loadBooks = async () => {
        try {
            const params = {
                skip: (page - 1) * pageSize,
                limit: pageSize,
                ...(search && { search }),
                ...(sortBy && { sort_by: sortBy }),
                ...(order && { order })
            };
            const res = await getBooks(params);
            setBooks(res.data.items);
            setTotalBooks(res.data.total);
        } catch (err) {
            console.error("Books load error:", err);
            setError("Unable to load book data from the backend.");
        }
    };

    // Load analytics (top books & genre distribution)
    const loadAnalytics = async () => {
        const [topRes, genreRes] = await Promise.all([
            getTopBooks(),
            getBookGenres()
        ]);
        setTopBooks(topRes.data);
        setGenres(genreRes.data);
    };

    const loadAll = async () => {
        setLoading(true);
        setError("");
        try {
            await Promise.all([loadAnalytics(), loadBooks()]);
        } catch (_) {}
        setLoading(false);
    };

    // Initial load
    useEffect(() => {
        loadAll();
    }, []);

    // Refetch books when pagination/search/sorting changes
    useEffect(() => {
        if (!loading) loadBooks();
    }, [page, search, sortBy, order]);

    if (loading) {
        return (
            <div>
                <div className="page-header"><div><h1>Books</h1><p>Loading book data...</p></div></div>
                <LoadingSkeleton count={3} height={100} />
                <LoadingSkeleton count={1} height={320} />
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="page-header"><div><h1>Books</h1><p>Book collection &amp; catalog</p></div></div>
                <ErrorMessage message={error} onRetry={loadAll} />
            </div>
        );
    }

    const topBooksColumns = [
        { key: "book_title", label: "Title" },
        { key: "author", label: "Author" },
        { key: "genre", label: "Genre", render: (g) => <StatusBadge status={g} /> },
        { key: "transaction_count", label: "Circulations", render: (c) => (<span style={{ fontWeight: 700, color: "var(--primary)" }}>{c}</span>) }
    ];

    const bookColumns = [
        { key: "book_id", label: "Book ID" },
        { key: "book_title", label: "Title" },
        { key: "author", label: "Author" },
        { key: "genre", label: "Genre", render: (g) => <StatusBadge status={g} /> },
        { key: "publication_year", label: "Year" },
        { key: "language", label: "Language" },
        { key: "format", label: "Format" },
        { key: "publisher", label: "Publisher" },
        { key: "isbn", label: "ISBN" }
    ];

    const totalPages = Math.max(1, Math.ceil(totalBooks / pageSize));

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Books</h1>
                    <p>Collection catalog, top titles, and genre analytics</p>
                </div>
                <StatusBadge status={`${totalBooks} Titles`} />
            </div>

            {/* Top Books + Genre Distribution */}
            <div className="analytics-grid">
                <ChartCard title="Top 10 Most Borrowed Titles" subtitle="Ranked by total circulation count">
                    <DataTable columns={topBooksColumns} data={topBooks} showSearch={false} showPagination={false} />
                </ChartCard>
                <ChartCard title="Genre Distribution" subtitle="Transaction volume by book genre">
                    <GenreDistributionChart data={genres} />
                </ChartCard>
            </div>

            {/* Complete Books Table */}
            <div className="table-container">
                <div className="table-toolbar">
                    <h3 className="chart-card__title" style={{ margin: 0 }}>Complete Book Catalog</h3>
                    <span className="table-count">{totalBooks} titles</span>
                </div>
                <DataTable
                    columns={bookColumns}
                    data={books}
                    searchPlaceholder="Search title, author, genre, ISBN..."
                    pageSize={pageSize}
                    showPagination={false}
                />
                {/* Server‑side pagination controls */}
                <div className="table-pagination" style={{ marginTop: "12px", textAlign: "center" }}>
                    <span>Page {page} of {totalPages}</span>
                    <div style={{ display: "inline-block", marginLeft: "12px" }}>
                        <button disabled={page === 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Previous</button>
                        <button disabled={page === totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))} style={{ marginLeft: "8px" }}>Next</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Books;