#!/bin/bash

# Navigate to frontend directory
cd frontend

# Install dependencies and create package-lock.json
npm install

# Create necessary directories if they don't exist
mkdir -p src/components
mkdir -p src/contexts
mkdir -p src/services
mkdir -p public

# Create basic React files if they don't exist
if [ ! -f "src/index.js" ]; then
    echo "import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();" > src/index.js
fi

if [ ! -f "src/reportWebVitals.js" ]; then
    echo "const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;" > src/reportWebVitals.js
fi

# Create public/index.html
if [ ! -f "public/index.html" ]; then
    echo '<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Medical Conversation Analysis System"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>Medical Conversation Analysis</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>' > public/index.html
fi

# Create public/manifest.json
if [ ! -f "public/manifest.json" ]; then
    echo '{
  "short_name": "Medical Analysis",
  "name": "Medical Conversation Analysis System",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}' > public/manifest.json
fi

echo "Frontend setup complete!" 