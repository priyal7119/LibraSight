import React, { useState, useMemo } from "react";
import { Search, ChevronLeft, ChevronRight, X } from "lucide-react";
import { EmptyState } from "./LoadingErrorState";

function DataTable({
    columns,
    data = [],
    searchPlaceholder = "Search records...",
    pageSize = 10,
    showSearch = true,
    showPagination = true,
}) {
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);

    const filteredData = useMemo(() => {
        if (!data || data.length === 0) return [];
        if (!searchQuery.trim()) return data;

        const query = searchQuery.toLowerCase().trim();
        return data.filter((row) =>
            columns.some((col) => {
                const val = row[col.key];
                if (val === null || val === undefined) return false;
                return String(val).toLowerCase().includes(query);
            })
        );
    }, [data, columns, searchQuery]);

    const totalPages = Math.max(1, Math.ceil(filteredData.length / pageSize));
    const paginatedData = useMemo(() => {
        if (!showPagination) return filteredData;
        const startIndex = (currentPage - 1) * pageSize;
        return filteredData.slice(startIndex, startIndex + pageSize);
    }, [filteredData, currentPage, pageSize, showPagination]);

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
        setCurrentPage(1);
    };

    if (!data || data.length === 0) {
        return <EmptyState title="No records found" message="There are currently no records to display." />;
    }

    return (
        <div className="table-container">
            {showSearch && (
                <div className="table-toolbar">
                    <div className="table-search">
                        <Search size={16} />
                        <input
                            type="text"
                            placeholder={searchPlaceholder}
                            value={searchQuery}
                            onChange={handleSearchChange}
                            aria-label={searchPlaceholder}
                        />
                        {searchQuery && (
                            <button
                                className="table-search__clear"
                                onClick={() => { setSearchQuery(""); setCurrentPage(1); }}
                                aria-label="Clear search"
                            >
                                <X size={14} />
                            </button>
                        )}
                    </div>
                    <span className="table-count">
                        Showing {filteredData.length} of {data.length} records
                    </span>
                </div>
            )}

            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            {columns.map((column) => (
                                <th key={column.key} style={column.style || {}}>
                                    {column.label}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {paginatedData.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length} style={{ textAlign: "center", padding: "32px" }}>
                                    No records match "{searchQuery}"
                                </td>
                            </tr>
                        ) : (
                            paginatedData.map((row, rowIndex) => (
                                <tr key={row.id || row.transaction_id || row.book_id || row.reader_id || row.branch_id || rowIndex}>
                                    {columns.map((column) => {
                                        const rawValue = row[column.key];
                                        return (
                                            <td key={column.key} style={column.style || {}}>
                                                {column.render
                                                    ? column.render(rawValue, row)
                                                    : rawValue === null || rawValue === undefined || rawValue === ""
                                                    ? <span className="null-val">N/A</span>
                                                    : String(rawValue)}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {showPagination && totalPages > 1 && (
                <div className="table-pagination">
                    <span className="table-pagination__info">
                        Page {currentPage} of {totalPages}
                    </span>
                    <div className="table-pagination__buttons">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                            aria-label="Previous page"
                        >
                            <ChevronLeft size={15} style={{ verticalAlign: "middle" }} /> Previous
                        </button>
                        <button
                            disabled={currentPage === totalPages}
                            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                            aria-label="Next page"
                        >
                            Next <ChevronRight size={15} style={{ verticalAlign: "middle" }} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default DataTable;