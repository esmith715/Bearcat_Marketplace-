import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import styles from "./AdminReports.module.css";

export default function AdminReports() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adminUser, setAdminUser] = useState(null);

  useEffect(() => {
    async function init() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          navigate("/login");
          return;
        }

        // Verify admin status
        const userRes = await fetch("http://localhost:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!userRes.ok) throw new Error("Could not verify session");

        const user = await userRes.json();
        if (user.role !== "admin") {
          navigate("/"); // Non-admins not allowed
          return;
        }
        setAdminUser(user);

        // Fetch reports
        const reportsRes = await fetch("http://localhost:8000/reports/", {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!reportsRes.ok) throw new Error("Failed to load reports");
        const reportsData = await reportsRes.json();
        setReports(reportsData.reports || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [navigate]);

  async function updateReportStatus(report_id, newStatus) {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`http://localhost:8000/reports/${report_id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          status: newStatus,
          reviewed_by: adminUser.id
        })
      });

      if (!res.ok) throw new Error("Failed to update report status");

      if (newStatus === "resolved") {
        setReports(prev => prev.map(r => r.report_id === report_id ? { ...r, report_status: newStatus, listing_status: "inactive" } : r));
      } else {
        setReports(prev => prev.map(r => r.report_id === report_id ? { ...r, report_status: newStatus } : r));
      }

    } catch (err) {
      alert(err.message);
    }
  }

  async function deleteReport(report_id) {
    if (!window.confirm("Are you sure you want to permanently delete this report?")) return;
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`http://localhost:8000/reports/${report_id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to delete report");

      setReports(prev => prev.filter(r => r.report_id !== report_id));
    } catch (err) {
      alert(err.message);
    }
  }

  if (loading) return <div className={styles.container}><p className={styles.loading}>Loading Admin Dashboard...</p></div>;
  if (error) return <div className={styles.container}><p className={styles.error}>{error}</p></div>;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Admin Reports Dashboard</h1>

      {reports.length === 0 ? (
        <div className={styles.emptyState}>
          <h3>No reports found</h3>
          <p>You're all caught up!</p>
        </div>
      ) : (
        <div className={styles.cardList}>
          {reports.map((report) => (
            <div key={report.report_id} className={styles.reportCard}>
              <div className={styles.cardHeader}>
                <h3 className={styles.reportReason}>Reason: "{report.reason}"</h3>
                <span className={`${styles.statusBadge} ${styles[report.report_status]}`}>
                  {report.report_status}
                </span>
              </div>

              <div className={styles.metaInfo}>
                <span>
                  <strong>Target Listing:</strong> <Link to={`/market/${report.listing_id}`} className={styles.listingTitle}>{report.listing_title}</Link>
                </span>
                <span>
                  <strong>Listing Status:</strong> {report.listing_status}
                </span>
                <span>
                  <strong>Reported At:</strong> {new Date(report.report_created_at).toLocaleString()}
                </span>
                <span>
                  <strong>Report ID:</strong> {report.report_id}
                </span>
              </div>

              <div className={styles.actions}>
                {report.report_status === "open" && (
                  <button className={`${styles.actionBtn} ${styles.reviewBtn}`} onClick={() => updateReportStatus(report.report_id, "reviewing")}>
                    Mark as Reviewing
                  </button>
                )}

                {report.report_status !== "resolved" && (
                  <button className={`${styles.actionBtn} ${styles.resolveBtn}`} onClick={() => updateReportStatus(report.report_id, "resolved")}>
                    Resolve (Inactivate Listing)
                  </button>
                )}

                {report.report_status !== "dismissed" && (
                  <button className={`${styles.actionBtn} ${styles.dismissBtn}`} onClick={() => updateReportStatus(report.report_id, "dismissed")}>
                    Dismiss
                  </button>
                )}

                <button className={`${styles.actionBtn} ${styles.deleteBtn}`} onClick={() => deleteReport(report.report_id)}>
                  Delete Report
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
