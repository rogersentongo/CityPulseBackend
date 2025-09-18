# CityPulse Frontend Features Guide

## Overview
This document outlines all frontend features for the CityPulse React/Next.js application, featuring a sleek glass morphism design with dark/light mode toggle and mobile-first responsive experience.

---

## 🎨 Design System & Theme

### Visual Style
- **Theme Toggle**: Dark mode (default) and light mode with smooth transitions
- **Primary Style**: Sleek black themed modern UI with glass morphism effects
- **Glass Effects**: Glassy finishing on buttons, video borders, cards, modals
- **Color Palette**:
  - Dark mode: Deep blacks, grays, with accent colors
  - Light mode: Clean whites, light grays, maintaining glass effects
- **Typography**: Clean, modern font hierarchy optimized for mobile reading

### Glass Morphism Elements
- Semi-transparent backgrounds with backdrop blur
- Subtle borders with glass-like shine
- Frosted glass overlays for modals and dropdowns
- Glassy button effects with hover states
- Video player controls with glass styling

---

## 🎯 Core Frontend Features

### 1. User Simulation & Borough Selection
**Purpose**: Entry point with sleek onboarding experience.

**Components Required**:
- `UserSetup.tsx` - Glass-styled user ID input
- `BoroughSelector.tsx` - NYC borough selection with glass cards
- `WelcomeScreen.tsx` - Animated welcome interface

**Features**:
- Glass-styled input field with floating labels
- Borough selection with glass cards showing NYC imagery
- Smooth animations and transitions
- Persistent user state with Zustand + localStorage
- Mobile-first responsive layout
- Dark/light mode toggle in header

**API Integration**: None (provides parameters for other API calls)

**Mobile-First Design**:
- Large touch targets (min 44px)
- Thumb-friendly borough selection grid
- Swipe-friendly interactions
- Glass effects optimized for mobile performance

---

### 2. Main Video Feed (with Auto-Refresh & Rubber Band)
**Purpose**: Primary content discovery with smooth infinite scroll.

**Components Required**:
- `VideoFeed.tsx` - Main feed with auto-refresh logic
- `VideoCard.tsx` - Glass-bordered video cards
- `PullToRefresh.tsx` - Bouncy rubber band component
- `InfiniteScroll.tsx` - Smooth infinite scrolling

**Features**:
- Auto-refresh feed when user taste changes
- **Bouncy rubber band effect** at top/bottom of page
- Loading spinners with glass styling when fetching new videos
- Glass-bordered video cards with hover effects
- Pull-to-refresh functionality with rubber band animation
- Infinite scroll with smooth loading transitions
- Grid layout optimized for mobile viewing

**API Integration**:
- `GET /api/v1/feed` - Personalized feed with auto-refresh
- Polling mechanism for taste profile changes

**Mobile-First Features**:
- Single column feed optimized for mobile
- Touch-friendly video cards
- Optimized scroll performance
- Rubber band physics for natural feel

---

### 3. Video Playback
**Purpose**: Immersive video viewing with glass-styled controls.

**Components Required**:
- `VideoPlayer.tsx` - Custom player with glass controls
- `VideoModal.tsx` - Full-screen glass modal
- `GlassControls.tsx` - Translucent video controls

**Features**:
- Glass-styled video player controls
- Smooth modal transitions with glass backdrop
- Touch-optimized controls for mobile
- Responsive video scaling
- Custom scrub bar with glass styling
- Tap-to-play/pause on mobile

**API Integration**:
- Direct media URL usage from `/media` endpoint

**Mobile Experience**:
- Full-width video on mobile
- Gesture controls (tap, double-tap, swipe)
- Optimized loading for mobile networks
- Picture-in-picture consideration

---

### 4. Like Functionality (Glass Heart Animation)
**Purpose**: Engaging personalization with beautiful animations.

**Components Required**:
- `GlassLikeButton.tsx` - Animated glass heart button
- `LikeToast.tsx` - Glass-styled success notifications

**Features**:
- Glass-styled heart button with glow effects
- Smooth heart fill animation with particle effects
- Optimistic UI updates with instant feedback
- Glass toast notifications for success/error states
- Unlike functionality with reverse animation
- Haptic feedback on mobile devices

**API Integration**:
- `POST /api/v1/like` - Register likes with immediate UI response
- `DELETE /api/v1/like` - Unlike functionality

**Mobile Interactions**:
- Large touch target for easy tapping
- Vibration feedback on like
- Smooth animations optimized for mobile

---

### 5. Video Upload (Single Page Flow)
**Purpose**: Streamlined single-page upload experience.

**Components Required**:
- `UploadPage.tsx` - Complete single-page upload flow
- `GlassDropzone.tsx` - Glass-styled drag & drop area
- `UploadProgress.tsx` - Glass progress indicators

**Features**:
- **Single page upload flow** with step indicators
- Glass-styled file dropzone with hover effects
- Real-time upload progress with glass progress bars
- File validation with glass error messages
- Borough selection integrated in upload flow
- Preview functionality with glass overlay

**API Integration**:
- `POST /api/v1/upload` - Multipart file upload

**Mobile Upload Experience**:
- Camera integration for direct video capture
- Touch-friendly file selection
- Optimized for mobile upload speeds
- Glass loading states during processing

---

### 6. Ask NYC (Glass Q&A Interface)
**Purpose**: Beautiful AI-powered search experience.

**Components Required**:
- `AskNYC.tsx` - Glass-styled search interface
- `GlassSearchBar.tsx` - Translucent search input
- `ResponseCard.tsx` - Glass response cards
- `SourceVideos.tsx` - Glass source attribution

**Features**:
- Glass-styled search bar with floating placeholder
- AI responses in glass cards with smooth animations
- Source videos with glass borders and hover effects
- Query suggestions in glass dropdown
- Search history with glass list styling

**API Integration**:
- `POST /api/v1/ask` - Natural language queries
- `GET /api/v1/ask-suggestions` - Contextual suggestions

**Mobile Search**:
- Voice search integration consideration
- Keyboard-optimized input experience
- Touch-friendly suggestion selection

---

## 🚀 Enhanced Features

### 7. Theme Toggle System
**Components Required**:
- `ThemeToggle.tsx` - Animated dark/light mode switch
- `ThemeProvider.tsx` - Theme context management

**Features**:
- Smooth transition animations between themes
- Glass effects maintained in both modes
- System preference detection
- Persistent theme selection

### 8. User Taste Profile (Glass Dashboard)
**Components Required**:
- `GlassTasteProfile.tsx` - Translucent profile cards
- `TasteStats.tsx` - Glass-styled statistics

**Features**:
- Glass cards showing taste evolution
- Smooth data visualization with glass elements
- Privacy-conscious display with glass overlays

### 9. Recent Feed Toggle
**Components Required**:
- `FeedModeToggle.tsx` - Glass toggle switch

**Features**:
- Glass-styled toggle between personalized/recent
- Smooth mode transition animations

---

## 📱 Mobile-First Design Specifications

### Screen Sizes
- **Mobile**: 320px - 768px (primary focus)
- **Tablet**: 768px - 1024px (enhanced experience)
- **Desktop**: 1024px+ (optional optimizations)

### Mobile-Specific Features
- **Touch Targets**: Minimum 44px for all interactive elements
- **Thumb Navigation**: Bottom-positioned navigation tabs
- **Swipe Gestures**: Natural mobile interactions
- **Rubber Band Physics**: Bouncy scroll effects
- **Glass Performance**: Optimized backdrop-filter for mobile

### Glass Effects on Mobile
- Reduced blur intensity for performance
- Optimized backdrop-filter usage
- Fallback solid colors for older devices
- Hardware acceleration for smooth animations

---

## 🔧 Technical Architecture

### State Management (Zustand)
```typescript
interface AppState {
  // User state
  userId: string | null;
  selectedBorough: Borough | null;

  // Theme state
  theme: 'dark' | 'light';

  // Feed state
  videos: VideoResponse[];
  isLoading: boolean;
  hasMore: boolean;

  // Upload state
  uploadProgress: number;
  isUploading: boolean;
}
```

### Key Libraries
- **Next.js 14** - App Router framework
- **Zustand** - Lightweight state management
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **React Hook Form** - Form handling
- **SWR** - API data fetching and caching

### Glass Morphism Implementation
```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
}

.glass-dark {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

---

## 🌐 API Integration Setup

### Development Configuration
- **Frontend Port**: 3000 (Next.js dev server)
- **Backend Port**: 8000 (FastAPI server)
- **API Proxy**: Next.js API routes proxy to backend
- **CORS**: Already configured in backend for frontend access

### API Client Structure
```typescript
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';
```

---

## 🎭 Animation & Interaction Details

### Rubber Band Effect
- **Top Pull**: Elastic bounce when pulling down to refresh
- **Bottom Pull**: Rubber band stretch when reaching end of feed
- **Physics**: Natural spring animations with damping
- **Visual Feedback**: Glass spinner with elastic scaling

### Glass Transitions
- **Theme Switch**: Smooth color and blur transitions
- **Modal Open**: Glass backdrop fade-in with scale animation
- **Card Hover**: Subtle glass glow and lift effects
- **Button Press**: Glass surface ripple effects

### Mobile Gestures
- **Pull to Refresh**: Elastic top pull with spinner
- **Infinite Scroll**: Smooth bottom loading with rubber band
- **Video Interaction**: Tap to play, double-tap to like
- **Navigation**: Swipe gestures between sections

This comprehensive guide ensures a premium mobile-first experience with beautiful glass morphism design and responsive functionality.