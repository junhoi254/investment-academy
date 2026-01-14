import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://investment-academy.onrender.com';

function Home() {
  const [freeRooms, setFreeRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchFreeRooms();
  }, []);

  const fetchFreeRooms = async () => {
    try {
      const response = await fetch(`${API_URL}/api/rooms?type=free`);
      if (response.ok) {
        const data = await response.json();
        setFreeRooms(data.filter(room => room.is_free === true));
      }
    } catch (error) {
      console.error('무료방 목록 가져오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoomClick = (roomId) => {
    navigate(`/chat/${roomId}`);
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const handleMyRooms = () => {
    navigate('/rooms');
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <div className="header-content">
          <h1>🎓 투자학당</h1>
          <p className="subtitle">일타쌍장님의 트레이딩 리딩방</p>
        </div>
        <div className="header-actions">
          {token ? (
            <button onClick={handleMyRooms} className="btn-primary">
              내 리딩방
            </button>
          ) : (
            <button onClick={handleLogin} className="btn-login">
              로그인
            </button>
          )}
        </div>
      </header>

      <main className="home-main">
        <section className="free-rooms-section">
          <h2>📢 무료 리딩방</h2>
          <p className="section-description">
            누구나 입장하여 트레이딩 정보를 확인할 수 있습니다
          </p>

          {loading ? (
            <div className="loading">로딩 중...</div>
          ) : freeRooms.length === 0 ? (
            <div className="no-rooms">
              <p>현재 운영 중인 무료방이 없습니다</p>
            </div>
          ) : (
            <div className="rooms-grid">
              {freeRooms.map((room) => (
                <div 
                  key={room.id} 
                  className="room-card free"
                  onClick={() => handleRoomClick(room.id)}
                >
                  <div className="room-badge">무료</div>
                  <h3>{room.name}</h3>
                  <p className="room-description">{room.description || '실시간 트레이딩 정보'}</p>
                  <div className="room-footer">
                    <span className="online-status">
                      ● {room.online_count || 0}명 접속 중
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="info-section">
          <div className="info-card">
            <h3>💎 프리미엄 리딩방</h3>
            <p>더 자세한 분석과 실시간 트레이딩 신호를 원하신다면</p>
            {!token && (
              <button onClick={handleLogin} className="btn-secondary">
                로그인하여 확인하기
              </button>
            )}
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <p>© 2026 투자학당. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default Home;
