import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Register from './pages/Register';
import Login from './pages/Login';
import Projects from './pages/Projects';

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Главная</Link> |{" "}
        <Link to="/register">Регистрация</Link> |{" "}
        <Link to="/login">Вход</Link> |{" "}
        <Link to="/projects">Проекты</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/projects" element={<Projects />} />
      </Routes>
    </Router>
  );
}

export default App;