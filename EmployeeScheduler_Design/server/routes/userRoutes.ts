// server/routes/userRoutes.ts

import { Request, Response, Router } from 'express';
import { getRepository } from 'typeorm';
import { User } from '../models/User';

const router = Router();

/**
 * GET /api/user
 * Returns the current user's info (including theme).
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const userId = req.user?.id; // or req.session.userId
    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const userRepo = getRepository(User);
    const user = await userRepo.findOne(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Return only what you want the client to see
    return res.json({
      id: user.id,
      email: user.email,
      theme: user.theme,
    });
  } catch (error) {
    console.error('GET /api/user error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

export default router;
