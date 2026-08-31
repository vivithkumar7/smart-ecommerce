import { useEffect, useMemo, useState } from "react";

import { getOrders, requestReturn } from "../api/orderApi";
import "../styles/notifications.css";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value || 0);

const normalizeStatus = (status) => {
  if (!status) return "Pending";
  const key = String(status).trim().toLowerCase();

  if (key === "paid") return "Paid";
  if (key === "pending") return "Pending payment";
  if (key === "shipped") return "Shipped";
  if (key === "delivered") return "Delivered";
  if (key === "cancelled") return "Cancelled";
  if (key.includes("return")) return "Return requested";
  return String(status).trim();
};

const statusTone = (status) => {
  if (!status) return "neutral";
  const key = status.toLowerCase();
  if (key === "shipped") return "shipped";
  if (key === "delivered" || key === "paid") return "success";
  if (key.includes("return")) return "warning";
  if (key === "cancelled") return "danger";
  if (key === "pending") return "pending";
  return "neutral";
};

const shipmentLabel = (order) => {
  if (!order) return "Awaiting shipment";
  const key = String(order.order_status || "").trim().toLowerCase();
  if (key === "shipped") return "Shipment in progress";
  if (key === "delivered") return "Delivered";
  if (key === "paid") return "Preparing shipment";
  if (key === "pending") return "Awaiting payment";
  if (key.includes("return")) return "Return review";
  return "Awaiting shipment";
};

const getStatusIcon = (status) => {
  if (!status) return "⏳";
  const key = String(status).trim().toLowerCase();
  if (key === "paid") return "💳";
  if (key === "pending") return "⏳";
  if (key === "shipped") return "🚚";
  if (key === "delivered") return "✓";
  if (key === "cancelled") return "✕";
  if (key.includes("return")) return "↩";
  return "📦";
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(null);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const data = await getOrders();
      setOrders(data);
    } catch (error) {
      console.error(error);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const canRequestReturn = (order) => {
    if (!order) return false;
    const statusLower = String(order.order_status || "").trim().toLowerCase();
    if (statusLower !== "delivered") return false;
    
    const createdAt = new Date(order.created_at);
    const cutoff = new Date(createdAt);
    cutoff.setDate(cutoff.getDate() + 7);
    return new Date() <= cutoff;
  };

  const getReturnEligibilityMessage = (order) => {
    if (!order) return "Only delivered orders are eligible.";

    const statusLower = String(order.order_status || "").trim().toLowerCase();

    if (statusLower === "delivered") {
      const createdAt = new Date(order.created_at);
      const cutoff = new Date(createdAt);
      cutoff.setDate(cutoff.getDate() + 7);
      if (new Date() > cutoff) {
        return "Return window expired. This order is outside the 7-day return period.";
      }
      return "This order is eligible for return within 7 days of delivery.";
    }

    if (statusLower.includes("return")) {
      return "Return request already submitted and under review.";
    }

    return "Only delivered orders are eligible for a return.";
  };

  const orderCountLabel = useMemo(() => `${orders.length} order${orders.length === 1 ? "" : "s"}`, [orders.length]);

  const handleReturnRequest = async (orderId) => {
    try {
      setSubmitting(orderId);
      await requestReturn(orderId, {
        reason: "General return",
      });
      await loadOrders();
      alert("Return request submitted successfully.");
    } catch (error) {
      alert(error.response?.data?.detail || "Unable to submit return request.");
    } finally {
      setSubmitting(null);
    }
  };

  if (loading) {
    return <div className="loading">Loading orders...</div>;
  }

  return (
    <main className="orders-page">
      <div className="orders-header">
        <div>
          <p className="orders-eyebrow">Recent orders</p>
          <h1>My Orders</h1>
          <p>{orderCountLabel}</p>
        </div>
      </div>

      <section className="orders-list" aria-label="My orders">
        {orders.length === 0 && (
          <div className="orders-empty">
            <h2>No orders yet</h2>
            <p>Your purchases will appear here once you place an order.</p>
          </div>
        )}

        {orders.map((order) => {
          const itemCount = order.items?.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0;

          return (
            <article className="order-card" key={order.id}>
              <div className="order-card-top">
                <div>
                  <span className="order-label">Order</span>
                  <h2>#{order.id}</h2>
                </div>
                <span className={`status-pill ${statusTone(order.order_status)}`}>
                  <span className="status-icon">{getStatusIcon(order.order_status)}</span>
                  {normalizeStatus(order.order_status)}
                </span>
              </div>

              <div className="order-card-meta">
                <time dateTime={order.created_at}>
                  {new Date(order.created_at).toLocaleString()}
                </time>
                <strong>{formatCurrency(order.total)}</strong>
              </div>

              <div className="order-card-summary">
                <div className="summary-stat">
                  <span>Items</span>
                  <strong>{itemCount}</strong>
                </div>
                <div className="summary-stat">
                  <span>Payment</span>
                  <strong>{order.payment_method || "Card"}</strong>
                </div>
                <div className="summary-stat">
                  <span>Shipment</span>
                  <strong>{shipmentLabel(order)}</strong>
                </div>
              </div>

              {order.order_status === "shipped" && (
                <div className="tracking-card">
                  <div className="tracking-card-content">
                    <div className="tracking-left">
                      <div className="tracking-label">Shipment Status</div>
                      <div className="tracking-value">In Transit</div>
                      <div className="tracking-subtext">Estimated delivery in 3-5 days</div>
                    </div>
                    <button type="button" className="track-button">Track Shipment</button>
                  </div>
                </div>
              )}

              {order.items?.length > 0 && (
                <div className="order-items">
                  {order.items.map((item) => (
                    <div className="order-item" key={`${order.id}-${item.product_id}`}>
                      <span>{item.product_name}</span>
                      <span>Qty {item.quantity}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="order-card-actions">
                <div className="action-buttons">
                  <button
                    className="return-button"
                    type="button"
                    disabled={!canRequestReturn(order) || submitting === order.id}
                    title={!canRequestReturn(order) ? getReturnEligibilityMessage(order) : "Request a return for this order"}
                    onClick={() => {
                      if (canRequestReturn(order)) {
                        handleReturnRequest(order.id);
                      } else {
                        alert(getReturnEligibilityMessage(order));
                      }
                    }}
                  >
                    {submitting === order.id
                      ? "Submitting..."
                      : !canRequestReturn(order)
                        ? "Only delivered orders are eligible"
                        : "Request Return"}
                  </button>
                  
                  <button
                    className="details-button"
                    type="button"
                    onClick={() => alert(`Order #${order.id} Details:\n\nTotal: ₹${order.total}\nStatus: ${order.order_status}\nCreated: ${new Date(order.created_at).toLocaleString()}\n\nItems: ${order.items?.length || 0}`)}
                  >
                    View Order Details
                  </button>
                </div>

                {!canRequestReturn(order) && order.order_status !== "Return Requested" && order.order_status !== "return requested" && (
                  <span className="info-note">{getReturnEligibilityMessage(order)}</span>
                )}

                {(order.order_status === "Return Requested" || order.order_status === "return requested") && (
                  <span className="success-note">Return requested. We are reviewing it.</span>
                )}
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}
