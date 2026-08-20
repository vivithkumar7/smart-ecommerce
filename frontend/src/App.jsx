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

import { getCart }
  from "./api/cartApi";


function AppContent() {

  const location = useLocation();

  const [cartCount, setCartCount] =
    useState(0);


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

  }, [location.pathname]);


  return (
    <>
      <Navbar
        cartCount={cartCount}
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
