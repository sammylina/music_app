import type { Express } from "express";
import { createServer, type Server } from "http";
import { setupAuth } from "./auth";
import multer from "multer";
import { storage } from "./storage";

const upload = multer({ memory: true });

export async function registerRoutes(app: Express): Promise<Server> {
  setupAuth(app);

  app.get("/api/playlists", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const playlists = await storage.getPlaylists();
    res.json(playlists);
  });

  app.get("/api/playlists/:id/songs", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const songs = await storage.getSongs(parseInt(req.params.id));
    res.json(songs);
  });

  app.post("/api/playlists", async (req, res) => {
    if (!req.isAuthenticated() || !req.user.isAdmin) return res.sendStatus(401);
    const playlist = await storage.createPlaylist(req.body);
    res.json(playlist);
  });

  app.post("/api/songs", upload.single("audio"), async (req, res) => {
    if (!req.isAuthenticated() || !req.user.isAdmin) return res.sendStatus(401);
    if (!req.file) return res.status(400).send("No audio file uploaded");

    const song = await storage.createSong(
      {
        ...req.body,
        audioFile: req.file.originalname,
      },
      req.file.buffer,
    );
    res.json(song);
  });

  app.get("/api/songs/:id/audio", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const song = await storage.getSong(parseInt(req.params.id));
    if (!song) return res.sendStatus(404);

    const audioFile = await storage.getAudioFile(song.audioFile);
    if (!audioFile) return res.sendStatus(404);

    res.type("audio/mpeg").send(audioFile);
  });

  app.post("/api/songs/:id/play", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    await storage.recordPlay(req.user.id, parseInt(req.params.id));
    res.sendStatus(200);
  });

  const httpServer = createServer(app);
  return httpServer;
}
