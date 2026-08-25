import { useEffect, useState } from "react";

import {
  getProducts
} from "../api/productApi";

import {
  addToCart
} from "../api/cartApi";

import ProductCard from "../components/ProductCard";

import ProductFilters
  from "../components/ProductFilters";

import "../styles/products.css";


export default function Products() {

  const [products, setProducts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [filters, setFilters] =
    useState({
      category: "",
      min_price: "",
      max_price: "",
      min_popularity: "",
      in_stock: false,
    });


  const loadProducts = async () => {

    try {

      setLoading(true);
      setError("");

      const data =
        await getProducts(filters);

      setProducts(data);

    } catch (error) {

      console.error(error);

      setError(
        "Unable to load products."
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    loadProducts();

  }, [filters]);


  const handleAddToCart = async (
    productId
  ) => {

    try {

      await addToCart(
        productId,
        1
      );

      alert(
        "Product added to cart!"
      );

      loadProducts();

    } catch (error) {

      if (error.response?.status === 404) {
        await loadProducts();
      }

      alert(
        error.response?.data?.detail ||
        "Unable to add product."
      );

    }
  };


  const clearFilters = () => {

    setFilters({
      category: "",
      min_price: "",
      max_price: "",
      min_popularity: "",
      in_stock: false,
    });

  };


  return (
    <div className="products-page">

      <div className="products-container">


        <div className="products-header">

          <div>

            <h1 className="products-title">
              Product Catalog
            </h1>

            <p className="products-subtitle">
              Browse our products and find
              what you need.
            </p>

          </div>

        </div>


        <div className="products-layout">


          <ProductFilters
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
          />


          <main className="products-area">


            <div className="products-toolbar">

              <span className="product-count">

                {products.length}
                {" "}
                Products

              </span>

            </div>


            {loading && (
              <div className="loading">
                Loading products...
              </div>
            )}


            {error && (
              <div className="error">
                {error}
              </div>
            )}


            {!loading &&
              !error &&
              products.length === 0 && (

                <div className="empty-products">

                  <h2>
                    No products found
                  </h2>

                  <p>
                    Try changing your filters.
                  </p>

                </div>

              )}


            <div className="product-grid">

              {products.map((product) => (

                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={
                    handleAddToCart
                  }
                />

              ))}

            </div>


          </main>

        </div>

      </div>

    </div>
  );
}