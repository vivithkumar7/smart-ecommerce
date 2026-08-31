import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getCart,
  updateCart,
  removeFromCart,
} from "../api/cartApi";

import CartItem from "../components/CartItem";

import CartSummary
  from "../components/CartSummary";

import "../styles/cart.css";


export default function Cart() {

  const [cart, setCart] =
    useState(null);

  const [loading, setLoading] =
    useState(true);


  const loadCart = async () => {

    try {

      setLoading(true);

      const data =
        await getCart();

      setCart(data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    loadCart();

  }, []);


  const handleUpdate = async (
    productId,
    quantity
  ) => {

    try {

      const data =
        await updateCart(
          productId,
          quantity
        );

      setCart(data);

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Unable to update cart."
      );

    }
  };


  const handleRemove = async (
    productId
  ) => {

    try {

      const data =
        await removeFromCart(
          productId
        );

      setCart(data);

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Unable to remove item."
      );

    }
  };


  if (loading) {

    return (
      <div className="loading">
        Loading cart...
      </div>
    );

  }


  if (!cart) {

    return (
      <div className="empty-cart-wrap">
        <div className="empty-cart">
          <span className="empty-cart-badge">Your bag</span>
          <h2>Your cart is empty</h2>
          <p>Browse our curated essentials and add a few premium picks.</p>
          <Link to="/" className="shop-now-button">Shop now</Link>
        </div>
      </div>
    );

  }


  return (
    <div className="cart-page">

      <div className="cart-container">


        <div className="cart-header">

          <h1 className="cart-title">
            Shopping Cart
          </h1>

        </div>


        {cart.items.length === 0 ? (

          <div className="empty-cart-wrap">
            <div className="empty-cart">
              <span className="empty-cart-badge">Your bag</span>
              <h2>Your cart is empty</h2>
              <p>Add some products to continue.</p>
              <Link to="/" className="shop-now-button">Shop now</Link>
            </div>
          </div>

        ) : (

          <div className="cart-layout">


            <div className="cart-items">

              {cart.items.map((item) => (

                <CartItem
                  key={item.product_id}
                  item={item}
                  onUpdate={handleUpdate}
                  onRemove={handleRemove}
                />

              ))}

            </div>


            <CartSummary
              cart={cart}
            />


          </div>

        )}

      </div>

    </div>
  );
}
