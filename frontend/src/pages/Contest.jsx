import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { contests } from "../api";
import { useAuth } from "../context/AuthContext";

function contestStatus(c) {
  const now = new Date();
  if (now < new Date(c.start_time)) return "upcoming";
  if (now > new Date(c.end_time)) return "finished";
  return "running";
}

export default function Contest() {
  const { id } = useParams();
  const { user } = useAuth();
  const [contest, setContest] = useState(null);
  const [standings, setStandings] = useState([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    contests.get(id).then(setContest);
    contests.standings(id).then(setStandings).catch(() => {});
  }, [id]);

  const register = async () => {
    setMsg("");
    try {
      await contests.register(id);
      setMsg("Registered successfully!");
    } catch (err) {
      setMsg(err.message);
    }
  };

  if (!contest) return <div className="loading">Loading...</div>;

  const status = contestStatus(contest);
  const start = new Date(contest.start_time);
  const end = new Date(contest.end_time);
  const hours = Math.round((end - start) / 3600000);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>{contest.title}</h2>
          {contest.description && <p style={{ color: "#8b949e", marginTop: "0.25rem" }}>{contest.description}</p>}
        </div>
        <span className={`status status-${status}`}>{status}</span>
      </div>

      <div className="contest-info">
        <div className="contest-info-item">
          <div className="label">Scoring</div>
          <div className="value">{contest.scoring_type.toUpperCase()}</div>
        </div>
        <div className="contest-info-item">
          <div className="label">Start</div>
          <div className="value">{start.toLocaleString()}</div>
        </div>
        <div className="contest-info-item">
          <div className="label">Duration</div>
          <div className="value">{hours} hours</div>
        </div>
        <div className="contest-info-item">
          <div className="label">Participants</div>
          <div className="value">{standings.length}</div>
        </div>
      </div>

      {user && (
        <div style={{ marginBottom: "2rem" }}>
          <button className="btn" onClick={register}>Register for Contest</button>
          {msg && <span style={{ marginLeft: "1rem", color: msg.includes("success") ? "#3fb950" : "#f85149" }}>{msg}</span>}
        </div>
      )}

      <div className="section-header">
        <h3>Problems</h3>
      </div>
      {contest.contest_problems.length === 0 ? (
        <div className="empty"><p>No problems added yet</p></div>
      ) : (
        <table>
          <thead>
            <tr>
              <th style={{ width: 80 }}>Label</th>
              <th>Problem</th>
            </tr>
          </thead>
          <tbody>
            {contest.contest_problems.map((cp) => (
              <tr key={cp.id}>
                <td><strong style={{ color: "#f0f6fc" }}>{cp.label}</strong></td>
                <td><Link to={`/problems/${cp.problem_id}`}>Problem #{cp.problem_id}</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="section-header">
        <h3>Standings</h3>
      </div>
      {standings.length === 0 ? (
        <div className="empty"><p>No participants yet</p></div>
      ) : (
        <table>
          <thead>
            <tr>
              <th style={{ width: 60 }}>Rank</th>
              <th>User</th>
              <th style={{ width: 100 }}>Score</th>
              <th style={{ width: 100 }}>Penalty</th>
            </tr>
          </thead>
          <tbody>
            {standings.map((s, i) => (
              <tr key={s.user_id}>
                <td style={{ fontWeight: 600, color: i < 3 ? "#d29922" : "#8b949e" }}>{s.rank}</td>
                <td style={{ fontWeight: 500 }}>{s.username}</td>
                <td style={{ color: "#3fb950", fontWeight: 600 }}>{s.score}</td>
                <td style={{ color: "#8b949e" }}>{s.penalty}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
