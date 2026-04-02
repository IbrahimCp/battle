import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { problems } from "../api";
import { useAuth } from "../context/AuthContext";

export default function AdminProblems() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [error, setError] = useState("");
  const { user } = useAuth();
  const navigate = useNavigate();
  const fileRef = useRef();

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    loadProblems();
  }, [user, navigate]);

  const loadProblems = () => {
    problems.list(0, 200).then(setList).finally(() => setLoading(false));
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await problems.upload(file);
      loadProblems();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (id, title) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    setDeleting(id);
    try {
      await problems.delete(id);
      setList((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(null);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Manage Problems</h2>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button
            className="btn"
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "Importing..." : "+ Import Polygon Package"}
          </button>
          <input
            type="file"
            accept=".zip"
            ref={fileRef}
            onChange={handleUpload}
            style={{ display: "none" }}
          />
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {list.length === 0 ? (
        <div className="empty">
          <p>No problems yet</p>
          <p>Import a Polygon package (.zip) to get started</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th style={{ width: 60 }}>#</th>
              <th>Title</th>
              <th style={{ width: 100 }}>Time</th>
              <th style={{ width: 100 }}>Memory</th>
              <th style={{ width: 100 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {list.map((p) => (
              <tr key={p.id}>
                <td style={{ color: "#8b949e" }}>{p.id}</td>
                <td><Link to={`/problems/${p.id}`}>{p.title}</Link></td>
                <td>{p.time_limit}s</td>
                <td>{p.memory_limit} MB</td>
                <td>
                  <button
                    className="btn-sm btn-danger"
                    onClick={() => handleDelete(p.id, p.title)}
                    disabled={deleting === p.id}
                  >
                    {deleting === p.id ? "..." : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
