import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { Grid, Card, CardContent, CardActions, Button, Typography, Box } from '@mui/material';
import { Add as AddIcon, Search as SearchIcon, Mic as MicIcon } from '@mui/icons-material';

const HomePage = () => {
    const { t } = useLanguage();
    const navigate = useNavigate();

    const features = [
        {
            title: t('new_conversation'),
            description: t('new_conversation_desc'),
            icon: <AddIcon fontSize="large" />,
            action: () => navigate('/new-conversation')
        },
        {
            title: t('search_conversations'),
            description: t('search_conversations_desc'),
            icon: <SearchIcon fontSize="large" />,
            action: () => navigate('/search')
        },
        {
            title: t('start_recording'),
            description: t('start_recording_desc'),
            icon: <MicIcon fontSize="large" />,
            action: () => navigate('/record')
        }
    ];

    return (
        <Grid container spacing={3}>
            {features.map((feature, index) => (
                <Grid item xs={12} md={4} key={index}>
                    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <CardContent sx={{ flexGrow: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                                {feature.icon}
                            </Box>
                            <Typography gutterBottom variant="h5" component="h2" align="center">
                                {feature.title}
                            </Typography>
                            <Typography align="center">
                                {feature.description}
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Button 
                                fullWidth 
                                variant="contained" 
                                onClick={feature.action}
                                startIcon={feature.icon}
                            >
                                {feature.title}
                            </Button>
                        </CardActions>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};

export default HomePage; 