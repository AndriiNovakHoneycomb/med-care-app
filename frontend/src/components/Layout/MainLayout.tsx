import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Toolbar } from '@mui/material';
import { useAuthStore } from '../../store/authStore';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

const MainLayout: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return null; // or redirect to login
  }

  const userWithAvatar = {
    ...user,
    avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=f3f4f6&color=6d28d9`,
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <Navbar />
      <Sidebar user={userWithAvatar} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'grey.50',
          minHeight: '100vh',
          p: 3
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout; 