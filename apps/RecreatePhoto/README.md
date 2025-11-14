# RecreatePhoto

An iOS app that helps you rediscover and recreate photos from your past by notifying you when you're near locations where you previously took pictures.

## Concept

RecreatePhoto implements "serendipitous rephotography" - the app passively tracks your location and compares it to the locations of your existing photos. When you wander near a spot where you once took a photo, it surfaces those memories and provides tools to help you recreate the same shot.

## Features

### Core Functionality

- **Passive Location Tracking**: Uses efficient location tracking (while the app is in use) to monitor your position
- **Photo Library Indexing**: Scans your photo library for geotagged images and builds a spatial index
- **Proximity Notifications**: Alerts you when you're near places where you took photos in the past
- **Photo Clustering**: Groups nearby photos into "spots" for easier browsing
- **Recreate Mode**: Camera view with adjustable opacity overlay to help you align and recreate original shots

### User Interface

- **Nearby Tab**: Shows photos and photo spots near your current location
- **Map Tab**: Displays all your geotagged photos on an interactive map
- **Settings Tab**: Configure proximity radius, filters, notifications, and other preferences

### Privacy & Permissions

- **Local-Only Processing**: All photo indexing and location matching happens on-device
- **Granular Permissions**: Only requires "When In Use" location access
- **User Control**: Configurable filters, notification settings, and tracking controls

## Architecture

### Core Components

#### Models (`Models/`)
- **PhotoLocation**: Represents a photo with its GPS coordinates and metadata
- **PhotoSpot**: Cluster of photos taken at similar locations
- **PhotoIndexCache**: Persistent storage for indexed photo data

#### Services (`Services/`)
- **PhotoIndexer**: Manages photo library access, indexing, and spatial queries
- **LocationManager**: Handles location tracking and permissions
- **NotificationManager**: Schedules local notifications for nearby photos
- **AppSettings**: User preferences and app configuration

#### Utilities (`Utilities/`)
- **SpatialIndex**: Grid-based spatial index for efficient proximity queries

#### Views (`Views/`)
- **ContentView**: Main tab-based navigation
- **NearbyPhotosView**: Shows photos near current location
- **MapView**: Interactive map of all geotagged photos
- **SpotDetailView**: Details of a photo spot with gallery
- **PhotoDetailView**: Individual photo viewer with recreate option
- **RecreatePhotoView**: Camera view with overlay functionality
- **SettingsView**: User preferences and configuration
- **ThumbnailView**: Photo thumbnail component

### Key Technologies

- **SwiftUI**: Modern declarative UI framework
- **PhotoKit**: Access to user's photo library
- **CoreLocation**: Location tracking and geofencing
- **AVFoundation**: Camera capture for recreate mode
- **UserNotifications**: Local notifications for nearby photos
- **Combine**: Reactive state management

## Setup Instructions

### Prerequisites

- Xcode 14.0 or later
- iOS 16.0+ deployment target
- Apple Developer account (for device testing)

### Opening the Project

Since this is a standalone iOS app created outside of a standard Xcode project:

1. Open Xcode
2. Create a new iOS App project:
   - Product Name: `RecreatePhoto`
   - Interface: SwiftUI
   - Language: Swift
3. Replace the default project files with the files from this repository:
   - Copy all files from `RecreatePhoto/` into your Xcode project
   - Ensure `Info.plist` is included and properly configured
4. Update the bundle identifier to match your developer account
5. Build and run on a physical device (recommended, as location features work best on device)

### Required Permissions

The app requires the following permissions (configured in `Info.plist`):

- **Photo Library Access** (`NSPhotoLibraryUsageDescription`): To read photo locations
- **Location When In Use** (`NSLocationWhenInUseUsageDescription`): To find nearby photos
- **Camera Access** (`NSCameraUsageDescription`): To recreate photos with overlay

### First Launch

On first launch, the app will:

1. Request photo library access
2. Request location permission
3. Request notification permission
4. Begin indexing your photo library (may take a few minutes for large libraries)

## Usage

### Finding Nearby Photos

1. Grant the required permissions
2. Wait for photo indexing to complete
3. Navigate to the "Nearby" tab
4. The app will show photos taken within your configured proximity radius
5. Tap on a spot to see all photos from that location

### Recreating a Photo

1. From the Nearby view or Map view, tap on a photo
2. Tap "Recreate This Photo"
3. Use the camera view with overlay:
   - Adjust overlay opacity with the slider
   - Toggle overlay visibility with the eye icon
   - Align your camera to match the overlay
   - Tap the capture button to take the new photo

### Configuring Settings

In the Settings tab, you can:

- **Proximity Radius**: How close you need to be to trigger "nearby" (20-200m)
- **Cluster Radius**: How close photos need to be to group together (5-50m)
- **Favorites Only**: Only show favorite photos
- **Minimum Photo Age**: Only show photos older than X months/years
- **Overlay Opacity**: Default opacity for camera overlay
- **Notifications**: Enable/disable and set cooldown period
- **Reindex**: Force a full reindex of your photo library

## Implementation Details

### Spatial Indexing

Photos are indexed using a grid-based spatial index that divides the earth's surface into cells. This allows for efficient O(1) proximity queries without scanning the entire photo library.

### Location Tracking

The app uses "When In Use" location tracking rather than "Always" background tracking to:
- Preserve battery life
- Respect user privacy
- Comply with iOS background execution policies

### Notification Logic

Notifications are throttled using a configurable cooldown period (default 24 hours) to prevent notification spam. The app tracks which spots have been notified recently and skips them until the cooldown expires.

### Photo Library Changes

The app registers as a `PHPhotoLibraryChangeObserver` to automatically reindex when photos are added or modified.

## Limitations & Future Enhancements

### Current Limitations

- **No AR Alignment**: The complex AR-based framing assistance has been omitted for simplicity
- **Basic Overlay**: Camera overlay is simple opacity-based, without edge detection or feature matching
- **When In Use Only**: Location tracking only works while app is open (no background geofencing)
- **No Photo Pairing**: Recreated photos aren't automatically linked to originals

### Potential Enhancements

- ARKit integration for advanced alignment assistance
- Machine learning-based scene matching
- Background region monitoring for specific photo spots
- Before/after photo pairing and timeline view
- Photo spot sharing and social features
- Manual geotagging for photos without location data
- Export recreated photo pairs as videos or animations

## Privacy Considerations

- All photo indexing happens on-device
- Location data never leaves the device
- No analytics or tracking
- User controls all permissions and can disable features at any time
- Photo library access is read-only

## License

This is a demonstration project. Adapt as needed for your own use.

## Technical Requirements

- iOS 16.0+
- iPhone (optimized for iPhone)
- Camera (required for recreate functionality)
- Geotagged photos (app only works with photos that have location metadata)

## Credits

Concept: Serendipitous rephotography and location-based photo discovery
Implementation: SwiftUI, PhotoKit, CoreLocation, AVFoundation
