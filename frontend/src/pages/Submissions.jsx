import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { submissions } from "../api";

function verdictClass(v) {
  if (v === "accepted") return "verdict verdict-ac";
  if (v === "pending") return "verdict verdict-pending";
  return "verdict verdict-fail";
}

function formatVerdict(v) {
  return v.replace(/_/g, " ").toUpperCase();
}

export default function Submissions() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    submissions.mine().then(setList).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading submissions...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>My Submissions</h2>
      </div>
      {list.length === 0 ? (
        <div className="empty">
          <p>No submissions yet</p>
          <Link to="/problems" className="btn btn-secondary">Browse problems</Link>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Problem</th>
              <th>Language</th>
              <th>Verdict</th>
              <th>Time</th>
              <th>Memory</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {list.map((s) => (
              <tr key={s.id}>
                <td><Link to={`/submissions/${s.id}`}>{s.id}</Link></td>
                <td><Link to={`/problems/${s.problem_id}`}>Problem #{s.problem_id}</Link></td>
                <td>{s.language}</td>
                <td><span className={verdictClass(s.verdict)}>{formatVerdict(s.verdict)}</span></td>
                <td>{s.time_used != null ? `${Math.round(s.time_used)} ms` : "-"}</td>
                <td>{s.memory_used != null ? `${s.memory_used} KB` : "-"}</td>
                <td style={{ color: "#8b949e" }}>{new Date(s.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
