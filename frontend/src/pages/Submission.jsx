import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { submissions } from "../api";

function verdictClass(v) {
  if (v === "accepted") return "verdict verdict-ac";
  if (v === "pending") return "verdict verdict-pending";
  return "verdict verdict-fail";
}

export default function Submission() {
  const { id } = useParams();
  const [sub, setSub] = useState(null);

  useEffect(() => {
    submissions.get(id).then(setSub);
  }, [id]);

  if (!sub) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Submission #{sub.id}</h2>
        <Link to="/submissions" className="btn btn-secondary">Back</Link>
      </div>

      <div className="sub-detail">
        <div className="sub-detail-item">
          <div className="label">Problem</div>
          <div className="value"><Link to={`/problems/${sub.problem_id}`}>#{sub.problem_id}</Link></div>
        </div>
        <div className="sub-detail-item">
          <div className="label">Language</div>
          <div className="value">{sub.language}</div>
        </div>
        <div className="sub-detail-item">
          <div className="label">Verdict</div>
          <div className="value"><span className={verdictClass(sub.verdict)}>{sub.verdict.replace(/_/g, " ").toUpperCase()}</span></div>
        </div>
        <div className="sub-detail-item">
          <div className="label">Time</div>
          <div className="value">{sub.time_used != null ? `${Math.round(sub.time_used)} ms` : "-"}</div>
        </div>
        <div className="sub-detail-item">
          <div className="label">Memory</div>
          <div className="value">{sub.memory_used != null ? `${sub.memory_used} KB` : "-"}</div>
        </div>
        <div className="sub-detail-item">
          <div className="label">Submitted</div>
          <div className="value" style={{ fontSize: "0.9rem" }}>{new Date(sub.created_at).toLocaleString()}</div>
        </div>
      </div>

      <h3 style={{ marginBottom: "0.75rem" }}>Source Code</h3>
      <pre className="code-block">{sub.source_code}</pre>
    </div>
  );
}
