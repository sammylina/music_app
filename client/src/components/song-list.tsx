import { Playlist, Song } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";

export default function SongList({
  playlist,
  songs,
  onBack,
  onSelect,
  selectedSong,
}: {
  playlist: Playlist;
  songs: Song[];
  onBack: () => void;
  onSelect: (song: Song) => void;
  selectedSong: Song | null;
}) {
  return (
    <div className="flex-1 overflow-auto">
      <div className="container mx-auto p-4">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{playlist.title}</h1>
            <p className="text-sm text-muted-foreground">
              {playlist.description}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          {songs.map((song) => (
            <SongItem
              key={song.id}
              song={song}
              isSelected={selectedSong?.id === song.id}
              onClick={() => onSelect(song)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function SongItem({
  song,
  isSelected,
  onClick,
}: {
  song: Song;
  isSelected: boolean;
  onClick: () => void;
}) {
  const { data: playCount } = useQuery<number>({
    queryKey: ["/api/songs", song.id, "plays"],
  });

  return (
    <div
      className={cn(
        "p-4 rounded-md cursor-pointer transition-colors",
        isSelected
          ? "bg-primary text-primary-foreground"
          : "hover:bg-accent",
        playCount === 0 && "border-l-4 border-yellow-500",
        playCount === 1 && "border-l-4 border-green-500",
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">{song.title}</h3>
          <p className="text-sm text-muted-foreground">{song.artist}</p>
        </div>
        {playCount && playCount > 1 && (
          <div className="bg-accent text-accent-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
            {playCount}
          </div>
        )}
      </div>
    </div>
  );
}
