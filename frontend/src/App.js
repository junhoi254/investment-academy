import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import ChatList from './components/ChatList';
import ChatRoom from './components/ChatRoom';
import AdminPanel from './components/AdminPanel';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 로컬 스토리지에서 토큰 확인
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* 공개 라우트 */}
          <Route 
            path="/login" 
            element={user ? <Navigate to="/chat" /> : <Login onLogin={handleLogin} />} 
          />
          <Route 
            path="/register" 
            element={user ? <Navigate to="/chat" /> : <Register />} 
          />
          
          {/* 보호된 라우트 */}
          <Route 
            path="/chat" 
            element={user ? <ChatList user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/chat/:roomId" 
            element={user ? <ChatRoom user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          
          {/* 관리자 라우트 */}
          <Route 
            path="/admin" 
            element={
              user && user.role === 'admin' 
                ? <AdminPanel user={user} onLogout={handleLogout} /> 
                : <Navigate to="/chat" />
            } 
          />
          
          {/* 기본 라우트 */}
          <Route path="/" element={<Navigate to="/chat" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
