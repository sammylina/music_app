import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  isAdmin: boolean("is_admin").notNull().default(false),
});

export const playlists = pgTable("playlists", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
});

export const songs = pgTable("songs", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  artist: text("artist").notNull(),
  playlistId: integer("playlist_id").notNull(),
  audioFile: text("audio_file").notNull(),
});

export const playHistory = pgTable("play_history", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull(),
  songId: integer("song_id").notNull(),
  playedAt: timestamp("played_at").notNull().defaultNow(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertPlaylistSchema = createInsertSchema(playlists);
export const insertSongSchema = createInsertSchema(songs);
export const insertPlayHistorySchema = createInsertSchema(playHistory);

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type Playlist = typeof playlists.$inferSelect;
export type Song = typeof songs.$inferSelect;
export type PlayHistory = typeof playHistory.$inferSelect;
