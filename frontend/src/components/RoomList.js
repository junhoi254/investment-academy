import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './RoomList.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://investment-academy.onrender.com';

function RoomList() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserInfo();
    fetchRooms();
  }, []);

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserInfo(data);
      }
    } catch (error) {
      console.error('사용자 정보 가져오기 실패:', error);
    }
  };

  const fetchRooms = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/rooms`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setRooms(data);
      }
    } catch (error) {
      console.error('방 목록 가져오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoomClick = (roomId) => {
    navigate(`/chat/${roomId}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const handleBackHome = () => {
    navigate('/');
  };

  // ✅ 관리자 페이지 이동 추가
  const handleAdminPanel = () => {
    navigate('/admin');
  };

  // 무료방과 유료방 분리
  const freeRooms = rooms.filter(room => room.is_free === true);
  const paidRooms = rooms.filter(room => room.is_free === false);

  return (
    <div className="roomlist-container">
      <header className="roomlist-header">
        <div className="header-left">
          <button onClick={handleBackHome} className="btn-back">
            ← 홈으로
          </button>
          <h1>🎓 투자학당</h1>
        </div>
        <div className="header-right">
          {userInfo && (
            <>
              <span className="user-name">
                {userInfo.name || userInfo.phone} 님
                {userInfo.role === 'admin' && ' (관리자)'}
                {userInfo.role === 'staff' && ' (서브관리자)'}
              </span>
              {/* ✅ 관리자 페이지 버튼 추가 */}
              {userInfo.role === 'admin' && (
                <button onClick={handleAdminPanel} className="btn-admin">
                  ⚙️ 관리자 페이지
                </button>
              )}
            </>
          )}
          <button onClick={handleLogout} className="btn-logout">
            로그아웃
          </button>
        </div>
      </header>

      <main className="roomlist-main">
        {loading ? (
          <div className="loading">로딩 중...</div>
        ) : (
          <>
            {/* 무료 리딩방 섹션 */}
            {freeRooms.length > 0 && (
              <section className="rooms-section">
                <h2>📢 무료 리딩방</h2>
                <div className="rooms-grid">
                  {freeRooms.map((room) => (
                    <div 
                      key={room.id} 
                      className="room-card free"
                      onClick={() => handleRoomClick(room.id)}
                    >
                      <div className="room-badge">무료</div>
                      <h3>{room.name}</h3>
                      <p className="room-description">
                        {room.description || '실시간 트레이딩 정보'}
                      </p>
                      <div className="room-footer">
                        <span className="online-status">
                          ● {room.online_count || 0}명 접속 중
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* 유료 리딩방 섹션 */}
            <section className="rooms-section">
              <h2>💎 프리미엄 리딩방</h2>
              {paidRooms.length === 0 ? (
                <div className="no-rooms">
                  <p>가입 가능한 프리미엄 리딩방이 없습니다</p>
                </div>
              ) : (
                <div className="rooms-grid">
                  {paidRooms.map((room) => (
                    <div 
                      key={room.id} 
                      className="room-card paid"
                      onClick={() => handleRoomClick(room.id)}
                    >
                      <div className="room-badge premium">프리미엄</div>
                      <h3>{room.name}</h3>
                      <p className="room-description">
                        {room.description || '심화 트레이딩 전략'}
                      </p>
                      <div className="room-footer">
                        <span className="price">
                          {room.price ? `₩${room.price.toLocaleString()}` : '구독형'}
                        </span>
                        <span className="online-status">
                          ● {room.online_count || 0}명 접속 중
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default RoomList;