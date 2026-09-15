import React, { useState, useEffect } from "react";
import {
    SlidersHorizontal,
    RotateCcw,
    Check,
    X,
    ChevronDown,
    AlertCircle,
} from "lucide-react";
import { getFilterYears, getBranches, getBookGenres } from "../services/api";

function FilterPanel({ filters, onApplyFilters, onResetFilters }) {
    const [years, setYears] = useState([]);
    const [branches, setBranches] = useState([]);
    const [genres, setGenres] = useState([]);

    // Internal state for form controls before user clicks Apply
    const [selectedYear, setSelectedYear] = useState(filters.year || "");
    const [selectedBranch, setSelectedBranch] = useState(filters.branch_id || "");
    const [selectedGenre, setSelectedGenre] = useState(filters.genre || "");
    const [startDate, setStartDate] = useState(filters.start_date || "");
    const [endDate, setEndDate] = useState(filters.end_date || "");
    const [dateError, setDateError] = useState("");

    // Load dynamic dropdown options from PostgreSQL backend
    useEffect(() => {
        let isMounted = true;
        Promise.all([getFilterYears(), getBranches(), getBookGenres()])
            .then(([yearsRes, branchesRes, genresRes]) => {
                if (isMounted) {
                    const yearsData = yearsRes && yearsRes.data;
                    const branchesData = branchesRes && branchesRes.data;
                    const genresData = genresRes && genresRes.data;

                    setYears(Array.isArray(yearsData) ? yearsData : yearsData?.years || []);
                    setBranches(Array.isArray(branchesData) ? branchesData : branchesData?.branches || []);
                    setGenres(Array.isArray(genresData) ? genresData : genresData?.genres || []);
                }
            })
            .catch((err) => {
                console.warn("Error loading filter options:", err);
            });
        return () => {
            isMounted = false;
        };
    }, []);

    // Sync with incoming prop changes (e.g. on reset or badge removal)
    useEffect(() => {
        setSelectedYear(filters.year || "");
        setSelectedBranch(filters.branch_id || "");
        setSelectedGenre(filters.genre || "");
        setStartDate(filters.start_date || "");
        setEndDate(filters.end_date || "");
        setDateError("");
    }, [filters]);

    const handleApply = (e) => {
        if (e) e.preventDefault();

        // Validate date range
        if (startDate && endDate && startDate > endDate) {
            setDateError("Start date must be before end date.");
            return;
        }
        setDateError("");

        onApplyFilters({
            year: selectedYear,
            branch_id: selectedBranch,
            genre: selectedGenre,
            start_date: startDate,
            end_date: endDate,
        });
    };

    const handleReset = () => {
        setSelectedYear("");
        setSelectedBranch("");
        setSelectedGenre("");
        setStartDate("");
        setEndDate("");
        setDateError("");
        onResetFilters();
    };

    // Construct active filter pills
    const activePills = [];
    if (filters.year) {
        activePills.push({
            key: "year",
            label: `Year: ${filters.year}`,
        });
    }
    if (filters.branch_id) {
        const branchObj = branches.find((b) => b.branch_id === filters.branch_id);
        const bName = branchObj ? branchObj.branch_name : filters.branch_id;
        activePills.push({
            key: "branch_id",
            label: `Branch: ${bName}`,
        });
    }
    if (filters.genre) {
        activePills.push({
            key: "genre",
            label: `Genre: ${filters.genre}`,
        });
    }
    if (filters.start_date && filters.end_date) {
        activePills.push({
            key: "date_range",
            label: `${filters.start_date} → ${filters.end_date}`,
        });
    } else if (filters.start_date) {
        activePills.push({
            key: "start_date",
            label: `From: ${filters.start_date}`,
        });
    } else if (filters.end_date) {
        activePills.push({
            key: "end_date",
            label: `To: ${filters.end_date}`,
        });
    }

    const removeFilter = (filterKey) => {
        const updated = { ...filters };
        if (filterKey === "date_range") {
            delete updated.start_date;
            delete updated.end_date;
        } else {
            delete updated[filterKey];
        }
        onApplyFilters(updated);
    };

    const hasActiveFilters = activePills.length > 0;

    return (
        <div className="filter-card">
            <form onSubmit={handleApply}>
                <div className="filter-card__header">
                    <div className="filter-card__title">
                        <SlidersHorizontal size={18} />
                        <span>Analytics Filters</span>
                    </div>

                    {/* Top-Right Header Actions */}
                    <div className="filter-actions">
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={handleReset}
                            aria-label="Reset filters"
                            title="Reset all filters"
                            disabled={!hasActiveFilters && !selectedYear && !selectedBranch && !selectedGenre && !startDate && !endDate}
                        >
                            <RotateCcw size={14} />
                            Reset
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                            aria-label="Apply filters"
                            title="Apply selected filters"
                        >
                            <Check size={14} />
                            Apply Filters
                        </button>
                    </div>
                </div>

                <div className="filter-card__grid">
                    {/* Year Filter */}
                    <div className="filter-group">
                        <label htmlFor="filter-year">Year</label>
                        <div className="filter-select-wrapper">
                            <select
                                id="filter-year"
                                className="filter-select"
                                value={selectedYear}
                                onChange={(e) => setSelectedYear(e.target.value)}
                            >
                                <option value="">All Years</option>
                                {years.map((y) => (
                                    <option key={y} value={y}>
                                        {y}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown size={14} className="filter-select-icon" />
                        </div>
                    </div>

                    {/* Branch Filter */}
                    <div className="filter-group">
                        <label htmlFor="filter-branch">Branch</label>
                        <div className="filter-select-wrapper">
                            <select
                                id="filter-branch"
                                className="filter-select"
                                value={selectedBranch}
                                onChange={(e) => setSelectedBranch(e.target.value)}
                            >
                                <option value="">All Branches</option>
                                {branches.map((b) => (
                                    <option key={b.branch_id} value={b.branch_id}>
                                        {b.branch_name}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown size={14} className="filter-select-icon" />
                        </div>
                    </div>

                    {/* Genre Filter */}
                    <div className="filter-group">
                        <label htmlFor="filter-genre">Genre</label>
                        <div className="filter-select-wrapper">
                            <select
                                id="filter-genre"
                                className="filter-select"
                                value={selectedGenre}
                                onChange={(e) => setSelectedGenre(e.target.value)}
                            >
                                <option value="">All Genres</option>
                                {genres.map((g) => (
                                    <option key={g.genre} value={g.genre}>
                                        {g.genre}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown size={14} className="filter-select-icon" />
                        </div>
                    </div>

                    {/* Date Range Filter */}
                    <div className="filter-group filter-group--date-range">
                        <label htmlFor="filter-start-date">Date Range</label>
                        <div className="date-range-inputs">
                            <input
                                id="filter-start-date"
                                type="date"
                                className="date-input"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                aria-label="Start Date"
                            />
                            <span className="date-separator">→</span>
                            <input
                                id="filter-end-date"
                                type="date"
                                className="date-input"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                aria-label="End Date"
                            />
                        </div>
                    </div>
                </div>

                {/* Date Validation Alert */}
                {dateError && (
                    <div className="filter-validation-error">
                        <AlertCircle size={15} />
                        <span>{dateError}</span>
                    </div>
                )}
            </form>

            {/* Active Filter Badges */}
            {activePills.length > 0 && (
                <div className="active-filters">
                    <span className="active-filters__label">Active Filters:</span>
                    {activePills.map((pill) => (
                        <span key={pill.key} className="filter-badge">
                            {pill.label}
                            <button
                                type="button"
                                className="filter-badge__remove"
                                onClick={() => removeFilter(pill.key)}
                                aria-label={`Remove ${pill.label}`}
                            >
                                <X size={13} />
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}

export default FilterPanel;