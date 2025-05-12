import { useState, useRef, useEffect } from "react";
import { Song } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
} from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

export default function AudioPlayer({
  song,
  onNext,
  onPrevious,
}: {
  song: Song;
  onNext: () => void;
  onPrevious: () => void;
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  useEffect(() => {
    setIsPlaying(false);
    setProgress(0);
  }, [song]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(
        (audioRef.current.currentTime / audioRef.current.duration) * 100,
      );
    }
  };

  const handlePlay = async () => {
    try {
      await apiRequest("POST", `/songs/${song.id}/play`);
      setIsPlaying(true);
      audioRef.current?.play();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to play song",
        variant: "destructive",
      });
    }
  };

  const handlePause = () => {
    setIsPlaying(false);
    audioRef.current?.pause();
  };

  const handleSeek = (value: number) => {
    if (audioRef.current) {
      const time = (value / 100) * audioRef.current.duration;
      audioRef.current.currentTime = time;
      setProgress(value);
    }
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-card p-4 border-t">
      <audio
        ref={audioRef}
        src={`/api/songs/${song.id}/audio`}
        onTimeUpdate={handleTimeUpdate}
        onEnded={onNext}
      />

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-sm font-medium">{song.title}</h3>
            <p className="text-xs text-muted-foreground">{song.artist}</p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMuted(!isMuted)}
            >
              {isMuted ? <VolumeX /> : <Volume2 />}
            </Button>
            <Slider
              className="w-24"
              value={[isMuted ? 0 : volume * 100]}
              onValueChange={(value) => setVolume(value[0] / 100)}
              max={100}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={onPrevious}>
            <SkipBack />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => skip(-5)}>
            -5s
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={isPlaying ? handlePause : handlePlay}
          >
            {isPlaying ? <Pause /> : <Play />}
          </Button>
          <Button variant="ghost" size="icon" onClick={() => skip(5)}>
            +5s
          </Button>
          <Button variant="ghost" size="icon" onClick={onNext}>
            <SkipForward />
          </Button>
        </div>

        <Slider
          value={[progress]}
          onValueChange={(value) => handleSeek(value[0])}
          max={100}
          className="w-full"
        />
      </div>
    </div>
  );
}
