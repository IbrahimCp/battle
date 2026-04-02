import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { contests } from "../api";

function contestStatus(c) {
  const now = new Date();
  const start = new Date(c.start_time);
  const end = new Date(c.end_time);
  if (now < start) return "upcoming";
  if (now > end) return "finished";
  return "running";
}

export default function Contests() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contests.list().then(setList).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading contests...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Contests</h2>
      </div>
      {list.length === 0 ? (
        <div className="empty">
          <p>No contests yet</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Contest</th>
              <th>Scoring</th>
              <th>Start</th>
              <th>Duration</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {list.map((c) => {
              const status = contestStatus(c);
              const start = new Date(c.start_time);
              const end = new Date(c.end_time);
              const hours = Math.round((end - start) / 3600000);
              return (
                <tr key={c.id}>
                  <td><Link to={`/contests/${c.id}`}>{c.title}</Link></td>
                  <td>{c.scoring_type.toUpperCase()}</td>
                  <td style={{ color: "#8b949e" }}>{start.toLocaleString()}</td>
                  <td>{hours}h</td>
                  <td><span className={`status status-${status}`}>{status}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
