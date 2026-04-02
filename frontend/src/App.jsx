import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Problems from "./pages/Problems";
import Problem from "./pages/Problem";
import Submissions from "./pages/Submissions";
import Submission from "./pages/Submission";
import Contests from "./pages/Contests";
import Contest from "./pages/Contest";
import AdminProblems from "./pages/AdminProblems";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <main className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/problems" element={<Problems />} />
            <Route path="/problems/:id" element={<Problem />} />
            <Route path="/submissions" element={<Submissions />} />
            <Route path="/submissions/:id" element={<Submission />} />
            <Route path="/contests" element={<Contests />} />
            <Route path="/contests/:id" element={<Contest />} />
            <Route path="/admin/problems" element={<AdminProblems />} />
          </Routes>
        </main>
      </AuthProvider>
    </BrowserRouter>
  );
}
