import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import { NotificationsOutlined, CalendarToday } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { ROUTES } from "../../constants.ts";

const DRAWER_WIDTH = 240;

const Navbar: React.FC = () => {
  const location = useLocation();
  const currentDate = new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const getPageTitle = () => {
    switch (location.pathname) {
      case ROUTES.PATIENTS:
        return 'Patients';
      case ROUTES.ADMINS:
        return 'Admin users';
      default:
        return '';
    }
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: `calc(100% - ${DRAWER_WIDTH}px)`,
        ml: `${DRAWER_WIDTH}px`,
        bgcolor: 'white',
        borderBottom: 1,
        borderColor: 'grey.200'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Typography variant="h6" color="grey.900" fontWeight={500}>
          {getPageTitle()}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            size="large"
            sx={{ color: 'grey.500' }}
          >
            <NotificationsOutlined />
          </IconButton>

          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              color: 'grey.500',
              ml: 2
            }}
          >
            <CalendarToday sx={{ fontSize: 20, mr: 1 }} />
            <Typography variant="body2">
              {currentDate}
            </Typography>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 