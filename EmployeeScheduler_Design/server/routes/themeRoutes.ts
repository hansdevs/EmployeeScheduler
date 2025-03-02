// server/routes/themeRoutes.ts

import { Request, Response, Router } from 'express';
import { getRepository } from 'typeorm';
import { User } from '../models/User';

const router = Router();

/**
 * PUT /api/theme
 * Body: { theme: 'light' | 'dark' }
 * Saves the user’s preferred theme in the DB
 */
router.put('/', async (req: Request, res: Response) => {
  try {
    // You must have some form of auth. For example:
    // if you're using sessions:   const userId = req.session.userId;
    // if you're using JWT:        const userId = req.user.id;
    const userId = req.user?.id; // adjust to your actual auth

    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const { theme } = req.body;
    if (!['light', 'dark'].includes(theme)) {
      return res.status(400).json({ message: 'Invalid theme' });
    }

    const userRepo = getRepository(User);
    const user = await userRepo.findOne(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    user.theme = theme as 'light' | 'dark';
    await userRepo.save(user);

    return res.json({ message: 'Theme updated successfully', theme: user.theme });
  } catch (error) {
    console.error('PUT /api/theme error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

export default router;
