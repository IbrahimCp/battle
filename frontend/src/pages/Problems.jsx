import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { problems } from "../api";

export default function Problems() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    problems.list().then(setList).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading problems...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Problems</h2>
      </div>
      {list.length === 0 ? (
        <div className="empty">
          <p>No problems yet</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th style={{ width: 60 }}>#</th>
              <th>Title</th>
              <th style={{ width: 120 }}>Time Limit</th>
              <th style={{ width: 140 }}>Memory Limit</th>
            </tr>
          </thead>
          <tbody>
            {list.map((p) => (
              <tr key={p.id}>
                <td style={{ color: "#8b949e" }}>{p.id}</td>
                <td><Link to={`/problems/${p.id}`}>{p.title}</Link></td>
                <td>{p.time_limit}s</td>
                <td>{p.memory_limit} MB</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
