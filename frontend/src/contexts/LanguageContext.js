import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState('en');
    const [translations, setTranslations] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Get language from cookie or default to English
        const savedLanguage = document.cookie
            .split('; ')
            .find(row => row.startsWith('language='))
            ?.split('=')[1] || 'en';
        
        setLanguage(savedLanguage);
        fetchTranslations();
    }, []);

    const fetchTranslations = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_URL}/translations`, {
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            setTranslations(response.data);
        } catch (error) {
            console.error('Error fetching translations:', error);
        } finally {
            setLoading(false);
        }
    };

    const changeLanguage = async (newLanguage) => {
        try {
            setLoading(true);
            await axios.post(`${API_URL}/language`, 
                { language: newLanguage },
                {
                    withCredentials: true,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
            setLanguage(newLanguage);
            await fetchTranslations();
            // Set cookie manually since we're in a different domain
            document.cookie = `language=${newLanguage}; path=/; max-age=31536000`; // 1 year
        } catch (error) {
            console.error('Error changing language:', error);
        } finally {
            setLoading(false);
        }
    };

    const t = (key) => {
        return translations[key] || key;
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <LanguageContext.Provider value={{ language, changeLanguage, t, translations }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}; 