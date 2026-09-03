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
  const [openOrderId, setOpenOrderId] = useState(null);
  const [returnOrderId, setReturnOrderId] = useState(null);
  const [returnForm, setReturnForm] = useState({ reason: "", condition: "", packaging: "", comment: "" });

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

  const getDeliveryDetails = (order) => {
    const orderDate = new Date(order.created_at);
    const deliveryStart = new Date(orderDate);
    const deliveryEnd = new Date(orderDate);
    deliveryStart.setDate(deliveryStart.getDate() + 3);
    deliveryEnd.setDate(deliveryEnd.getDate() + 5);
    const formatDate = (date) => date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
    const status = String(order.order_status || "").trim().toLowerCase();

    if (status === "shipped") {
      return {
        title: "In transit",
        message: "Your order is on the way.",
        date: `${formatDate(deliveryStart)} - ${formatDate(deliveryEnd)}`,
      };
    }
    if (status === "delivered") {
      return {
        title: "Delivered",
        message: "This order has been delivered.",
        date: `Expected by ${formatDate(deliveryEnd)}`,
      };
    }
    if (status.includes("return") || status === "returned" || status === "refunded") {
      return {
        title: "Delivery complete",
        message: "Shipment timing is no longer active for this order.",
        date: `Original estimate: ${formatDate(deliveryStart)} - ${formatDate(deliveryEnd)}`,
      };
    }
    return {
      title: "Preparing shipment",
      message: "We will notify you when your order ships.",
      date: `${formatDate(deliveryStart)} - ${formatDate(deliveryEnd)}`,
    };
  };

  const orderCountLabel = useMemo(() => `${orders.length} order${orders.length === 1 ? "" : "s"}`, [orders.length]);

  const handleReturnRequest = async (orderId) => {
    if (!returnForm.reason || !returnForm.condition || !returnForm.packaging) {
      alert("Please answer all return questions.");
      return;
    }
    try {
      setSubmitting(orderId);
      await requestReturn(orderId, {
        reason: returnForm.reason,
        comment: `Product condition: ${returnForm.condition}. Original packaging: ${returnForm.packaging}. ${returnForm.comment}`.trim(),
      });
      await loadOrders();
      setReturnOrderId(null);
      setReturnForm({ reason: "", condition: "", packaging: "", comment: "" });
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
          const deliveryDetails = getDeliveryDetails(order);
          const isDetailsOpen = openOrderId === order.id;

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
                        setReturnOrderId(returnOrderId === order.id ? null : order.id);
                      } else {
                        alert(getReturnEligibilityMessage(order));
                      }
                    }}
                  >
                    {submitting === order.id
                      ? "Submitting..."
                      : !canRequestReturn(order)
                        ? "Only delivered orders are eligible"
                        : returnOrderId === order.id ? "Close Return Form" : "Request Return"}
                  </button>
                  
                  <button
                    className="details-button"
                    type="button"
                    aria-expanded={isDetailsOpen}
                    onClick={() => setOpenOrderId(isDetailsOpen ? null : order.id)}
                  >
                    {isDetailsOpen ? "Hide Order Details" : "View Order Details"}
                  </button>
                </div>

                {isDetailsOpen && (
                  <div className="order-details-panel">
                    <div className="details-panel-heading">
                      <div>

                      {returnOrderId === order.id && canRequestReturn(order) && (
                        <div className="return-form-panel">
                          <div>
                            <span className="order-label">Return request</span>
                            <h3>Tell us why you are returning this product</h3>
                            <p>Your answers help us review the return and process the refund.</p>
                          </div>
                          <label>Why are you returning it?
                            <select value={returnForm.reason} onChange={(event) => setReturnForm({ ...returnForm, reason: event.target.value })}>
                              <option value="">Select a reason</option>
                              <option value="Product is damaged">Product is damaged</option>
                              <option value="Wrong product received">Wrong product received</option>
                              <option value="Product does not match description">Product does not match description</option>
                              <option value="Changed my mind">Changed my mind</option>
                            </select>
                          </label>
                          <label>What is the product condition?
                            <select value={returnForm.condition} onChange={(event) => setReturnForm({ ...returnForm, condition: event.target.value })}>
                              <option value="">Select product condition</option>
                              <option value="Unused and unopened">Unused and unopened</option>
                              <option value="Opened but unused">Opened but unused</option>
                              <option value="Used or damaged">Used or damaged</option>
                            </select>
                          </label>
                          <label>Do you have the original packaging?
                            <select value={returnForm.packaging} onChange={(event) => setReturnForm({ ...returnForm, packaging: event.target.value })}>
                              <option value="">Select an answer</option>
                              <option value="Yes">Yes</option>
                              <option value="No">No</option>
                            </select>
                          </label>
                          <label>Additional comments (optional)
                            <textarea rows="3" value={returnForm.comment} onChange={(event) => setReturnForm({ ...returnForm, comment: event.target.value })} placeholder="Add details about the issue" />
                          </label>
                          <button className="submit-return-button" type="button" disabled={submitting === order.id} onClick={() => handleReturnRequest(order.id)}>
                            {submitting === order.id ? "Submitting..." : `Submit Return Request · ${formatCurrency(order.total)} refund`}
                          </button>
                        </div>
                      )}
                        <span className="order-label">Order details</span>
                        <h3>Order #{order.id}</h3>
                      </div>
                      <span className={`details-status ${statusTone(order.order_status)}`}>{normalizeStatus(order.order_status)}</span>
                    </div>
                    <div className="details-grid">
                      <div><span>Order placed</span><strong>{new Date(order.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}</strong></div>
                      <div><span>Delivery time</span><strong>3-5 days after shipping</strong></div>
                      <div><span>Estimated delivery</span><strong>{deliveryDetails.date}</strong></div>
                      <div><span>Payment status</span><strong>{String(order.payment_status || "pending").replaceAll("_", " ")}</strong></div>
                    </div>
                    <div className="delivery-callout">
                      <span className="delivery-callout-icon" aria-hidden="true">🚚</span>
                      <div><strong>{deliveryDetails.title}</strong><p>{deliveryDetails.message}</p></div>
                    </div>
                  </div>
                )}

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
