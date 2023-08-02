import React, { useState, useEffect } from 'react';
import { GoogleLogin, useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import jwtDecode from 'jwt-decode'



const Register = ({ setUser, setIsAccountCreation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/register', {
        email,
        password,
      });

      const userData = jwtDecode(response.access);
      setUser({ ...userData, access_token: response['access'] });

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
    
  const login = useGoogleLogin({
    onSuccess: async tokenResponse => {
      // tokenResponse
      // const userInfo = await axios
      // .post('http://127.0.0.1:8000/auth/rest-auth/google/', {
      //   'access_token': tokenResponse.access_token
      // })
      // .then(res => res.data);



      // const clientId = '190046103428-8b378mervfe8o5qgto9pp1293sa891h0.apps.googleusercontent.com';
      // // const redirectUri = '/';
      // // const scope = 'openid email profile';

      // const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}`
      // // &redirect_uri=${redirectUri}&response_type=id_token&scope=${scope}`;

      // const userInfo = await axios
      // .get(url, {
      // headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
      // })
      // .then(res => res.data);

      // console.log(userInfo);
      // debugger
    }
  });

  const responseMessage = async (response) => {
    const userInfo = await axios
    .post('http://127.0.0.1:8000/api/rest-auth/google_login/', {
      'access_token': response.credential
    })
    .then(res => res.data);

    const userData = jwtDecode(userInfo.access)
    setUser({ ...userData, access_token: userInfo['access'] });
  }

  const errorMessage = (error) => {
    console.error(error);
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/login', {
        email,
        password,
      });

      const userData = jwtDecode(response.access);

      // Update the user context using setUser
      setUser({ ...userData, access_token: response['access'] });

      console.log(response.data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const googleResponse = (response) => {
    console.log(response);
  }

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
      {/* <button onClick={login} onError={errorMessage}>Google login</button> */}
      <GoogleLogin onSuccess={responseMessage}/>
      {/* <button onClick={login}>Login Google</button> */}
      {/* <GoogleLogin
          clientId="190046103428-8b378mervfe8o5qgto9pp1293sa891h0.apps.googleusercontent.com"
          buttonText="LOGIN WITH GOOGLE"
          onSuccess={googleResponse}
          onFailure={googleResponse}
        /> */}
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
