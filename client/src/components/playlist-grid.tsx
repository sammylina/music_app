import { Playlist } from "@shared/schema";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

export default function PlaylistGrid({
  playlists,
  onSelect,
}: {
  playlists: Playlist[];
  onSelect: (playlist: Playlist) => void;
}) {
  const { logoutMutation } = useAuth();

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Playlists</h1>
        <Button variant="ghost" size="icon" onClick={() => logoutMutation.mutate()}>
          <LogOut className="h-5 w-5" />
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {playlists.map((playlist) => (
          <Card
            key={playlist.id}
            className="cursor-pointer hover:bg-accent transition-colors"
            onClick={() => onSelect(playlist)}
          >
            <CardContent className="p-4">
              <h3 className="font-medium mb-2">{playlist.title}</h3>
              <p className="text-sm text-muted-foreground">
                {playlist.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
