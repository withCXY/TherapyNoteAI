import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import {
    Paper,
    TextField,
    Button,
    Typography,
    Box,
    IconButton,
} from '@mui/material';
import { MicOff, Mic, Stop } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const NewConversation = () => {
    const { t } = useLanguage();
    const [isRecording, setIsRecording] = useState(false);
    const [patientId, setPatientId] = useState('');
    const [doctorId, setDoctorId] = useState('');

    const handleStartRecording = () => {
        // TODO: Implement recording functionality
        setIsRecording(true);
    };

    const handleStopRecording = () => {
        // TODO: Implement stop recording and processing
        setIsRecording(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${API_URL}/conversations/`, {
                patient_id: patientId,
                doctor_id: doctorId,
            });
            console.log('Conversation created:', response.data);
            // TODO: Handle successful creation
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    };

    return (
        <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
            <Typography variant="h5" gutterBottom>
                {t('new_conversation')}
            </Typography>
            <form onSubmit={handleSubmit}>
                <TextField
                    fullWidth
                    label={t('patient_id')}
                    value={patientId}
                    onChange={(e) => setPatientId(e.target.value)}
                    margin="normal"
                    required
                />
                <TextField
                    fullWidth
                    label={t('doctor_id')}
                    value={doctorId}
                    onChange={(e) => setDoctorId(e.target.value)}
                    margin="normal"
                    required
                />
                <Box sx={{ my: 2, display: 'flex', justifyContent: 'center' }}>
                    <IconButton
                        color={isRecording ? 'error' : 'primary'}
                        size="large"
                        onClick={isRecording ? handleStopRecording : handleStartRecording}
                    >
                        {isRecording ? <Stop /> : <Mic />}
                    </IconButton>
                </Box>
                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={isRecording}
                >
                    {t('save')}
                </Button>
            </form>
        </Paper>
    );
};

export default NewConversation; 