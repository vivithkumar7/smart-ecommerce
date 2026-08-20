export default function ProductFilters({
  filters,
  setFilters,
  clearFilters,
}) {

  const handleChange = (event) => {

    const {
      name,
      value,
      type,
      checked
    } = event.target;

    setFilters({
      ...filters,

      [name]:
        type === "checkbox"
          ? checked
          : value,
    });
  };


  return (
    <aside className="filter-card">

      <h2 className="filter-title">
        Filters
      </h2>


      <div className="filter-group">

        <label className="filter-label">
          Category
        </label>

        <select
          name="category"
          value={filters.category}
          onChange={handleChange}
          className="filter-select"
        >

          <option value="">
            All Categories
          </option>

          <option value="Electronics">
            Electronics
          </option>

          <option value="Footwear">
            Footwear
          </option>

          <option value="Bags">
            Bags
          </option>

        </select>

      </div>


      <div className="filter-group">

        <label className="filter-label">
          Price Range
        </label>

        <div className="price-row">

          <input
            type="number"
            name="min_price"
            value={filters.min_price}
            onChange={handleChange}
            placeholder="Min"
            className="filter-input"
          />

          <input
            type="number"
            name="max_price"
            value={filters.max_price}
            onChange={handleChange}
            placeholder="Max"
            className="filter-input"
          />

        </div>

      </div>


      <div className="filter-group">

        <label className="filter-label">
          Popularity
        </label>

        <select
          name="min_popularity"
          value={filters.min_popularity}
          onChange={handleChange}
          className="filter-select"
        >

          <option value="">
            Any Rating
          </option>

          <option value="3">
            3+ Stars
          </option>

          <option value="4">
            4+ Stars
          </option>

          <option value="4.5">
            4.5+ Stars
          </option>

        </select>

      </div>


      <div className="filter-group">

        <label className="stock-checkbox">

          <input
            type="checkbox"
            name="in_stock"
            checked={filters.in_stock}
            onChange={handleChange}
          />

          Only show in-stock products

        </label>

      </div>


      <button
        className="clear-filter-button"
        onClick={clearFilters}
      >
        Clear Filters
      </button>

    </aside>
  );
}