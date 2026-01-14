import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import RoomList from './pages/RoomList';
import ChatRoom from './pages/ChatRoom';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        {/* 메인 페이지 - 무료 리딩방 목록 */}
        <Route path="/" element={<Home />} />
        
        {/* 로그인 페이지 */}
        <Route path="/login" element={<Login />} />
        
        {/* 유료방 목록 - 로그인 필요 */}
        <Route 
          path="/rooms" 
          element={
            <PrivateRoute>
              <RoomList />
            </PrivateRoute>
          } 
        />
        
        {/* 채팅방 */}
        <Route path="/chat/:roomId" element={<ChatRoom />} />
        
        {/* 잘못된 경로는 메인으로 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
