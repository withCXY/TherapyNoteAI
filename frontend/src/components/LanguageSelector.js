import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { Button, ButtonGroup } from '@mui/material';
import TranslateIcon from '@mui/icons-material/Translate';

const LanguageSelector = () => {
    const { language, changeLanguage } = useLanguage();

    return (
        <ButtonGroup
            variant="contained"
            aria-label="language selector"
            sx={{
                position: 'fixed',
                top: 16,
                right: 16,
                zIndex: 1000,
            }}
        >
            <Button
                startIcon={<TranslateIcon />}
                onClick={() => changeLanguage('en')}
                variant={language === 'en' ? 'contained' : 'outlined'}
            >
                EN
            </Button>
            <Button
                onClick={() => changeLanguage('zh')}
                variant={language === 'zh' ? 'contained' : 'outlined'}
            >
                中文
            </Button>
        </ButtonGroup>
    );
};

export default LanguageSelector; 