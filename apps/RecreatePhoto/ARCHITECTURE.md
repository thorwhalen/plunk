# RecreatePhoto Architecture

## Overview

RecreatePhoto is built using SwiftUI with a modular, service-oriented architecture. The app follows Apple's recommended patterns for iOS development while maintaining clear separation of concerns.

## Project Structure

```
RecreatePhoto/
├── RecreatePhoto/
│   ├── App/
│   │   └── RecreatePhotoApp.swift          # Main app entry point
│   ├── Models/
│   │   └── PhotoLocation.swift             # Data models (PhotoLocation, PhotoSpot, PhotoIndexCache)
│   ├── Services/
│   │   ├── PhotoIndexer.swift              # Photo library access and indexing
│   │   ├── LocationManager.swift           # Location tracking
│   │   ├── NotificationManager.swift       # Local notifications
│   │   └── AppSettings.swift               # User preferences
│   ├── Views/
│   │   ├── ContentView.swift               # Main tab navigation
│   │   ├── NearbyPhotosView.swift          # Nearby photos list
│   │   ├── MapView.swift                   # Photo map
│   │   ├── SpotDetailView.swift            # Photo spot details
│   │   ├── PhotoDetailView.swift           # Individual photo view
│   │   ├── RecreatePhotoView.swift         # Camera with overlay
│   │   ├── SettingsView.swift              # Settings panel
│   │   └── Components/
│   │       └── ThumbnailView.swift         # Photo thumbnail
│   ├── Utilities/
│   │   └── SpatialIndex.swift              # Spatial indexing
│   └── Info.plist                          # App configuration & permissions
├── README.md
├── ARCHITECTURE.md
└── .gitignore
```

## Core Services

### PhotoIndexer

**Responsibility**: Manages photo library access and builds/maintains a spatial index of geotagged photos.

**Key Features**:
- Requests photo library permissions
- Scans photo library for geotagged images
- Builds spatial index for fast proximity queries
- Caches index to disk for faster startup
- Monitors photo library changes via `PHPhotoLibraryChangeObserver`
- Provides filtering (favorites, age, albums)
- Clusters photos into "spots" based on proximity

**Performance Considerations**:
- Indexing happens on background queue
- Progress tracking for UI feedback
- Incremental updates when photos change
- 7-day cache expiration

### LocationManager

**Responsibility**: Handles location tracking and permissions.

**Key Features**:
- Requests "When In Use" location permission
- Tracks user location with 10m accuracy and 10m filter
- Provides current location to other components
- Manages tracking state (on/off)
- Implements notification cooldown logic

**iOS Background Limitations**:
- Only tracks when app is in use (foreground or recently backgrounded)
- No "Always" background tracking (battery and privacy conscious)
- No region monitoring or geofencing (simplified implementation)

### NotificationManager

**Responsibility**: Schedules local notifications when user is near photo locations.

**Key Features**:
- Requests notification permissions
- Schedules notifications for nearby photo spots
- Implements per-spot cooldown to prevent spam
- Persists notification history
- Handles notification tap actions

**Notification Logic**:
- Triggered when nearby photos found AND cooldown expired
- Default cooldown: 24 hours per spot
- Selects closest spot with most photos
- Immediate delivery (no scheduled trigger)

### AppSettings

**Responsibility**: Manages user preferences with persistence.

**Settings**:
- Proximity radius (20-200m)
- Cluster radius (5-50m)
- Favorites only filter
- Minimum photo age filter
- Notification enabled/disabled
- Notification cooldown period
- Camera overlay opacity

**Persistence**: Uses `UserDefaults` with Combine `@Published` properties.

## Data Models

### PhotoLocation

Represents a single geotagged photo with:
- Unique identifier (PHAsset localIdentifier)
- GPS coordinates (latitude, longitude)
- Capture date
- Metadata (album, favorite status, EXIF)

**Conforms to**: `Identifiable`, `Codable`

### PhotoSpot

Represents a cluster of photos at similar locations:
- Center coordinate (calculated from photo cluster)
- Array of PhotoLocation objects
- Cluster radius
- Computed properties (photo count, date range)

**Not persisted**: Generated on-demand from spatial queries

### PhotoIndexCache

Serializable cache structure:
- Array of PhotoLocation objects
- Last updated timestamp
- Version number (for schema migrations)

## Spatial Indexing Algorithm

### Grid-Based Approach

The `SpatialIndex` uses a simple grid-based approach:

1. **Grid Division**: Earth divided into cells (0.01° ≈ 1km)
2. **Hashing**: Each photo hashed to grid cell by lat/lon
3. **Proximity Query**:
   - Calculate center cell from query location
   - Check neighboring cells within radius
   - Filter candidates by exact distance
   - Sort by distance from query point

**Time Complexity**:
- Index build: O(n) where n = number of photos
- Proximity query: O(k) where k = photos in nearby cells
- Typically k << n for localized queries

**Space Complexity**: O(n)

### Clustering Algorithm

Photos are clustered into spots using a greedy approach:

1. Start with all nearby photos
2. Take first photo as cluster anchor
3. Find all photos within cluster radius
4. Remove clustered photos from remaining set
5. Repeat until all photos assigned
6. Sort spots by photo count (descending)

**Parameters**:
- Default cluster radius: 15m
- Configurable in settings (5-50m)

## View Architecture

### SwiftUI & Environment Objects

All services are injected as `@EnvironmentObject`:
- `PhotoIndexer`
- `LocationManager`
- `AppSettings`
- `NotificationManager`

This allows any view to access shared state without prop drilling.

### View Hierarchy

```
RecreatePhotoApp
└── ContentView (TabView)
    ├── NearbyPhotosView
    │   └── SpotDetailView
    │       └── PhotoDetailView
    │           └── RecreatePhotoView
    ├── MapView
    │   └── PhotoDetailView
    │       └── RecreatePhotoView
    └── SettingsView
```

### State Management

- **Local @State**: View-specific ephemeral state (UI toggles, selections)
- **@EnvironmentObject**: Shared app-wide state (services)
- **@Published**: Observable service properties
- **UserDefaults**: Persisted settings

## Camera & Overlay Implementation

### RecreatePhotoView

**Components**:
- `CameraManager`: ObservableObject that manages AVFoundation camera session
- `CameraPreview`: UIViewRepresentable wrapping AVCaptureVideoPreviewLayer
- SwiftUI overlay: Original photo with adjustable opacity

**Camera Setup**:
1. Check/request camera permission
2. Create AVCaptureSession
3. Add camera input (back wide-angle camera)
4. Add photo output (AVCapturePhotoOutput)
5. Create preview layer
6. Start session on background queue

**Capture Flow**:
1. User taps capture button
2. CameraManager captures photo via AVCapturePhotoOutput
3. Photo saved to library via UIImageWriteToSavedPhotosAlbum

**Simplified Approach**:
- No AR/alignment detection (would require Vision framework or ARKit)
- No edge detection or feature matching
- Simple opacity overlay for manual alignment
- User adjusts framing by eye

## Performance Optimizations

### Photo Indexing
- Background queue processing
- Batched enumeration (update progress every 100 photos)
- Disk caching with 7-day expiration
- Lazy loading of photo assets

### Spatial Queries
- Grid-based index for O(k) queries vs O(n) linear scan
- Pre-computed grid cells
- Distance filtering only on candidates

### UI Rendering
- Lazy loading of thumbnails
- Async image loading via PHImageManager
- Grid views instead of lists for better scrolling
- Conditional rendering based on auth status

## Privacy & Security

### On-Device Processing
- All photo indexing happens locally
- Location data never transmitted
- No analytics or tracking
- No third-party SDKs

### Permissions
- Photo library: Read-only access
- Location: When In Use only (not Always)
- Camera: Only when recreate mode active
- Notifications: User configurable

### Data Storage
- Photo index: Documents directory (user-accessible, backed up)
- Settings: UserDefaults
- Notification history: UserDefaults
- Original photos: Never copied or moved (accessed via PHAsset references)

## Testing Considerations

### Unit Testing Targets
- `SpatialIndex`: Grid hashing, proximity queries
- `PhotoIndexer`: Filtering logic, clustering algorithm
- `LocationManager`: Cooldown logic
- `NotificationManager`: History tracking, cooldown

### Integration Testing
- Photo library permissions flow
- Location permission flow
- End-to-end proximity detection
- Notification scheduling

### UI Testing
- Permission grant/deny flows
- Settings changes persist
- Photo recreation flow
- Map interaction

## Known Limitations

### Background Processing
- No background location tracking (design choice for privacy/battery)
- No region monitoring or geofencing
- Location only updated while app in use

### Photo Processing
- Only works with geotagged photos (no manual tagging)
- GPS accuracy depends on original photo metadata
- No EXIF focal length parsing (future enhancement)

### Camera Features
- No AR-based alignment (simplified implementation)
- No scene matching or similarity scoring
- No multi-lens support (always uses wide-angle)
- No zoom or focus controls

### Scalability
- Tested with ~10,000 photos
- Large libraries (>50,000) may see slower indexing
- Grid size may need tuning for global coverage
- In-memory index (no database)

## Future Architecture Improvements

### Potential Enhancements
1. **Core Data**: Replace in-memory index with persistent database
2. **Background Processing**: Use BackgroundTasks framework for periodic reindexing
3. **Vision Framework**: Add scene matching and alignment scoring
4. **ARKit**: Implement proper AR-based overlay with 3D positioning
5. **CloudKit**: Sync photo spots across devices
6. **WidgetKit**: Show nearby photos in home screen widget
7. **App Clips**: Lightweight experience for sharing spots
8. **Siri Shortcuts**: Voice-activated nearby photo lookup

### Scalability Improvements
1. **Hierarchical Grid**: Multi-resolution spatial index
2. **Lazy Loading**: Only load photos for visible map region
3. **Incremental Indexing**: Track last indexed photo, only scan new ones
4. **Batch Processing**: Process photos in chunks with yield points

## Dependencies

### Apple Frameworks
- **SwiftUI**: UI framework
- **PhotoKit**: Photo library access
- **CoreLocation**: Location services
- **AVFoundation**: Camera capture
- **UserNotifications**: Local notifications
- **MapKit**: Map display
- **Combine**: Reactive programming

### Third-Party Dependencies
None - pure Apple frameworks for maximum compatibility and minimal attack surface.

## Build Configuration

### Minimum Requirements
- iOS 16.0+
- Xcode 14.0+
- Swift 5.7+

### Capabilities Required
- Photo Library access
- Location Services (When In Use)
- Camera
- User Notifications

### App Store Considerations
- Privacy manifest required (privacy usage descriptions)
- Photo library access justification
- Location usage justification
- Camera usage justification

## Deployment

### Debug Build
- Location simulation in Xcode
- Photo library simulation with sample photos
- Notification testing in simulator (limited)

### Release Build
- Physical device required for full testing
- Location services only work on device
- Photo library needs real photos with location data
- App Store review will check permission justifications

## Maintenance & Monitoring

### Crash Reporting
- Consider adding crash reporting (Crashlytics, Sentry)
- Monitor PHPhotoLibrary errors
- Track location permission denials

### Analytics (Optional)
- Feature usage (if privacy-preserving analytics added)
- Performance metrics (indexing time, query latency)
- User engagement (recreated photos count)

### Update Strategy
- Cache version bumping for schema changes
- Migration logic for settings format changes
- Graceful degradation for permission denials
