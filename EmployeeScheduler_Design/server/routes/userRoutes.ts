// server/routes/userRoutes.ts
import { Router } from 'express';

const router = Router();

// Hard-coded test user
const validUser = {
  username: 'Test',
  password: 'password',
  theme: 'light', // default or whatever you like
};

router.post('/login', (req, res) => {
  const { username, password } = req.body;

  // Check user credentials
  if (username === validUser.username && password === validUser.password) {
    // Store user in session
    req.session.user = {
      username: validUser.username,
      theme: validUser.theme,
    };
    return res.json({ message: 'Login successful' });
  }

  // Wrong credentials
  return res.status(401).json({ error: 'Invalid username or password' });
});

router.get('/user', (req, res) => {
  // If user is not in session, return 401
  if (!req.session.user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  // Return user info (e.g., username, theme)
  return res.json(req.session.user);
});

export default router;
