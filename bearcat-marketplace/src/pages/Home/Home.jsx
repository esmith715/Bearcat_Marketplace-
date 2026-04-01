import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Home.module.css";

const CATEGORIES = [
  { label: "Books", type: "book" },
  { label: "Furniture", type: "furniture" },
  { label: "Misc", type: "misc" },
];

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

function Home() {
  const [query, setQuery] = useState("");
  const [preview, setPreview] = useState([]);
  const [previewLoading, setPreviewLoading] = useState(true);
  const [previewError, setPreviewError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setPreviewLoading(true);
      setPreviewError(false);
      try {
        const res = await fetch("http://localhost:8000/listings/?status=active");
        if (!res.ok) throw new Error("failed");
        const data = await res.json();
        if (!cancelled) setPreview(Array.isArray(data) ? data.slice(0, 8) : []);
      } catch {
        if (!cancelled) {
          setPreviewError(true);
          setPreview([]);
        }
      } finally {
        if (!cancelled) setPreviewLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function handleSearch(e) {
    e.preventDefault();
    const q = query.trim();
    if (q) navigate(`/market?q=${encodeURIComponent(q)}`);
    else navigate("/market");
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-label="Welcome">
        <p className={styles.eyebrow}>University of Cincinnati</p>
        <h1 className={styles.headline}>The campus marketplace.</h1>
        <p className={styles.subhead}>
          Buy and sell from students. Search listings or browse by category.
        </p>

        <form className={styles.searchForm} onSubmit={handleSearch} role="search">
          <span className={styles.searchIcon}>
            <SearchIcon />
          </span>
          <input
            className={styles.searchInput}
            type="search"
            name="q"
            placeholder="Search for anything…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
            enterKeyHint="search"
            aria-label="Search listings"
          />
          <button type="submit" className={styles.searchBtn}>
            Search
          </button>
        </form>

        <div className={styles.chips}>
          {CATEGORIES.map((c) => (
            <Link key={c.type} to={`/market?type=${encodeURIComponent(c.type)}`} className={styles.chip}>
              {c.label}
            </Link>
          ))}
          <Link to="/market" className={styles.chipMuted}>
            Browse all
          </Link>
        </div>
      </section>

      <section className={styles.featured} aria-labelledby="fresh-heading">
        <div className={styles.sectionHeader}>
          <h2 id="fresh-heading" className={styles.sectionTitle}>
            Fresh listings
          </h2>
          <Link to="/market" className={styles.sectionLink}>
            See all
          </Link>
        </div>

        {previewError && (
          <p className={styles.muted}>Listings appear here when the API is available.</p>
        )}
        {!previewError && previewLoading && <p className={styles.muted}>Loading…</p>}
        {!previewError && !previewLoading && preview.length === 0 && (
          <p className={styles.muted}>No listings yet — be the first to sell something.</p>
        )}
        {!previewError && !previewLoading && preview.length > 0 && (
          <div className={styles.tileRow}>
            {preview.map((item) => (
              <Link key={item.id} to={`/market/${item.id}`} className={styles.tile}>
                <div className={styles.tileImageWrap}>
                  {item.image ? (
                    <img src={item.image} alt="" className={styles.tileImage} />
                  ) : (
                    <div className={styles.tilePlaceholder} aria-hidden />
                  )}
                </div>
                <span className={styles.tileTitle}>{item.title}</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Home;
