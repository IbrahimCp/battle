import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="home">
      <h1>Battle</h1>
      <p className="subtitle">Competitive programming platform. Solve problems. Join contests. Climb the ranks.</p>
      <div className="home-links">
        <Link to="/problems" className="btn" style={{ background: "#58a6ff", border: "none" }}>Browse Problems</Link>
        <Link to="/contests" className="btn btn-secondary">View Contests</Link>
        {!user && <Link to="/register" className="btn">Get Started</Link>}
      </div>
    </div>
  );
}
