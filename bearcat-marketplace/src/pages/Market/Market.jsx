import { useEffect, useMemo, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import ItemCard from "../../components/itemcard/ItemCard.jsx";
import styles from "./Market.module.css";
import ListingForm from "../../components/listingform/ListingForm.jsx";

const CATEGORIES = [
  { label: "All", value: "" },
  { label: "Books", value: "book" },
  { label: "Furniture", value: "furniture" },
  { label: "Misc", value: "misc" },
];

const CONDITIONS = [
  { label: "Any Condition", value: "" },
  { label: "New",           value: "New" },
  { label: "Like New",      value: "Like New" },
  { label: "Good",          value: "Good" },
  { label: "Fair",          value: "Fair" },
];

const SORT_OPTIONS = [
  { label: "Most Relevant", value: "relevance" },
  { label: "Newest First", value: "newest" },
  { label: "Price: Low to High", value: "price_asc" },
  { label: "Price: High to Low", value: "price_desc" },
];

const EMPTY_FORM = {
  type: "misc",
  title: "",
  description: "",
  price_cents: "",
  item_condition: "",
  isbn: "",
  measurements: "",
};

function CreateListingModal({ onClose, onCreated }) {
  async function handleCreate(payload, imageFile) {
    const token = localStorage.getItem("access_token");

    const res = await fetch("http://localhost:8000/listings/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to create listing");
    }

    let created = await res.json();

    if (imageFile) {
      const formData = new FormData();
      formData.append("image", imageFile);

      const uploadRes = await fetch(`http://localhost:8000/listings/${created.id}/image`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });

      if (!uploadRes.ok) {
        const data = await uploadRes.json();
        throw new Error(data.detail || "Failed to upload image");
      }

      created = await uploadRes.json();
    }

    onCreated(created);
    onClose();
  }
}

  
function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm0-2a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11Z"
        fill="currentColor"
      />
      <path
        d="m16.85 16.15 3.5 3.5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function Market() {
  const [items, setItems] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  // Price inputs are LOCAL state (not URL params) while the user is typing.
  // We only push them to the URL when they hit "Apply" or press Enter.
  // This avoids firing a new search on every keystroke.
  const [minInput, setMinInput] = useState("");
  const [maxInput, setMaxInput] = useState("");
  
  // Read current filter values from the URL
  const q         = searchParams.get("q")         || "";
  const type      = searchParams.get("type")       || "";
  const condition = searchParams.get("condition")  || "";
  const minPrice  = searchParams.get("min_price")  || "";
  const maxPrice  = searchParams.get("max_price")  || "";
  const sort      = searchParams.get("sort")       || "relevance";

  const [qInput, setQInput] = useState(q); // initialize from URL

  // Keep qInput in sync if URL changes externally (e.g. navigating back)
  useEffect(() => {
    setQInput(q);
  }, [q]);

  // Submit handler
  function handleSearch(e) {
    e.preventDefault();
    setParam("q", qInput.trim());
  }

   // ── Helper: update one param without wiping the others ──────────────────
  function setParam(key, value) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) next.set(key, value);
      else next.delete(key);
      return next;
    });
  }

   // ── Fetch from backend whenever URL params change ────────────────────────
  const fetchListings = useCallback(async () => {
    setLoading(true);
    try {
      // Build query string from current URL params
      const params = new URLSearchParams();
      if (q)         params.set("query", q);
      if (type)      params.set("type", type);
      if (condition) params.set("condition", condition);
      if (minPrice)  params.set("min_price", Math.round(parseFloat(minPrice) * 100)); // dollars → cents
      if (maxPrice)  params.set("max_price", Math.round(parseFloat(maxPrice) * 100));
      if (sort)      params.set("sort", sort);

      const res = await fetch(`http://localhost:8000/search/?${params}`);
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      setItems(data.results ?? []);
    } catch (err) {
      console.error(err);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [q, type, condition, minPrice, maxPrice, sort]);

  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  // Sync price URL params → local input state when URL changes externally
  useEffect(() => {
    setMinInput(minPrice);
    setMaxInput(maxPrice);
  }, [minPrice, maxPrice]);

  // Fetch favorites separately (unchanged logic)
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    fetch("http://localhost:8000/favorites/me/ids", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : [])
      .then(setFavoriteIds)
      .catch(() => {});
  }, []);

  function applyPriceFilter() {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (minInput) next.set("min_price", minInput);
      else next.delete("min_price");
      if (maxInput) next.set("max_price", maxInput);
      else next.delete("max_price");
      return next;
    });
  }

  function clearAllFilters() {
    setSearchParams({ q }); // keep the text query, clear everything else
    setMinInput("");
    setMaxInput("");
    setQInput("");
  }

  const hasActiveFilters = type || condition || minPrice || maxPrice || q;

  function handleCreated(newListing) {
    setItems((prev) => [newListing, ...prev]);
  }

  async function handleToggleFavorite(listingId, isFavorited) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("Please log in to favorite listings.");
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/favorites/${listingId}`, {
        method: isFavorited ? "DELETE" : "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to update favorites");
      }

      setFavoriteIds((prev) =>
        isFavorited
          ? prev.filter((id) => id !== listingId)
          : [...prev, listingId]
      );
    } catch (error) {
      console.error("Error updating favorite:", error);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.layout}>

        {/* ── LEFT: Filter Sidebar ── */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h2 className={styles.sidebarTitle}>Filters</h2>
            {hasActiveFilters && (
              <button className={styles.clearBtn} onClick={clearAllFilters}>
                Clear all
              </button>
            )}
          </div>

          {/* Category */}
          <div className={styles.filterGroup}>
            <h3 className={styles.filterLabel}>Category</h3>
            {CATEGORIES.map((c) => (
              <label key={c.value} className={styles.radioLabel}>
                <input
                  type="radio"
                  name="type"
                  value={c.value}
                  checked={type === c.value}
                  onChange={() => setParam("type", c.value)}
                />
                {c.label}
              </label>
            ))}
          </div>

          {/* Condition */}
          <div className={styles.filterGroup}>
            <h3 className={styles.filterLabel}>Condition</h3>
            {CONDITIONS.map((c) => (
              <label key={c.value} className={styles.radioLabel}>
                <input
                  type="radio"
                  name="condition"
                  value={c.value}
                  checked={condition === c.value}
                  onChange={() => setParam("condition", c.value)}
                />
                {c.label}
              </label>
            ))}
          </div>

          {/* Price Range */}
          <div className={styles.filterGroup}>
            <h3 className={styles.filterLabel}>Price Range</h3>
            <div className={styles.priceRow}>
              <input
                className={styles.priceInput}
                type="number"
                min="0"
                placeholder="Min $"
                value={minInput}
                onChange={(e) => setMinInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && applyPriceFilter()}
              />
              <span className={styles.priceSep}>–</span>
              <input
                className={styles.priceInput}
                type="number"
                min="0"
                placeholder="Max $"
                value={maxInput}
                onChange={(e) => setMaxInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && applyPriceFilter()}
              />
            </div>
            <button className={styles.applyBtn} onClick={applyPriceFilter}>
              Apply
            </button>
          </div>
        </aside>

        {/* ── RIGHT: Results ── */}
        <div className={styles.results}>
          <form className={styles.searchForm} onSubmit={handleSearch} role="search">
            <span className={styles.searchIcon}>
              <SearchIcon />
            </span>
            <input
              className={styles.searchInput}
              type="search"
              placeholder="Search listings…"
              value={qInput}
              onChange={(e) => setQInput(e.target.value)}
              autoComplete="off"
              aria-label="Search listings"
            />
            <button type="submit" className={styles.searchBtn}>
              Search
            </button>
          </form>

          {/* Sort + result count bar */}
          <div className={styles.resultsBar}>
            <span className={styles.resultCount}>
              {loading ? "Searching…" : `${items.length} listing${items.length !== 1 ? "s" : ""}`}
            </span>
            <select
              className={styles.sortSelect}
              value={sort}
              onChange={(e) => setParam("sort", e.target.value)}
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          {/* Grid */}
          <div className={styles.grid}>
            <div className={styles.addCard} onClick={() => setShowModal(true)}>
              <div className={styles.addIcon}>+</div>
              <p className={styles.addTitle}>Sell Something</p>
              <p className={styles.addSubtitle}>Post your item to the marketplace</p>
            </div>

            {!loading && items.map((item) => (
              <ItemCard
                key={item.id}
                id={item.id}
                title={item.title}
                description={item.description}
                image={item.image_url}
                isFavorited={favoriteIds.includes(item.id)}
                onToggleFavorite={handleToggleFavorite}
              />
            ))}
          </div>
        </div>
      </div>

      {showModal && (
        <CreateListingModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}

export default Market;
