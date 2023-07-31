import React, { useState, useEffect } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import jwtDecode from 'jwt-decode'

const Register = ({ setUser, setIsAccountCreation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/register', {
        email,
        password,
      });

      const userData = response.data;

      // Update the user context using setUser
      setUser(userData);

      console.log(response.data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <>
      <h2 className='text-center'>Register</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        className='w-100 mb-2'
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        className='w-100 mb-2'
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin} className='primary w-100 mb-1'>Register</button>
      <button onClick={()=> setIsAccountCreation(false)} className='warn w-100'> Already have an account?</button>
    </>
  );
};

const Login = ({ setUser, setIsAccountCreation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
    
  const responseMessage = async (response) => {
    const USER_CREDENTIAL = jwtDecode(response.credential);
    try {
      const apiResponse = await axios.post('http://127.0.0.1:8000/auth/OauthGoogle', {
        email: USER_CREDENTIAL['email'],
        password: USER_CREDENTIAL['sub'],
      });
      const userData = apiResponse.data;
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
    }
  }
  

  const errorMessage = (error) => {
    console.error(error);
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/login', {
        email,
        password,
      });

      const userData = response.data;

      // Update the user context using setUser
      setUser(userData);

      console.log(response.data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div>
      <h2 className='text-center'>Login</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        className='w-100 mb-2'
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        className='w-100 mb-2'
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin} className='primary w-100  mb-1'>Login</button>
      <GoogleLogin onSuccess={responseMessage} onError={errorMessage} />
      <button onClick={()=> setIsAccountCreation(true)} className='warn w-100'> Don't have an account?</button>
    </div>
  );
};



const ProcessLoginPage = ({ setUser }) => {
  const [isAccountCreation, setIsAccountCreation] = useState(false);

  return (
    <div className="app light">
      <div className="container">
      {isAccountCreation ? <Register setUser={setUser} setIsAccountCreation={setIsAccountCreation} /> : <Login setUser={setUser} setIsAccountCreation={setIsAccountCreation} />}
      </div>
    </div>
  );
};

export default ProcessLoginPage;
