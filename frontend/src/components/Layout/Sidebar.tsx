import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Box, Avatar, Typography, IconButton } from '@mui/material';
import { People as PeopleIcon, Security as SecurityIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { useAuthStore } from '../../store/authStore';
import { ROUTES } from "../../constants.ts";

const DRAWER_WIDTH = 240;

interface SidebarProps {
  user: {
    name: string;
    avatar: string;
  };
}

const Sidebar: React.FC<SidebarProps> = ({ user }) => {
  const location = useLocation();
  const logout = useAuthStore((state) => state.logout);

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          bgcolor: 'grey.50',
          border: 'none',
        },
      }}
    >
      {/* Logo */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', height: 64 }}>
        <Link to="/" style={{ textDecoration: 'none' }}>
          <Typography variant="h5" color="primary" fontWeight="bold">
            LOGO
          </Typography>
        </Link>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, px: 2, py: 1 }}>
        <ListItemButton
          component={Link}
          to={ROUTES.PATIENTS}
          selected={location.pathname === ROUTES.PATIENTS}
          sx={{
            borderRadius: 2,
            mb: 1,
            '&.Mui-selected': {
              bgcolor: 'grey.200',
              '&:hover': {
                bgcolor: 'grey.200',
              },
            },
            '& .MuiListItemIcon-root': {
              color: 'grey.600',
            },
            '& .MuiListItemText-primary': {
              color: 'grey.700',
              fontWeight: 500,
            },
          }}
        >
          <ListItemIcon>
            <PeopleIcon />
          </ListItemIcon>
          <ListItemText primary="Patients" />
        </ListItemButton>

        <ListItemButton
          component={Link}
          to={ROUTES.ADMINS}
          selected={location.pathname === ROUTES.ADMINS}
          sx={{
            borderRadius: 2,
            '&.Mui-selected': {
              bgcolor: 'grey.200',
              '&:hover': {
                bgcolor: 'grey.200',
              },
            },
            '& .MuiListItemIcon-root': {
              color: 'grey.600',
            },
            '& .MuiListItemText-primary': {
              color: 'grey.700',
              fontWeight: 500,
            },
          }}
        >
          <ListItemIcon>
            <SecurityIcon />
          </ListItemIcon>
          <ListItemText primary="Admin users" />
        </ListItemButton>
      </List>

      {/* User Profile & Logout */}
      <Box 
        sx={{ 
          p: 2, 
          mt: 'auto',
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          borderTop: 1,
          borderColor: 'grey.200'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
          <Avatar 
            src={user.avatar} 
            alt="" 
            sx={{ 
              width: 40, 
              height: 40,
              bgcolor: 'grey.100'
            }}
          />
          <Box sx={{ ml: 1.5}}>
            <Typography
              variant="body2"
              sx={{ 
                color: 'grey.900',
                fontWeight: 500,
                lineHeight: 1.2
              }}
            >
              {user.name}
            </Typography>
          </Box>
        </Box>
        <IconButton 
          onClick={logout} 
          size="small" 
          sx={{ 
            color: 'grey.500',
            '&:hover': {
              color: 'grey.700'
            }
          }}
        >
          <LogoutIcon fontSize="small" />
        </IconButton>
      </Box>
    </Drawer>
  );
};

export default Sidebar; 