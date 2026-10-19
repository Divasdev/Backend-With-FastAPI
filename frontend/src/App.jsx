import { Navigate, Route, Routes } from 'react-router-dom';
import { Analytics } from '@vercel/analytics/react';
import { GuestOnly, RequireAuth } from './auth/AuthContext';
import Layout from './components/Layout';
import FeedPage from './pages/FeedPage';
import LoginPage from './pages/LoginPage';
import PostPage from './pages/PostPage';
import RegisterPage from './pages/RegisterPage';
import CreatePage from './pages/CreatePage';
import EditPage from './pages/EditPage';
import ProfilePage from './pages/ProfilePage';
export default function App() {
  return (
    <>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<FeedPage />} />
          <Route path="/posts/:id" element={<PostPage />} />
          {/* Not /users/:id: Vite sends /users to the backend, so a refresh would show JSON. */}
          <Route path="/profile/:userId" element={<ProfilePage />} />
          <Route path="/login" element={<GuestOnly><LoginPage /></GuestOnly>} />
          <Route path="/register" element={<GuestOnly><RegisterPage /></GuestOnly>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        <Route path="/create" element={<RequireAuth><CreatePage /></RequireAuth>} />
        <Route path="/posts/:id/edit" element={<RequireAuth><EditPage /></RequireAuth>} />
        </Route>
        
      </Routes>
      <Analytics />
    </>
  );
}
