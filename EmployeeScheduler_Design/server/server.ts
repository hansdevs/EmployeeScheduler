// server/server.ts
import express from 'express';
import session from 'express-session';
import path from 'path';

// Import our route modules
import userRoutes from './routes/userRoutes';
import themeRoutes from './routes/themeRoutes';

// Create Express app
const app = express();

// Body parsing middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session configuration (storing session in memory for demo)
// For production, use a real session store like Redis or a DB
app.use(
  session({
    secret: 'some-random-secret', // change to something secure in production
    resave: false,
    saveUninitialized: false,
    cookie: {
      maxAge: 1000 * 60 * 60, // 1 hour
    },
  })
);

// Serve static front-end from "Front" folder
// (If your entry file is "Front/pages/index.html", just ensure the path is correct)
app.use(express.static(path.join(__dirname, '../../Front')));

// Mount routes under /api
app.use('/api', userRoutes);
app.use('/api', themeRoutes);

// Fallback: if no matching route, serve index.html (SPA-like fallback)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../../Front/pages/index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
