import React, { createContext, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Login from './pages/login';
import Feed from './pages/feed';
import './App.css';

export const UserContext = createContext();

const App = () => {
  const [user, setUser] = useState(null);

  return (
    <GoogleOAuthProvider clientId="190046103428-8b378mervfe8o5qgto9pp1293sa891h0.apps.googleusercontent.com">
      <UserContext.Provider value={{ user, setUser }}>
        <Router>
          <Routes>
            <Route path="/" element={user ? <Feed user={user} /> : <Login setUser={setUser} />} />
          </Routes>
        </Router>
      </UserContext.Provider>
    </GoogleOAuthProvider>
  );
};

export default App;
