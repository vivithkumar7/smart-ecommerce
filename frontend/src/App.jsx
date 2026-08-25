import {
  BrowserRouter,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";

import {
  useEffect,
  useState,
} from "react";

import Navbar
  from "./components/Navbar";

import ProtectedRoute
  from "./components/ProtectedRoute";

import Products
  from "./pages/Products";

import Cart
  from "./pages/Cart";

import Checkout
  from "./pages/Checkout";

import Login
  from "./pages/Login";

import Notifications
  from "./pages/Notifications";

import { getCart }
  from "./api/cartApi";

import { getNotifications }
  from "./api/notificationApi";


function AppContent() {

  const location = useLocation();

  const [cartCount, setCartCount] =
    useState(0);

  const [notifications, setNotifications] =
    useState([]);


  const loadCartCount =
    async () => {

      const token =
        localStorage.getItem(
          "access_token"
        );


      if (!token) {

        setCartCount(0);

        return;

      }


      try {

        const cart =
          await getCart();


        const count =
          cart.items.reduce(
            (total, item) =>
              total + item.quantity,
            0
          );


        setCartCount(count);

      } catch (error) {

        console.log(
          "Unable to load cart"
        );

      }
    };


  useEffect(() => {

    loadCartCount();

    const token = localStorage.getItem("access_token");
    if (!token) {
      setNotifications([]);
      return undefined;
    }

    getNotifications()
      .then(setNotifications)
      .catch(() => setNotifications([]));

    const socketUrl = `ws://127.0.0.1:8000/notifications/ws?token=${encodeURIComponent(token)}`;
    const socket = new WebSocket(socketUrl);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "cart_updated") {
        loadCartCount();
      }
      if (data.notification) {
        setNotifications((current) => [
          data.notification,
          ...current.filter((item) => item.id !== data.notification.id),
        ]);
      }
    };

    return () => socket.close();

  }, [location.pathname]);


  return (
    <>
      <Navbar
        cartCount={cartCount}
        notifications={notifications}
        setNotifications={setNotifications}
      />


      <Routes>


        {/* LOGIN */}

        <Route
          path="/login"
          element={<Login />}
        />


        {/* PRODUCTS */}

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Products />
            </ProtectedRoute>
          }
        />


        {/* CART */}

        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <Cart />
            </ProtectedRoute>
          }
        />


        {/* CHECKOUT */}

        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <Checkout />
            </ProtectedRoute>
          }
        />

        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications
                notifications={notifications}
                setNotifications={setNotifications}
              />
            </ProtectedRoute>
          }
        />


      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
