import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { problems, submissions as subApi } from "../api";
import { useAuth } from "../context/AuthContext";

const LANGUAGES = [
  { value: "cpp", label: "C++" },
  { value: "python", label: "Python" },
  { value: "java", label: "Java" },
];

export default function Problem() {
  const { id } = useParams();
  const { user } = useAuth();
  const [problem, setProblem] = useState(null);
  const [tab, setTab] = useState("statement");
  const [lang, setLang] = useState("cpp");
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    problems.get(id).then(setProblem);
  }, [id]);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    setResult(null);
    try {
      const sub = await subApi.create({
        problem_id: Number(id),
        language: lang,
        source_code: code,
      });
      setResult(sub);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (!problem) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="problem-header">
        <h2>{problem.title}</h2>
        <div className="problem-badges">
          <span className="badge">Time: <span className="badge-label">{problem.time_limit}s</span></span>
          <span className="badge">Memory: <span className="badge-label">{problem.memory_limit} MB</span></span>
          <span className="badge">Checker: <span className="badge-label">{problem.checker_type}</span></span>
        </div>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === "statement" ? "active" : ""}`} onClick={() => setTab("statement")}>Statement</button>
        {user && <button className={`tab ${tab === "submit" ? "active" : ""}`} onClick={() => setTab("submit")}>Submit</button>}
      </div>

      {tab === "statement" && (
        <div className="statement">{problem.statement}</div>
      )}

      {tab === "submit" && user && (
        <div className="submit-section">
          <h3>Submit Solution</h3>
          {error && <div className="error">{error}</div>}
          {result && (
            <div className="success">
              Submitted! ID: <Link to={`/submissions/${result.id}`}>#{result.id}</Link> — Verdict: <strong>{result.verdict.replace("_", " ")}</strong>
            </div>
          )}
          <form onSubmit={submit}>
            <div className="submit-row">
              <div className="form-group" style={{ flex: "0 0 180px" }}>
                <label>Language</label>
                <select value={lang} onChange={(e) => setLang(e.target.value)}>
                  {LANGUAGES.map((l) => (
                    <option key={l.value} value={l.value}>{l.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Source Code</label>
              <textarea
                placeholder="Paste your code here..."
                value={code}
                onChange={(e) => setCode(e.target.value)}
                rows={18}
                required
              />
            </div>
            <button type="submit" className="btn" disabled={submitting}>
              {submitting ? "Submitting..." : "Submit Solution"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
