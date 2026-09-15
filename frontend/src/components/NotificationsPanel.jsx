import React from "react";
import { Link } from "react-router-dom";
import {
    AlertTriangle,
    Bookmark,
    ShieldAlert,
    CheckCircle2,
    X,
    ExternalLink,
} from "lucide-react";

function NotificationsPanel({ notifications = [], onClose }) {
    const getIcon = (type) => {
        switch (type) {
            case "warning":
                return <AlertTriangle size={18} />;
            case "danger":
                return <ShieldAlert size={18} />;
            case "info":
                return <Bookmark size={18} />;
            default:
                return <CheckCircle2 size={18} />;
        }
    };

    return (
        <div className="notifications-panel">
            <div className="notifications-panel__header">
                <div className="notifications-panel__title">
                    <span>Notifications</span>
                    {notifications.length > 0 && (
                        <span className="notifications-panel__badge">
                            {notifications.length} Active
                        </span>
                    )}
                </div>
                <button
                    className="icon-btn"
                    style={{ width: 28, height: 28 }}
                    onClick={onClose}
                    aria-label="Close notifications"
                >
                    <X size={16} />
                </button>
            </div>

            <div className="notifications-panel__list">
                {notifications.length === 0 ? (
                    <div className="notifications-panel__empty">
                        <CheckCircle2 size={32} />
                        <p>No new notifications</p>
                    </div>
                ) : (
                    notifications.map((notif) => (
                        <Link
                            key={notif.id}
                            to={notif.link}
                            className="notification-item"
                            onClick={onClose}
                        >
                            <div
                                className={`notification-item__icon notification-item__icon--${
                                    notif.type || "info"
                                }`}
                            >
                                {getIcon(notif.type)}
                            </div>
                            <div className="notification-item__content">
                                <div className="notification-item__top">
                                    <span className="notification-item__title">
                                        {notif.title}
                                    </span>
                                    {notif.priority && (
                                        <span
                                            className={`notification-item__priority notification-item__priority--${notif.priority.toLowerCase()}`}
                                        >
                                            {notif.priority}
                                        </span>
                                    )}
                                </div>
                                <p className="notification-item__message">
                                    {notif.message}
                                </p>
                            </div>
                        </Link>
                    ))
                )}
            </div>
        </div>
    );
}

export default NotificationsPanel;
