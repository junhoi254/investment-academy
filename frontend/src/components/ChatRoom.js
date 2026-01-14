import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ChatRoom.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

// 이모티콘 목록
const EMOJIS = [
  '😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊',
  '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '☺️', '🙂',
  '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣',
  '😥', '😮', '🤐', '😯', '😪', '😫', '😴', '😌', '😛', '😜',
  '😝', '🤤', '😒', '😓', '😔', '😕', '🙃', '🤑', '😲', '☹️',
  '🙁', '😖', '😞', '😟', '😤', '😢', '😭', '😦', '😧', '😨',
  '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉',
  '👆', '👇', '☝️', '✋', '🤚', '🖐', '🖖', '👋', '🤝', '🙏',
  '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '❤️',
  '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️',
  '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️',
  '🔥', '💯', '💢', '💥', '💫', '💦', '💨', '🕳️', '💬', '👁️',
  '🗨️', '🗯️', '💭', '💤', '👋', '🎉', '🎊', '🎈', '🎁', '🏆'
];

function ChatRoom({ user, onLogout }) {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);

  useEffect(() => {
    loadRoomInfo();
    loadMessages();
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

  const loadRoomInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      const endpoint = room?.is_free ? 'free' : 'paid';
      const response = await axios.get(`${API_URL}/api/rooms/${endpoint}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      
      const currentRoom = response.data.find(r => r.id === parseInt(roomId));
      setRoom(currentRoom);
    } catch (error) {
      console.error('채팅방 정보 로딩 실패:', error);
    }
  };

  const loadMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/rooms/${roomId}/messages`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setMessages(response.data);
    } catch (error) {
      console.error('메시지 로딩 실패:', error);
    }
  };

  const connectWebSocket = () => {
    const token = localStorage.getItem('token');
    const websocket = new WebSocket(`${WS_URL}/ws/chat/${roomId}?token=${token}`);

    websocket.onopen = () => {
      console.log('WebSocket 연결됨');
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'message') {
        setMessages(prev => [...prev, {
          id: data.id,
          user_id: data.user_id,
          content: data.content,
          message_type: data.message_type,
          file_url: data.file_url,
          file_name: data.file_name,
          created_at: data.timestamp,
          user: {
            name: data.user_name,
            role: data.user_role
          }
        }]);
      } else if (data.type === 'system') {
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: data.message,
          message_type: 'system',
          created_at: data.timestamp
        }]);
      } else if (data.type === 'signal') {
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: data.content,
          message_type: 'signal',
          created_at: data.timestamp,
          user: {
            name: 'MT4 시그널',
            role: 'system'
          }
        }]);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket 연결 종료');
      setConnected(false);
      
      // 재연결 시도
      setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };

    setWs(websocket);
  };

  const sendMessage = (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !ws || !connected) return;

    // 일반 회원은 메시지 전송 불가
    if (user.role === 'member') {
      alert('관리자와 직원만 메시지를 보낼 수 있습니다.');
      return;
    }

    ws.send(JSON.stringify({
      message: newMessage,
      type: 'text'
    }));

    setNewMessage('');
    setShowEmojiPicker(false);
  };

  const handleEmojiClick = (emoji) => {
    setNewMessage(prev => prev + emoji);
    setShowEmojiPicker(false);
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 이미지 파일인지 확인
    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드 가능합니다.');
      return;
    }

    setUploadingImage(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/upload/image`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // 이미지 메시지 전송
      if (ws && connected) {
        ws.send(JSON.stringify({
          message: `[이미지: ${response.data.filename}]`,
          type: 'image',
          file_url: response.data.url,
          file_name: response.data.filename
        }));
      }
    } catch (error) {
      alert('이미지 업로드 실패: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploadingImage(false);
      e.target.value = '';
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingFile(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/upload/file`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // 파일 메시지 전송
      if (ws && connected) {
        ws.send(JSON.stringify({
          message: `[파일: ${response.data.filename}]`,
          type: 'file',
          file_url: response.data.url,
          file_name: response.data.filename
        }));
      }
    } catch (error) {
      alert('파일 업로드 실패: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploadingFile(false);
      e.target.value = '';
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getUserRoleBadge = (role) => {
    const badges = {
      admin: { text: '일타훈장님', class: 'admin' },
      staff: { text: '서브관리자', class: 'staff' },
      member: { text: '회원', class: 'member' },
      system: { text: 'SYSTEM', class: 'system' }
    };
    return badges[role] || badges.member;
  };

  const canSendMessage = () => {
    if (!room) return false;
    // 관리자와 직원(서브관리자)만 메시지 전송 가능
    if (user.role === 'member') return false;
    return true;
  };

  const renderMessage = (message) => {
    if (message.message_type === 'image') {
      return (
        <div className="message-image">
          <img 
            src={`${API_URL}${message.file_url}`} 
            alt={message.file_name}
            onClick={() => window.open(`${API_URL}${message.file_url}`, '_blank')}
          />
          <div className="message-time">{formatTime(message.created_at)}</div>
        </div>
      );
    } else if (message.message_type === 'file') {
      return (
        <div className="message-file">
          <a 
            href={`${API_URL}${message.file_url}`} 
            download={message.file_name}
            target="_blank"
            rel="noopener noreferrer"
          >
            📎 {message.file_name}
          </a>
          <div className="message-time">{formatTime(message.created_at)}</div>
        </div>
      );
    } else {
      return (
        <>
          <div className="message-header">
            <span className="sender-name">{message.user?.name}</span>
            <span className={`role-badge ${getUserRoleBadge(message.user?.role).class}`}>
              {getUserRoleBadge(message.user?.role).text}
            </span>
            <span className="message-time">{formatTime(message.created_at)}</span>
          </div>
          <div className="message-content">{message.content}</div>
        </>
      );
    }
  };

  return (
    <div className="chatroom-container">
      <header className="chatroom-header">
        <button className="back-button" onClick={() => navigate('/chat')}>
          ← 뒤로
        </button>
        <div className="room-title">
          <h2>{room?.name || '채팅방'}</h2>
          <span className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? '● 연결됨' : '○ 연결 안됨'}
          </span>
        </div>
        <div className="header-actions">
          <span className="user-name">{user.name}</span>
          <button className="logout-button" onClick={onLogout}>로그아웃</button>
        </div>
      </header>

      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={message.id || index} 
            className={`message ${message.message_type} ${message.user_id === user.id ? 'own' : ''}`}
          >
            {message.message_type === 'system' ? (
              <div className="system-message">{message.content}</div>
            ) : message.message_type === 'signal' ? (
              <div className="signal-message">
                <div className="signal-header">📊 트레이딩 시그널</div>
                <pre className="signal-content">{message.content}</pre>
                <div className="message-time">{formatTime(message.created_at)}</div>
              </div>
            ) : (
              renderMessage(message)
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="message-input-container" onSubmit={sendMessage}>
        {/* 파일 업로드 버튼 */}
        {canSendMessage() && (
          <div className="upload-buttons">
            <input
              type="file"
              ref={imageInputRef}
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleImageUpload}
            />
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.zip"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            
            <button
              type="button"
              className="upload-btn"
              onClick={() => imageInputRef.current?.click()}
              disabled={uploadingImage || !connected}
              title="이미지 업로드"
            >
              {uploadingImage ? '⏳' : '🖼️'}
            </button>
            
            <button
              type="button"
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingFile || !connected}
              title="파일 업로드"
            >
              {uploadingFile ? '⏳' : '📎'}
            </button>
            
            <button
              type="button"
              className="emoji-btn"
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              disabled={!connected}
              title="이모티콘"
            >
              😊
            </button>
          </div>
        )}

        {/* 이모티콘 선택기 */}
        {showEmojiPicker && canSendMessage() && (
          <div className="emoji-picker">
            {EMOJIS.map((emoji, index) => (
              <button
                key={index}
                type="button"
                className="emoji-item"
                onClick={() => handleEmojiClick(emoji)}
              >
                {emoji}
              </button>
            ))}
          </div>
        )}

        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={
            canSendMessage() 
              ? "메시지를 입력하세요..." 
              : "관리자와 서브관리자만 메시지를 보낼 수 있습니다"
          }
          disabled={!canSendMessage() || !connected}
          className="message-input"
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={!newMessage.trim() || !canSendMessage() || !connected}
        >
          전송
        </button>
      </form>
    </div>
  );
}

export default ChatRoom;
