import { useEffect, useState } from "react";

import {
  getProducts,
  getProductCategories,
} from "../api/productApi";

import {
  addToCart
} from "../api/cartApi";

import ProductCard from "../components/ProductCard";
import RecommendationSection from "../components/RecommendationSection";
import {
  getRecommendations,
  getTrendingProducts,
} from "../api/productApi";

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

  const [categories, setCategories] =
    useState([]);

  const [recommendations, setRecommendations] = useState([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(true);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [trendingLoading, setTrendingLoading] = useState(true);

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

  useEffect(() => {
    getProductCategories()
      .then(setCategories)
      .catch(() => setCategories([]));

    const userId = localStorage.getItem("user_id");
    const loadRecommendations = userId
      ? getRecommendations(userId)
      : getTrendingProducts();

    loadRecommendations
      .then(setRecommendations)
      .catch(() => setRecommendations([]))
      .finally(() => setRecommendationsLoading(false));

    getTrendingProducts()
      .then(setTrendingProducts)
      .catch(() => setTrendingProducts([]))
      .finally(() => setTrendingLoading(false));
  }, []);


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

  const featuredCollections = [
    { label: "Curated picks", value: "42" },
    { label: "New arrivals", value: "12" },
    { label: "Free delivery", value: "Today" },
  ];

  const categoryHighlights = [
    { title: "Electronics", subtitle: "Modern utility, refined", tone: "dark" },
    { title: "Footwear", subtitle: "Comfort with character", tone: "amber" },
    { title: "Bags", subtitle: "Everyday pieces, elevated", tone: "gold" },
  ];

  const selectCategory = (category) => {
    setFilters((currentFilters) => ({
      ...currentFilters,
      category,
    }));
    document.querySelector(".products-results")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const editorialStories = [
    { title: "Crafted for slower living", text: "Thoughtful objects chosen to make everyday rituals feel more considered and beautifully lived-in." },
    { title: "The quiet luxury edit", text: "A tightly curated collection of elevated essentials designed to feel timeless, polished, and personal." },
    { title: "Designed to be kept", text: "Each piece is selected for longevity, comfort, and a refined finish that makes an impression without excess." },
  ];

  const brandPromises = [
    { value: "24/7", label: "concierge support" },
    { value: "Free", label: "shipping over ₹1999" },
    { value: "7-day", label: "easy returns" },
  ];

  return (
    <div className="products-page">

      <div className="products-container">

        <div className="products-hero">
          <div className="hero-copy">
            <span className="hero-badge">Luxury essentials</span>
            <h1 className="products-title">
              Curated for elevated everyday living.
            </h1>
            <p className="products-subtitle">
              Discover refined essentials, designer picks, and premium finds designed to bring a richer, more elevated lifestyle home.
            </p>
            <div className="hero-actions">
              <button type="button" className="hero-cta primary">
                Shop collection
              </button>
              <button type="button" className="hero-cta secondary">
                Explore offers
              </button>
            </div>
          </div>

          <div className="hero-metrics">
            {featuredCollections.map((item) => (
              <div key={item.label} className="metric-card">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="featured-strip">
          <div className="featured-item active">
            <span className="featured-tag">Featured</span>
            <h3>Signature Collection</h3>
            <p>Elegant everyday essentials with premium finish.</p>
          </div>
          <div className="featured-item">
            <span className="featured-tag">Best seller</span>
            <h3>Designer Luxe</h3>
            <p>High-demand pieces curated for modern living.</p>
          </div>
          <div className="featured-item">
            <span className="featured-tag">Exclusive</span>
            <h3>Limited Drop</h3>
            <p>Fresh arrivals in small, curated batches.</p>
          </div>
        </div>

        <div className="category-showcase">
          {categoryHighlights.map((category) => (
            <button
              key={category.title}
              type="button"
              className={`category-card ${category.tone}`}
              onClick={() => selectCategory(category.title)}
              aria-label={`Browse ${category.title}`}
            >
              <div className="category-card-glow" />
              <span>{category.title}</span>
              <strong>{category.subtitle}</strong>
              <em>Browse collection →</em>
            </button>
          ))}
        </div>

        <div className="sale-banner">
          <div>
            <span className="sale-tag">Member exclusive</span>
            <h2>Up to 40% off premium essentials.</h2>
            <p className="sale-instructions">
              <strong>How to apply:</strong> sign in, choose a premium product, and add it to your cart. The offer is applied at checkout.
            </p>
          </div>
          <a className="sale-button" href="#products-results">Apply offer</a>
        </div>

        <section className="editorial-grid" aria-label="Brand editorial highlights">
          {editorialStories.map((story) => (
            <article key={story.title} className="editorial-card">
              <span className="editorial-label">Journal</span>
              <h3>{story.title}</h3>
              <p>{story.text}</p>
            </article>
          ))}
        </section>

        <div className="brand-promises">
          {brandPromises.map((item) => (
            <div key={item.label} className="promise-card">
              <strong>{item.value}</strong>
              <span>{item.label}</span>
            </div>
          ))}
        </div>

        <RecommendationSection
          title="Recommended For You"
          eyebrow="Picked around your taste"
          products={recommendations}
          loading={recommendationsLoading}
          onAddToCart={handleAddToCart}
          showViewMore
        />

        <RecommendationSection
          title="Trending"
          eyebrow="Trending now"
          products={trendingProducts}
          loading={trendingLoading}
          onAddToCart={handleAddToCart}
          showViewMore
        />


        <div id="products-results" className="products-layout products-results">


          <ProductFilters
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            categories={categories}
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