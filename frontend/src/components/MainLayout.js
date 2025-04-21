import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import LanguageSelector from './LanguageSelector';

const MainLayout = ({ children }) => {
    const { t } = useLanguage();

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        {t('welcome')}
                    </Typography>
                    <LanguageSelector />
                </Toolbar>
            </AppBar>
            <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
                {children}
            </Container>
        </Box>
    );
};

export default MainLayout; 