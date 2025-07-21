"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Play, Download, Volume2, Sun, Moon, Instagram, Youtube } from "lucide-react";

const XIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const TikTokIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
  </svg>
);

export default function BrainrotGenerator() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isResizing, setIsResizing] = useState(false);
  const [leftWidth, setLeftWidth] = useState(25);
  const [middleWidth, setMiddleWidth] = useState(30);
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<"video" | "image">("video");

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
      document.documentElement.style.colorScheme = "dark";
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.style.colorScheme = "light";
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleMouseDown = (dividerIndex: number) => {
    setIsResizing(true);

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const containerWidth = containerRect.width;
      const mouseX = e.clientX - containerRect.left;
      const percentage = (mouseX / containerWidth) * 100;

      if (dividerIndex === 0) {
        // First divider - adjust left column
        const newLeftWidth = Math.max(25, Math.min(60, percentage));
        const remainingWidth = 100 - newLeftWidth;
        const newMiddleWidth = Math.max(25, Math.min(remainingWidth - 25, middleWidth));

        setLeftWidth(newLeftWidth);
        setMiddleWidth(newMiddleWidth);
      } else {
        // Second divider - adjust middle column
        const maxMiddleWidth = 100 - leftWidth - 25; // Ensure right column has at least 25%
        const newMiddleWidth = Math.max(25, Math.min(maxMiddleWidth, percentage - leftWidth));
        setMiddleWidth(newMiddleWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const rightWidth = 100 - leftWidth - middleWidth;

  const [formData, setFormData] = useState({
    url: "",
    width: "1080",
    height: "1920",
    maxLength: "60",
    audioModel: "",
    videoTitle: "",
    videoDescription: "",
    useImageInIntro: false,
  });

  const [audioFiles] = useState([
    { id: 1, name: "brainrot_audio_1.mp3", duration: "2:34", size: "3.2 MB" },
    { id: 2, name: "brainrot_audio_2.mp3", duration: "1:45", size: "2.1 MB" },
    { id: 3, name: "brainrot_audio_3.mp3", duration: "3:12", size: "4.5 MB" },
    { id: 4, name: "brainrot_audio_4.mp3", duration: "2:01", size: "2.8 MB" },
    { id: 5, name: "brainrot_audio_5.mp3", duration: "1:58", size: "2.7 MB" },
    { id: 6, name: "brainrot_audio_6.mp3", duration: "2:45", size: "3.8 MB" },
    { id: 7, name: "brainrot_audio_7.mp3", duration: "1:32", size: "2.3 MB" },
    { id: 8, name: "brainrot_audio_8.mp3", duration: "3:05", size: "4.2 MB" },
    { id: 9, name: "brainrot_audio_9.mp3", duration: "2:18", size: "3.1 MB" },
    { id: 10, name: "brainrot_audio_10.mp3", duration: "1:55", size: "2.6 MB" },
    { id: 11, name: "brainrot_audio_11.mp3", duration: "2:42", size: "3.5 MB" },
    { id: 12, name: "brainrot_audio_12.mp3", duration: "1:38", size: "2.4 MB" },
    { id: 13, name: "brainrot_audio_13.mp3", duration: "3:21", size: "4.7 MB" },
    { id: 14, name: "brainrot_audio_14.mp3", duration: "2:15", size: "3.0 MB" },
    { id: 15, name: "brainrot_audio_15.mp3", duration: "1:49", size: "2.5 MB" },
    { id: 16, name: "brainrot_audio_16.mp3", duration: "2:56", size: "4.0 MB" },
    { id: 17, name: "brainrot_audio_17.mp3", duration: "1:27", size: "2.2 MB" },
    { id: 18, name: "brainrot_audio_18.mp3", duration: "3:08", size: "4.3 MB" },
    { id: 19, name: "brainrot_audio_19.mp3", duration: "2:33", size: "3.4 MB" },
    { id: 20, name: "brainrot_audio_20.mp3", duration: "1:52", size: "2.8 MB" },
  ]);

  const audioModels = [
    "OpenAI TTS-1",
    "OpenAI TTS-1-HD",
    "ElevenLabs Multilingual",
    "Azure Neural Voice",
    "Google Cloud TTS",
  ];

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleGenerate = () => {
    console.log("Generating video with:", formData);
    // Here you would call your backend API
  };

  return (
    <div className="min-h-screen bg-background text-foreground  overflow-hidden">
      {/* Header */}
      <div className="border-b border-border">
        <div className="flex justify-between items-center px-6 py-3">
          <div className="flex-1"></div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 via-purple-500 to-purple-600 bg-clip-text text-transparent">
            BrainrotGenerator
          </h1>
          <div className="flex-1 flex justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="h-8 w-8 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
            >
              {isDarkMode ? (
                <Sun className="h-4 w-4 text-purple-400" />
              ) : (
                <Moon className="h-4 w-4 text-purple-600" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content - Resizable 3 Columns */}
      <div
        ref={containerRef}
        className="flex h-[calc(100vh-56px)] overflow-hidden"
        style={{ userSelect: isResizing ? "none" : "auto" }}
      >
        {/* Left Panel - Video Configuration */}
        <div
          className="border-r border-border overflow-y-auto"
          style={{
            width: `${leftWidth}%`,
            scrollbarWidth: "thin",
            scrollbarColor: "rgb(147 51 234 / 0.5) transparent",
          }}
        >
          <div className="p-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-purple-400">Video Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* URL Input */}
                <div className="space-y-2">
                  <Label htmlFor="url">Source URL</Label>
                  <Input
                    id="url"
                    placeholder="https://example.com/video"
                    value={formData.url}
                    onChange={(e) => handleInputChange("url", e.target.value)}
                    className="bg-muted border-border"
                  />
                </div>

                {/* Dimensions */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="width">Width</Label>
                    <Input
                      id="width"
                      type="number"
                      placeholder="1080"
                      value={formData.width}
                      onChange={(e) => handleInputChange("width", e.target.value)}
                      className="bg-muted border-border"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="height">Height</Label>
                    <Input
                      id="height"
                      type="number"
                      placeholder="1920"
                      value={formData.height}
                      onChange={(e) => handleInputChange("height", e.target.value)}
                      className="bg-muted border-border"
                    />
                  </div>
                </div>

                {/* Max Length */}
                <div className="space-y-2">
                  <Label htmlFor="maxLength">Max Length (seconds)</Label>
                  <Input
                    id="maxLength"
                    type="number"
                    placeholder="60"
                    value={formData.maxLength}
                    onChange={(e) => handleInputChange("maxLength", e.target.value)}
                    className="bg-muted border-border"
                  />
                </div>

                {/* Audio Model Selection */}
                <div className="space-y-2">
                  <Label>Audio Model</Label>
                  <Select
                    value={formData.audioModel}
                    onValueChange={(value) => handleInputChange("audioModel", value)}
                  >
                    <SelectTrigger className="bg-muted border-border">
                      <SelectValue placeholder="Select an audio model" />
                    </SelectTrigger>
                    <SelectContent>
                      {audioModels.map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Video Title */}
                <div className="space-y-2">
                  <Label htmlFor="videoTitle">Video Title</Label>
                  <Input
                    id="videoTitle"
                    placeholder="Enter video title"
                    value={formData.videoTitle}
                    onChange={(e) => handleInputChange("videoTitle", e.target.value)}
                    className="bg-muted border-border"
                  />
                </div>

                {/* Video Description */}
                <div className="space-y-2">
                  <Label htmlFor="videoDescription">Video Description</Label>
                  <Textarea
                    id="videoDescription"
                    placeholder="Enter video description"
                    value={formData.videoDescription}
                    onChange={(e) => handleInputChange("videoDescription", e.target.value)}
                    className="bg-muted border-border min-h-[100px]"
                  />
                </div>

                {/* Use Image in Intro Toggle */}
                <div className="flex items-center space-x-2">
                  <Switch
                    id="useImageInIntro"
                    checked={formData.useImageInIntro}
                    onCheckedChange={(checked) => handleInputChange("useImageInIntro", checked)}
                  />
                  <Label htmlFor="useImageInIntro">Use image in intro</Label>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* First Resizer */}
        <div
          className="w-1 bg-border hover:bg-purple-500/50 cursor-col-resize transition-colors duration-200 flex-shrink-0"
          onMouseDown={() => handleMouseDown(0)}
        />

        {/* Middle Panel - Video/Image Preview */}
        <div
          className="border-r border-border overflow-y-auto flex flex-col"
          style={{
            width: `${middleWidth}%`,
            scrollbarWidth: "thin",
            scrollbarColor: "rgb(147 51 234 / 0.5) transparent",
          }}
        >
          {/* Tab Navigation */}
          <div className="border-b border-border">
            <div className="flex">
              <button
                onClick={() => setActiveTab("video")}
                className={`px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === "video"
                    ? "text-purple-400 border-b-2 border-purple-400 bg-purple-500/5"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                }`}
              >
                Video Preview
              </button>
              <button
                onClick={() => setActiveTab("image")}
                className={`px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === "image"
                    ? "text-purple-400 border-b-2 border-purple-400 bg-purple-500/5"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                }`}
              >
                Image Preview
              </button>
            </div>
          </div>

          <div className="flex-1 p-6">
            <div className="h-full flex items-center justify-center">
              {activeTab === "video" ? (
                <div
                  className="bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-border max-w-full max-h-full"
                  style={{
                    aspectRatio: `${formData.width}/${formData.height}`,
                    width: "auto",
                    height: "70vh",
                  }}
                >
                  <div className="text-center">
                    <Play className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                    <p className="text-muted-foreground">Video preview will appear here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Generate a video to see preview
                    </p>
                  </div>
                </div>
              ) : (
                <div
                  className="bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-border max-w-full max-h-full"
                  style={{
                    aspectRatio: `${formData.width}/${formData.height}`,
                    width: "auto",
                    height: "70vh",
                  }}
                >
                  <div className="text-center">
                    <svg
                      className="w-16 h-16 mx-auto mb-4 text-purple-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    <p className="text-muted-foreground">Image preview will appear here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Generate a video to see image preview
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Generate Button and Social Icons at bottom of preview column */}
          <div className="p-6 border-t border-border space-y-4">
            <Button
              onClick={handleGenerate}
              className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-purple-500/25 transition-all duration-200"
              style={{ transform: "scale(1)", transition: "transform 0.2s ease" }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "scale(1.02)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "scale(1)";
              }}
              size="lg"
            >
              <Play className="w-5 h-5 mr-2" />
              Generate Video
            </Button>

            {/* Social Media Icons */}
            <div className="flex justify-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
              >
                <Download className="h-3 w-3 text-purple-400" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
              >
                <Instagram className="h-3 w-3 text-purple-400" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
              >
                <XIcon className="h-3 w-3 text-purple-400" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
              >
                <Youtube className="h-3 w-3 text-purple-400" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 rounded-full bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 transition-all duration-200"
              >
                <TikTokIcon className="h-3 w-3 text-purple-400" />
              </Button>
            </div>
          </div>
        </div>

        {/* Second Resizer */}
        <div
          className="w-1 bg-border hover:bg-purple-500/50 cursor-col-resize transition-colors duration-200 flex-shrink-0"
          onMouseDown={() => handleMouseDown(1)}
        />

        {/* Right Panel - Audio Files */}
        <div
          className="overflow-y-auto"
          style={{
            width: `${rightWidth}%`,
            scrollbarWidth: "thin",
            scrollbarColor: "rgb(147 51 234 / 0.5) transparent",
          }}
        >
          <div className="p-6">
            <h3 className="text-lg font-semibold text-purple-400 mb-4">Generated Audio Files</h3>

            {/* Table Header */}
            <div className="grid grid-cols-2 gap-4 mb-4 pb-3 border-b border-border">
              <div className="text-sm font-semibold text-purple-400">Transcript</div>
              <div className="text-sm font-semibold text-purple-400">Audio File</div>
            </div>

            {/* Table Content */}
            <div className="space-y-4">
              {audioFiles.map((file, index) => (
                <div key={file.id} className="grid grid-cols-2 gap-4">
                  {/* Transcript Column */}
                  <div className="p-4 bg-muted/30 rounded-lg border border-border/50">
                    <p className="text-sm text-foreground leading-relaxed">
                      {index % 4 === 0 &&
                        "This is a sample transcript for the generated audio content. It shows what was spoken in the audio file and provides context for the generated speech."}
                      {index % 4 === 1 &&
                        "Another example transcript showing different content that might be generated from your video source. This demonstrates varied speech patterns."}
                      {index % 4 === 2 &&
                        "Here's a third variation of transcript text to demonstrate how different audio files would have unique content and speaking styles."}
                      {index % 4 === 3 &&
                        "Final sample transcript showing how the text content varies across different generated audio files with distinct messaging."}
                    </p>
                  </div>

                  {/* Audio File Column */}
                  <div className="p-4 bg-muted rounded-lg border border-border hover:bg-muted/80 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 min-w-0">
                        <Volume2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{file.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {file.duration} • {file.size}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 flex-shrink-0">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-purple-400 hover:text-purple-300 h-8 w-8 p-0"
                        >
                          <Play className="w-3 h-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-purple-400 hover:text-purple-300 h-8 w-8 p-0"
                        >
                          <Download className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        /* Cross-browser scrollbar styles */
        ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }

        ::-webkit-scrollbar-track {
          background: transparent;
        }

        ::-webkit-scrollbar-thumb {
          background: rgb(147 51 234 / 0.5);
          border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgb(147 51 234 / 0.7);
        }

        /* Firefox scrollbar */
        * {
          scrollbar-width: thin;
          scrollbar-color: rgb(147 51 234 / 0.5) transparent;
        }
      `}</style>
    </div>
  );
}
