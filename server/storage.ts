import { IStorage } from "./types";
import { User, InsertUser, Playlist, Song, PlayHistory } from "@shared/schema";
import session from "express-session";
import createMemoryStore from "memorystore";

const MemoryStore = createMemoryStore(session);

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private playlists: Map<number, Playlist>;
  private songs: Map<number, Song>;
  private playHistory: Map<number, PlayHistory>;
  private audioFiles: Map<string, Buffer>;
  sessionStore: session.Store;
  currentId: number;

  constructor() {
    this.users = new Map();
    this.playlists = new Map();
    this.songs = new Map();
    this.playHistory = new Map();
    this.audioFiles = new Map();
    this.currentId = 1;
    this.sessionStore = new MemoryStore({
      checkPeriod: 86400000,
    });

    // Create default admin user
    this.createUser({
      username: "admin@example.com",
      password: "admin123",
      isAdmin: true,
    });

    // Seed playlists
    const playlist1 = this.createPlaylist({
      title: "Chill Vibes",
      description: "Relaxing tunes for your downtime",
    });

    const playlist2 = this.createPlaylist({
      title: "Workout Mix",
      description: "High-energy songs to keep you motivated",
    });

    // Seed songs
    Promise.all([playlist1, playlist2]).then(([chillPlaylist, workoutPlaylist]) => {
      // Chill playlist songs
      this.createSong({
        title: "Ocean Waves",
        artist: "Nature Sounds",
        playlistId: chillPlaylist.id,
        audioFile: "ocean-waves.mp3"
      }, Buffer.from(""));

      this.createSong({
        title: "Gentle Rain",
        artist: "Ambient Music",
        playlistId: chillPlaylist.id,
        audioFile: "gentle-rain.mp3"
      }, Buffer.from(""));

      // Workout playlist songs
      this.createSong({
        title: "Power Up",
        artist: "Energy Beats",
        playlistId: workoutPlaylist.id,
        audioFile: "power-up.mp3"
      }, Buffer.from(""));

      this.createSong({
        title: "Fast Pace",
        artist: "Workout Remix",
        playlistId: workoutPlaylist.id,
        audioFile: "fast-pace.mp3"
      }, Buffer.from(""));
    });
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createPlaylist(playlist: Omit<Playlist, "id">): Promise<Playlist> {
    const id = this.currentId++;
    const newPlaylist = { ...playlist, id };
    this.playlists.set(id, newPlaylist);
    return newPlaylist;
  }

  async getPlaylists(): Promise<Playlist[]> {
    return Array.from(this.playlists.values());
  }

  async getPlaylist(id: number): Promise<Playlist | undefined> {
    return this.playlists.get(id);
  }

  async createSong(song: Omit<Song, "id">, audioFile: Buffer): Promise<Song> {
    const id = this.currentId++;
    const newSong = { ...song, id };
    this.songs.set(id, newSong);
    this.audioFiles.set(newSong.audioFile, audioFile);
    return newSong;
  }

  async getSongs(playlistId: number): Promise<Song[]> {
    return Array.from(this.songs.values()).filter(
      (song) => song.playlistId === playlistId,
    );
  }

  async getAudioFile(audioFile: string): Promise<Buffer | undefined> {
    return this.audioFiles.get(audioFile);
  }

  async recordPlay(userId: number, songId: number): Promise<void> {
    const id = this.currentId++;
    const playRecord: PlayHistory = {
      id,
      userId,
      songId,
      playedAt: new Date(),
    };
    this.playHistory.set(id, playRecord);
  }

  async getPlayCount(songId: number): Promise<number> {
    return Array.from(this.playHistory.values()).filter(
      (record) => record.songId === songId,
    ).length;
  }

  async getUserPlayCount(userId: number, songId: number): Promise<number> {
    return Array.from(this.playHistory.values()).filter(
      (record) => record.userId === userId && record.songId === songId,
    ).length;
  }
}

export const storage = new MemStorage();