import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Playlist, Song } from "@shared/schema";
import PlaylistGrid from "@/components/playlist-grid";
import SongList from "@/components/song-list";
import AudioPlayer from "@/components/audio-player";

export default function HomePage() {
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(null);
  const [selectedSong, setSelectedSong] = useState<Song | null>(null);

  const { data: playlists } = useQuery<Playlist[]>({
    queryKey: ["/api/playlists"],
  });

  const { data: songs } = useQuery<Song[]>({
    queryKey: ["/api/playlists", selectedPlaylist?.id, "songs"],
    enabled: !!selectedPlaylist,
  });

  return (
    <div className="min-h-screen bg-background">
      {!selectedPlaylist ? (
        <PlaylistGrid
          playlists={playlists || []}
          onSelect={setSelectedPlaylist}
        />
      ) : (
        <div className="h-screen flex flex-col">
          <SongList
            playlist={selectedPlaylist}
            songs={songs || []}
            onBack={() => setSelectedPlaylist(null)}
            onSelect={setSelectedSong}
            selectedSong={selectedSong}
          />
          {selectedSong && (
            <AudioPlayer
              song={selectedSong}
              onNext={() => {
                const currentIndex = songs?.findIndex(s => s.id === selectedSong.id) || 0;
                setSelectedSong(songs?.[currentIndex + 1] || null);
              }}
              onPrevious={() => {
                const currentIndex = songs?.findIndex(s => s.id === selectedSong.id) || 0;
                setSelectedSong(songs?.[currentIndex - 1] || null);
              }}
            />
          )}
        </div>
      )}
    </div>
  );
}
