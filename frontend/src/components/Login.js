import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Login({ onLogin }) {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // 전화번호 자동 포맷팅
  const handlePhoneChange = (e) => {
    let value = e.target.value.replace(/[^0-9]/g, '');
    
    if (value.length <= 3) {
      setPhone(value);
    } else if (value.length <= 7) {
      setPhone(`${value.slice(0, 3)}-${value.slice(3)}`);
    } else if (value.length <= 11) {
      setPhone(`${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7, 11)}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', phone);
      formData.append('password', password);

      const response = await axios.post(`${API_URL}/api/token`, formData);
      
      onLogin(response.data.user, response.data.access_token);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || '로그인에 실패했습니다');
      } else {
        setError('서버 연결에 실패했습니다');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-logo">
          <img src="/hunjang-logo.png" alt="일타훈장님" />
        </div>
        <h1>투자학당 로그인</h1>
        <p className="login-subtitle">일타훈장님의 트레이딩 리딩방</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>전화번호</label>
            <input
              type="tel"
              value={phone}
              onChange={handlePhoneChange}
              placeholder="010-0000-0000"
              maxLength="13"
              required
            />
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="register-link">
          <p>계정이 없으신가요? <Link to="/register">회원가입</Link></p>
        </div>
      </div>
    </div>
  );
}

export default Login;
