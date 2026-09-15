import React, { useState, useEffect, useRef } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import {
    Library,
    Search,
    Bell,
    Sun,
    Moon,
    Menu,
    X,
    BookOpen,
    Users,
    Building2,
    Loader2,
} from "lucide-react";
import NotificationsPanel from "./NotificationsPanel";
import { getNotifications, globalSearch } from "../services/api";

function Navbar({ onToggleSidebar }) {
    const location = useLocation();
    const navigate = useNavigate();

    const [theme, setTheme] = useState(
        () => localStorage.getItem("libraSightTheme") || "light"
    );
    const [notificationsOpen, setNotificationsOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);

    // Search state
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState(null);
    const [isSearching, setIsSearching] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);

    const notifRef = useRef(null);
    const searchRef = useRef(null);

    // Synchronize data-theme on documentElement
    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("libraSightTheme", theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme((prev) => (prev === "dark" ? "light" : "dark"));
    };

    // Load real notifications from backend
    useEffect(() => {
        let isMounted = true;
        getNotifications()
            .then((res) => {
                if (isMounted) {
                    const list = res.data.notifications || [];
                    setNotifications(list);
                    setUnreadCount(list.length);
                }
            })
            .catch((err) => {
                console.warn("Notifications load error:", err);
            });
        return () => {
            isMounted = false;
        };
    }, []);

    // Live search debounced query to PostgreSQL backend
    useEffect(() => {
        if (!searchQuery.trim()) {
            setSearchResults(null);
            setIsSearching(false);
            return;
        }

        setIsSearching(true);
        const timer = setTimeout(() => {
            globalSearch(searchQuery)
                .then((res) => {
                    setSearchResults(res.data);
                    setIsSearching(false);
                    setSearchOpen(true);
                })
                .catch((err) => {
                    console.warn("Global search error:", err);
                    setIsSearching(false);
                });
        }, 250);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Close notifications and search panel on outside click
    useEffect(() => {
        function handleClickOutside(e) {
            if (notifRef.current && !notifRef.current.contains(e.target)) {
                setNotificationsOpen(false);
            }
            if (searchRef.current && !searchRef.current.contains(e.target)) {
                setSearchOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Handle pressing Enter on search input
    const handleSearchKeyDown = (e) => {
        if (e.key === "Enter" && searchQuery.trim()) {
            setSearchOpen(false);
            // If books matched, navigate to /books
            if (searchResults && searchResults.books && searchResults.books.length > 0) {
                navigate("/books");
            } else if (searchResults && searchResults.readers && searchResults.readers.length > 0) {
                navigate("/readers");
            } else if (searchResults && searchResults.branches && searchResults.branches.length > 0) {
                navigate("/branches");
            } else {
                navigate("/books");
            }
        }
    };

    const handleClearSearch = () => {
        setSearchQuery("");
        setSearchResults(null);
        setSearchOpen(false);
    };

    const handleSelectResult = (path) => {
        setSearchOpen(false);
        navigate(path);
    };

    const getPageTitle = (path) => {
        switch (path) {
            case "/":
            case "/dashboard":
                return "Analytics Dashboard";
            case "/books":
                return "Books & Catalog";
            case "/readers":
                return "Reader Activity";
            case "/branches":
                return "Branch Performance";
            case "/reading-trends":
                return "Reading Trends";
            case "/collection":
                return "Collection Health";
            case "/data-quality":
                return "Data Quality & Audit";
            case "/reports":
                return "Analytical Reports";
            default:
                return "Public Library Analytics";
        }
    };

    const hasResults =
        searchResults &&
        (searchResults.books.length > 0 ||
            searchResults.readers.length > 0 ||
            searchResults.branches.length > 0);

    return (
        <header className="navbar">
            <div className="navbar__left">
                <button
                    className="mobile-menu-btn"
                    onClick={onToggleSidebar}
                    aria-label="Toggle navigation menu"
                >
                    <Menu size={20} />
                </button>

                {/* LibraSight Branding -> Click navigates to / */}
                <Link to="/" className="navbar-brand-link" aria-label="LibraSight Home">
                    <div className="navbar-brand">
                        <div className="navbar-brand__logo">
                            <Library size={20} />
                        </div>
                        <div className="navbar-brand__text">
                            <h2>LibraSight</h2>
                            <span>Public Library Analytics</span>
                        </div>
                    </div>
                </Link>

                <div className="navbar__page-tag">
                    <span className="navbar__page-separator">/</span>
                    <span className="navbar__page-title">{getPageTitle(location.pathname)}</span>
                </div>
            </div>

            <div className="navbar__right">
                {/* Global Search Component */}
                <div className="header-search" ref={searchRef}>
                    <button
                        type="button"
                        className="header-search__icon-btn"
                        onClick={() => {
                            if (searchQuery.trim()) {
                                setSearchOpen(true);
                            }
                        }}
                        aria-label="Search database"
                    >
                        {isSearching ? (
                            <Loader2 size={16} className="search-spinner" />
                        ) : (
                            <Search size={16} />
                        )}
                    </button>
                    <input
                        type="text"
                        placeholder="Search books, readers, branches..."
                        value={searchQuery}
                        onChange={(e) => {
                            setSearchQuery(e.target.value);
                            setSearchOpen(true);
                        }}
                        onFocus={() => {
                            if (searchQuery.trim()) {
                                setSearchOpen(true);
                            }
                        }}
                        onKeyDown={handleSearchKeyDown}
                        aria-label="Search books, readers, and branches in PostgreSQL"
                    />
                    {searchQuery && (
                        <button
                            type="button"
                            className="header-search__clear"
                            onClick={handleClearSearch}
                            aria-label="Clear search"
                        >
                            <X size={14} />
                        </button>
                    )}

                    {/* Search Results Dropdown */}
                    {searchOpen && searchQuery.trim() && (
                        <div className="search-dropdown">
                            {isSearching && !searchResults ? (
                                <div className="search-dropdown__loading">
                                    <Loader2 size={18} className="search-spinner" />
                                    <span>Searching PostgreSQL database...</span>
                                </div>
                            ) : !hasResults ? (
                                <div className="search-dropdown__empty">
                                    <p>No results found for "{searchQuery}"</p>
                                    <span>Try searching for a title, author, reader name, or branch</span>
                                </div>
                            ) : (
                                <div className="search-dropdown__content">
                                    {/* Books Section */}
                                    {searchResults.books.length > 0 && (
                                        <div className="search-section">
                                            <div className="search-section__title">
                                                <BookOpen size={14} />
                                                <span>Books ({searchResults.books.length})</span>
                                            </div>
                                            {searchResults.books.map((b) => (
                                                <div
                                                    key={b.book_id}
                                                    className="search-item"
                                                    onClick={() => handleSelectResult("/books")}
                                                >
                                                    <span className="search-item__primary">
                                                        {b.book_title}
                                                    </span>
                                                    <span className="search-item__secondary">
                                                        {b.author} · {b.genre}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Readers Section */}
                                    {searchResults.readers.length > 0 && (
                                        <div className="search-section">
                                            <div className="search-section__title">
                                                <Users size={14} />
                                                <span>Readers ({searchResults.readers.length})</span>
                                            </div>
                                            {searchResults.readers.map((r) => (
                                                <div
                                                    key={r.reader_id}
                                                    className="search-item"
                                                    onClick={() => handleSelectResult("/readers")}
                                                >
                                                    <span className="search-item__primary">
                                                        {r.reader_name}
                                                    </span>
                                                    <span className="search-item__secondary">
                                                        ID: {r.reader_id} · {r.reader_type}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Branches Section */}
                                    {searchResults.branches.length > 0 && (
                                        <div className="search-section">
                                            <div className="search-section__title">
                                                <Building2 size={14} />
                                                <span>Branches ({searchResults.branches.length})</span>
                                            </div>
                                            {searchResults.branches.map((br) => (
                                                <div
                                                    key={br.branch_id}
                                                    className="search-item"
                                                    onClick={() => handleSelectResult("/branches")}
                                                >
                                                    <span className="search-item__primary">
                                                        {br.branch_name}
                                                    </span>
                                                    <span className="search-item__secondary">
                                                        {br.city} · {br.area}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Dark Mode Toggle */}
                <button
                    className="icon-btn"
                    onClick={toggleTheme}
                    aria-label="Toggle dark mode"
                    title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
                >
                    {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
                </button>

                {/* Notifications Bell */}
                <div style={{ position: "relative" }} ref={notifRef}>
                    <button
                        className="icon-btn"
                        onClick={() => setNotificationsOpen((prev) => !prev)}
                        aria-label="View notifications"
                        title="Notifications"
                    >
                        <Bell size={18} />
                        {unreadCount > 0 && <span className="icon-btn__badge" />}
                    </button>

                    {notificationsOpen && (
                        <NotificationsPanel
                            notifications={notifications}
                            onClose={() => setNotificationsOpen(false)}
                        />
                    )}
                </div>

                {/* User Profile */}
                <div className="user-profile">
                    <div className="user-profile__avatar">
                        LS
                    </div>
                    <div className="user-profile__info">
                        <span className="user-profile__name">Library Staff</span>
                        <span className="user-profile__role">Admin</span>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Navbar;