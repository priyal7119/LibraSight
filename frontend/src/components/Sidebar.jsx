import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
    LayoutDashboard,
    BookOpen,
    Users,
    Building2,
    TrendingUp,
    LibraryBig,
    ShieldCheck,
    FileText,
} from "lucide-react";

function Sidebar({ isOpen, onClose }) {
    const location = useLocation();

    const navItems = [
        {
            to: "/",
            altTo: "/dashboard",
            label: "Dashboard",
            icon: <LayoutDashboard size={19} />,
        },
        {
            to: "/books",
            label: "Books",
            icon: <BookOpen size={19} />,
        },
        {
            to: "/readers",
            label: "Readers",
            icon: <Users size={19} />,
        },
        {
            to: "/branches",
            label: "Branches",
            icon: <Building2 size={19} />,
        },
        {
            to: "/reading-trends",
            label: "Reading Trends",
            icon: <TrendingUp size={19} />,
        },
        {
            to: "/collection",
            label: "Collection",
            icon: <LibraryBig size={19} />,
        },
        {
            to: "/data-quality",
            label: "Data Quality",
            icon: <ShieldCheck size={19} />,
        },
        {
            to: "/reports",
            label: "Reports",
            icon: <FileText size={19} />,
        },
    ];

    const isItemActive = (item) => {
        if (item.to === "/" && (location.pathname === "/" || location.pathname === "/dashboard")) {
            return true;
        }
        return location.pathname === item.to;
    };

    return (
        <>
            {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}
            <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
                <nav className="sidebar__nav">
                    {navItems.map((item) => {
                        const active = isItemActive(item);
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={`sidebar__item ${active ? "sidebar__item--active" : ""}`}
                                onClick={onClose}
                            >
                                <span className="sidebar__icon">{item.icon}</span>
                                <span className="sidebar__label">{item.label}</span>
                                {active && <span className="sidebar__active-pill" />}
                            </NavLink>
                        );
                    })}
                </nav>

                <div className="sidebar__footer">
                    <div className="warehouse-status">
                        <span className="warehouse-status__indicator" />
                        <div className="warehouse-status__text">
                            <span className="warehouse-status__title">Warehouse Star Schema</span>
                            <span className="warehouse-status__sub">PostgreSQL Active</span>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
}

export default Sidebar;