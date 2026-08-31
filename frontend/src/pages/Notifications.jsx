import { useState } from "react";

import { markNotificationsRead } from "../api/notificationApi";

import "../styles/notifications.css";

const notificationMeta = (type) => {
  const key = String(type || "").toLowerCase();

  if (key.includes("payment") && key.includes("success")) {
    return { icon: "✓", label: "Payment success", tone: "success" };
  }
  if (key.includes("return")) {
    return { icon: "↩", label: "Return update", tone: "return" };
  }
  if (key.includes("status") || key.includes("order")) {
    return { icon: "▣", label: "Order update", tone: "order" };
  }
  if (key.includes("payment") && key.includes("fail")) {
    return { icon: "!", label: "Payment issue", tone: "warning" };
  }

  return { icon: "•", label: "Account update", tone: "neutral" };
};

export default function Notifications({ notifications, setNotifications }) {
  const [markingAll, setMarkingAll] = useState(false);

  const handleRead = async (notificationId) => {
    await markNotificationsRead([notificationId]);
    setNotifications((current) => current.map((notification) =>
      notification.id === notificationId
        ? { ...notification, read_status: true }
        : notification,
    ));
  };

  const handleMarkAllRead = async () => {
    setMarkingAll(true);
    try {
      await markNotificationsRead();
      setNotifications((current) => current.map((notification) => ({
        ...notification,
        read_status: true,
      })));
    } finally {
      setMarkingAll(false);
    }
  };

  return (
    <main className="notifications-page">
      <div className="notifications-header">
        <div>
          <p className="notifications-eyebrow">Account updates</p>
          <h1>Notification history</h1>
          <p>All your order and payment updates in one place.</p>
        </div>
        <button
          className="mark-all-button"
          disabled={markingAll || !notifications.some((item) => !item.read_status)}
          onClick={handleMarkAllRead}
          type="button"
        >
          {markingAll ? "Updating..." : "Mark all as read"}
        </button>
      </div>

      <section className="notifications-list" aria-label="Notification history">
        {notifications.length === 0 && (
          <div className="notifications-empty">
            <h2>No notifications yet</h2>
            <p>Order and payment updates will appear here.</p>
          </div>
        )}
        {notifications.map((notification) => {
          const meta = notificationMeta(notification.type);

          return (
            <article
              className={`history-item${notification.read_status ? " is-read" : ""}`}
              key={notification.id}
            >
              <div className={`history-icon ${meta.tone}`} aria-hidden="true">
                {notification.read_status ? "✓" : meta.icon}
              </div>
              <div className="history-content">
                <div className="history-title-row">
                  <h2>{meta.label}</h2>
                  <time dateTime={notification.timestamp}>
                    {new Date(notification.timestamp).toLocaleString()}
                  </time>
                </div>
                <p>{notification.message}</p>
                {!notification.read_status && (
                  <button
                    className="read-button"
                    onClick={() => handleRead(notification.id)}
                    type="button"
                  >
                    Mark as read
                  </button>
                )}
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}
