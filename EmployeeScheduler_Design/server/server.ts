// server/server.ts

import 'reflect-metadata';
import express from 'express';
import { createConnection } from 'typeorm';
import themeRoutes from './routes/themeRoutes';
import userRoutes from './routes/userRoutes';
// import your session or JWT auth middleware as needed

async function startServer() {
  try {
    await createConnection({
      type: 'postgres', // or 'mysql', 'sqlite', etc.
      host: 'localhost',
      port: 5432,
      username: 'test',
      password: 'test',
      database: 'schedulerdb',
      entities: [__dirname + '/models/*.ts'],
      synchronize: true, // for dev only, auto-creates tables
    });

    const app = express();
    app.use(express.json());

    // Example: app.use(sessionMiddleware) or JWT verification, etc.

    // Example: all /api/theme, /api/user require auth
    app.use('/api/theme', themeRoutes);
    app.use('/api/user', userRoutes);

    // Serve static front-end
    // e.g. app.use(express.static('Front'));

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Error starting server:', error);
  }
}

startServer();
