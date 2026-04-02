import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const loc = useLocation();

  const navLink = (to, label) => (
    <Link
      to={to}
      style={loc.pathname.startsWith(to) ? { color: "#f0f6fc", background: "#21262d" } : {}}
    >
      {label}
    </Link>
  );

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">Battle</Link>
      <div className="nav-links">
        {navLink("/problems", "Problems")}
        {navLink("/contests", "Contests")}
        {user ? (
          <>
            {navLink("/submissions", "Submissions")}
            {navLink("/admin/problems", "Admin")}
            <span className="nav-user">{user.username}</span>
            <button onClick={logout} className="btn-sm">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn-sm" style={{ marginLeft: "0.5rem" }}>Login</Link>
            <Link to="/register" className="btn btn-sm" style={{ background: "#238636", color: "#fff", border: "1px solid #238636" }}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
