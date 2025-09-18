// API Types matching backend models
export type Borough = "Manhattan" | "Brooklyn" | "Queens" | "Bronx" | "Staten Island";

export interface VideoResponse {
  video_id: string;
  media_url: string;
  title: string;
  description?: string;
  tags: string[];
  borough: Borough;
  created_at: string;
  uploaded_at?: string;
  duration_sec: number;
  user_liked?: boolean;
  like_count?: number;
}

export interface FeedResponse {
  videos: VideoResponse[];
  total_count: number;
  has_more: boolean;
}

export interface UploadResponse {
  video_id: string;
  media_url: string;
  borough: Borough;
  borough_source: "manual" | "gps";
  title: string;
  tags: string[];
  transcript: string;
}

export interface LikeResponse {
  ok: boolean;
  message: string;
}

export interface AskResponse {
  answer: string;
  sources: AskSource[];
  borough?: Borough;
}

export interface AskSource {
  video_id: string;
  title: string;
  created_at: string;
  relevance_score: number;
}

export interface UserTasteProfile {
  user_id: string;
  likes_count: number;
  has_taste_profile: boolean;
  last_updated: string | null;
  embedding_dimensions: number;
  embedding_magnitude?: number;
  embedding_mean?: number;
  embedding_std?: number;
}

// Request types
export interface LikeRequest {
  user_id: string;
  video_id: string;
}

export interface AskRequest {
  query: string;
  borough?: Borough;
  window_hours?: number;
}

export interface FeedParams {
  borough: Borough;
  user_id: string;
  limit?: number;
  skip?: number;
  since_hours?: number;
}

// Constants
export const VALID_BOROUGHS: Borough[] = [
  "Manhattan",
  "Brooklyn",
  "Queens",
  "Bronx",
  "Staten Island"
];

export const BOROUGH_COLORS = {
  Manhattan: "#1E40AF",
  Brooklyn: "#EA580C",
  Queens: "#059669",
  Bronx: "#7C3AED",
  "Staten Island": "#DC2626"
} as const;