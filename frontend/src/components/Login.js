import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://investment-academy.onrender.com';

function Login() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Backend API는 /api/token을 사용합니다
      // FormData 형식으로 전송 (OAuth2 표준)
      const formData = new URLSearchParams();
      formData.append('username', phone);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/api/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // 토큰 저장
        localStorage.setItem('token', data.access_token);
        
        // 유료방 목록 페이지로 이동
        navigate('/rooms');
      } else {
        const data = await response.json();
        setError(data.detail || '로그인에 실패했습니다');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('서버 연결에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleBackHome = () => {
    navigate('/');
  };

  return (
    <div className="login-container">
      <button onClick={handleBackHome} className="back-btn">
        ← 뒤로
      </button>
      
      <div className="login-card">
        <div className="login-avatar">
          <img 
            src="https://via.placeholder.com/100" 
            alt="Logo" 
          />
        </div>
        
        <h1 className="login-title">투자학당 로그인</h1>
        <p className="login-subtitle">일타쌍장님의 트레이딩 리딩방</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>전화번호</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="010-0000-0000"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="login-footer">
          <p>계정이 없으신가요? <a href="/signup">회원가입</a></p>
        </div>
      </div>
    </div>
  );
}

export default Login;
