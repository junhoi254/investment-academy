import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ChatRoom.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://investment-academy.onrender.com';
const WS_URL = process.env.REACT_APP_WS_URL || 'wss://investment-academy.onrender.com';

function ChatRoom() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [roomInfo, setRoomInfo] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchRoomInfo();
    if (token) {
      fetchUserInfo();
    }
    fetchMessages();
    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [roomId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchRoomInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/api/rooms/${roomId}`);
      if (response.ok) {
        const data = await response.json();
        setRoomInfo(data);
      }
    } catch (error) {
      console.error('방 정보 가져오기 실패:', error);
    }
  };

  const fetchUserInfo = async () => {
    try {
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

  const fetchMessages = async () => {
    try {
      const response = await fetch(`${API_URL}/api/messages/${roomId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('메시지 가져오기 실패:', error);
    }
  };

  const connectWebSocket = () => {
    try {
      const wsUrl = `${WS_URL}/ws/${roomId}${token ? `?token=${token}` : ''}`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('WebSocket 연결됨');
        setIsConnected(true);
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // 시스템 메시지가 아닌 경우에만 메시지 목록에 추가
        if (data.type !== 'system') {
          setMessages(prev => [...prev, data]);
        }
      };

      websocket.onclose = () => {
        console.log('WebSocket 연결 종료');
        setIsConnected(false);
        // 5초 후 재연결 시도
        setTimeout(() => connectWebSocket(), 5000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket 에러:', error);
      };

      setWs(websocket);
    } catch (error) {
      console.error('WebSocket 연결 실패:', error);
    }
  };

  const canSendMessage = () => {
    // 로그인하지 않은 경우
    if (!token || !userInfo) {
      return false;
    }

    // 무료방인 경우 관리자만 전송 가능
    if (roomInfo?.is_free) {
      return userInfo.role === 'admin' || userInfo.role === 'sub_admin';
    }

    // 유료방은 로그인한 사용자 모두 전송 가능
    return true;
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) {
      return;
    }

    if (!canSendMessage()) {
      if (!token) {
        alert('메시지를 보내려면 로그인이 필요합니다');
        navigate('/login');
      } else {
        alert('관리자와 서브관리자만 메시지를 보낼 수 있습니다');
      }
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          room_id: parseInt(roomId),
          content: newMessage,
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
      } else {
        const error = await response.json();
        alert(error.detail || '메시지 전송 실패');
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      alert('메시지 전송에 실패했습니다');
    }
  };

  const handleBack = () => {
    if (token) {
      navigate('/rooms');
    } else {
      navigate('/');
    }
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const getMessagePlaceholder = () => {
    if (!token) {
      return '로그인 후 메시지를 보낼 수 있습니다';
    }
    if (roomInfo?.is_free && !canSendMessage()) {
      return '관리자와 서브관리자만 메시지를 보낼 수 있습니다';
    }
    return '메시지를 입력하세요...';
  };

  return (
    <div className="chatroom-container">
      <header className="chatroom-header">
        <button onClick={handleBack} className="btn-back">
          ← 뒤로
        </button>
        <div className="room-title">
          <h2>{roomInfo?.name || '채팅방'}</h2>
          {roomInfo?.is_free && <span className="free-badge">무료</span>}
          <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● 연결됨' : '○ 연결 중...'}
          </span>
        </div>
        {!token && (
          <button onClick={handleLogin} className="btn-login-small">
            로그인
          </button>
        )}
      </header>

      <main className="chatroom-main">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="no-messages">
              <p>아직 메시지가 없습니다</p>
              {roomInfo?.is_free && (
                <p className="info-text">관리자의 트레이딩 신호를 기다려주세요</p>
              )}
            </div>
          ) : (
            messages.map((msg, index) => (
              <div 
                key={msg.id || index} 
                className={`message ${msg.user_id === userInfo?.id ? 'mine' : 'theirs'}`}
              >
                <div className="message-header">
                  <span className="message-author">
                    {msg.user_name || '익명'}
                    {msg.user_role === 'admin' && <span className="admin-badge">관리자</span>}
                  </span>
                  <span className="message-time">
                    {new Date(msg.created_at).toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                <div className="message-content">
                  {msg.content}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="chatroom-footer">
        <form onSubmit={handleSendMessage} className="message-form">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={getMessagePlaceholder()}
            disabled={!canSendMessage()}
            className="message-input"
          />
          <button 
            type="submit" 
            className="btn-send"
            disabled={!canSendMessage() || !newMessage.trim()}
          >
            전송
          </button>
        </form>
        {!token && (
          <div className="login-prompt">
            메시지를 보내려면 <button onClick={handleLogin} className="link-btn">로그인</button>이 필요합니다
          </div>
        )}
        {token && roomInfo?.is_free && !canSendMessage() && (
          <div className="admin-only-notice">
            이 방은 관리자만 메시지를 작성할 수 있습니다
          </div>
        )}
      </footer>
    </div>
  );
}

export default ChatRoom;