// server/models/User.ts

import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ default: 'light' })
  theme: 'light' | 'dark';

  @Column()
  email: string;

  @Column()
  passwordHash: string;

  // Add other fields as needed
}
