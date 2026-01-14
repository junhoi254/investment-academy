import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Register.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    phone: '',
    password: '',
    confirmPassword: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // 전화번호 자동 포맷팅
  const handlePhoneChange = (e) => {
    let value = e.target.value.replace(/[^0-9]/g, '');
    
    if (value.length <= 3) {
      setFormData({ ...formData, phone: value });
    } else if (value.length <= 7) {
      setFormData({ ...formData, phone: `${value.slice(0, 3)}-${value.slice(3)}` });
    } else if (value.length <= 11) {
      setFormData({ ...formData, phone: `${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7, 11)}` });
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다');
      return;
    }

    if (formData.password.length < 4) {
      setError('비밀번호는 최소 4자 이상이어야 합니다');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_URL}/api/register`, {
        phone: formData.phone,
        password: formData.password,
        name: formData.name
      });

      setSuccess(true);
      
      // 3초 후 로그인 페이지로 이동
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || '회원가입에 실패했습니다');
      } else {
        setError('서버 연결에 실패했습니다');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="register-container">
        <div className="register-box success-box">
          <div className="register-logo">
            <img src="/hunjang-logo.png" alt="일타훈장님" />
          </div>
          <h1>✅ 회원가입 완료</h1>
          <p>관리자 승인 후 이용하실 수 있습니다.</p>
          <p>잠시 후 로그인 페이지로 이동합니다...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-box">
        <div className="register-logo">
          <img src="/hunjang-logo.png" alt="일타훈장님" />
        </div>
        <h1>회원가입</h1>
        <p className="register-subtitle">투자학당에 오신 것을 환영합니다</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>이름</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="이름을 입력하세요"
              required
            />
          </div>

          <div className="form-group">
            <label>전화번호</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={handlePhoneChange}
              placeholder="010-0000-0000"
              maxLength="13"
              required
            />
            <small>아이디로 사용됩니다 (자동으로 - 추가)</small>
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="비밀번호 (최소 4자)"
              required
            />
          </div>

          <div className="form-group">
            <label>비밀번호 확인</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="비밀번호 확인"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? '가입 중...' : '회원가입'}
          </button>
        </form>

        <div className="login-link">
          <p>이미 계정이 있으신가요? <Link to="/login">로그인</Link></p>
        </div>
      </div>
    </div>
  );
}

export default Register;
