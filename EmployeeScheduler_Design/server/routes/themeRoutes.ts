// server/routes/themeRoutes.ts
import { Router } from 'express';

const router = Router();

router.put('/theme', (req, res) => {
  // Must be logged in
  if (!req.session.user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  const { theme } = req.body;
  if (!theme) {
    return res.status(400).json({ error: 'No theme provided' });
  }

  // Update the user’s theme in session
  req.session.user.theme = theme;

  return res.json({ message: `Theme updated to ${theme}`, user: req.session.user });
});

export default router;
