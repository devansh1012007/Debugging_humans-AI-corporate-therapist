import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // Import the App we explained above
import './index.css'

// Find the element with id="root" and put the App inside it
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)