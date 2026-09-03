import {
  Link,
  NavLink,
  useNavigate,
} from "react-router-dom";

import { markNotificationsRead }
  from "../api/notificationApi";

import "../styles/navbar.css";


export default function Navbar({
  cartCount,
  notifications,
  setNotifications,
}) {

  const navigate =
    useNavigate();


  const token =
    localStorage.getItem(
      "access_token"
    );

  const unreadCount = notifications.filter(
    (notification) => !notification.read_status,
  ).length;

  const handleRead = async (notificationId) => {
    await markNotificationsRead([notificationId]);
    setNotifications((current) => current.map((notification) =>
      notification.id === notificationId
        ? { ...notification, read_status: true }
        : notification,
    ));
  };


  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "token_type"
    );

    navigate("/login");

  };


  return (

    <nav className="navbar">

      <div className="navbar-container">


        <Link
          to="/"
          className="navbar-logo"
        >
          SmartShop
        </Link>


        <div className="navbar-links">


          {token && (

            <>

              <NavLink to="/" end>
                Products
              </NavLink>


              <NavLink to="/cart" className="nav-cart-link">

                <span aria-hidden="true">🛒</span> Cart

                {cartCount > 0 && (

                  <span className="cart-count">
                    {cartCount}
                  </span>

                )}

              </NavLink>

              <NavLink to="/orders">
                Orders
              </NavLink>

              <div className="notification-menu">
                <button className="notification-button" type="button" aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ""}`}>
                  <span aria-hidden="true">✦</span>
                  <span>Notifications</span>
                  {unreadCount > 0 && (
                    <span className="notification-count">{unreadCount}</span>
                  )}
                </button>
                <div className="notification-panel">
                  {notifications.length === 0 && <p>No notifications yet.</p>}
                  {notifications.slice(0, 6).map((notification) => (
                    <button
                      className={`notification-item${notification.read_status ? " is-read" : ""}`}
                      key={notification.id}
                      onClick={() => handleRead(notification.id)}
                      type="button"
                    >
                      <strong>{notification.type.replaceAll("_", " ")}</strong>
                      <span>{notification.message}</span>
                    </button>
                  ))}
                  {notifications.length > 0 && (
                    <Link className="notification-history-link" to="/notifications">
                      View all notifications
                    </Link>
                  )}
                </div>
              </div>


              <button
                onClick={handleLogout}
                className="logout-button"
              >
                Logout
              </button>

            </>

          )}


        </div>

      </div>

    </nav>

  );
}