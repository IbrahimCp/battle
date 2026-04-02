import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { auth } from "../api";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await auth.register(form);
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-page">
      <h2>Create account</h2>
      <p className="form-subtitle">Join Battle and start competing</p>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input value={form.username} onChange={set("username")} required />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={form.email} onChange={set("email")} required />
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>First Name</label>
            <input value={form.first_name} onChange={set("first_name")} required />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Last Name</label>
            <input value={form.last_name} onChange={set("last_name")} required />
          </div>
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={form.password} onChange={set("password")} required />
        </div>
        <button type="submit" className="btn" style={{ width: "100%", justifyContent: "center" }}>Create account</button>
      </form>
      <p>Already have an account? <Link to="/login">Sign in</Link></p>
    </div>
  );
}
