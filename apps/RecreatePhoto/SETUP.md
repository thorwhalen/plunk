# RecreatePhoto Setup Guide

This guide will help you set up the RecreatePhoto iOS app in Xcode.

## Quick Start

Since the source files are provided without an Xcode project file, you'll need to create a new Xcode project and import the source files.

### Step 1: Create New Xcode Project

1. Open Xcode
2. Select **File > New > Project**
3. Choose **iOS > App**
4. Configure the project:
   - **Product Name**: `RecreatePhoto`
   - **Team**: Your development team
   - **Organization Identifier**: Your reverse domain (e.g., `com.yourname`)
   - **Interface**: `SwiftUI`
   - **Language**: `Swift`
   - **Storage**: None (we're not using Core Data)
   - **Include Tests**: Optional
5. Choose a save location
6. Click **Create**

### Step 2: Import Source Files

1. In Finder, navigate to the `RecreatePhoto/RecreatePhoto/` folder from this repository
2. Select all the subdirectories (`App/`, `Models/`, `Services/`, `Views/`, `Utilities/`)
3. Drag them into your Xcode project navigator, dropping onto the `RecreatePhoto` folder
4. In the dialog that appears:
   - ✓ Check **Copy items if needed**
   - ✓ Select **Create groups**
   - ✓ Ensure the `RecreatePhoto` target is checked
   - Click **Finish**

### Step 3: Replace Info.plist

1. Delete the default `Info.plist` from your Xcode project (if it exists as a file)
2. Drag the `Info.plist` from this repository into your Xcode project
3. Ensure it's added to the `RecreatePhoto` target

### Step 4: Configure Build Settings

1. Select your project in the navigator
2. Select the `RecreatePhoto` target
3. Go to the **Info** tab
4. Verify the custom iOS target properties are present:
   - Privacy - Photo Library Usage Description
   - Privacy - Location When In Use Usage Description
   - Privacy - Camera Usage Description

If they're missing, add them manually with the descriptions from `Info.plist`.

### Step 5: Delete Default Files

Delete the following default files created by Xcode (if they exist):
- `ContentView.swift` (we have our own)
- `RecreatePhotoApp.swift` (if it was auto-generated differently)

### Step 6: Verify File Structure

Your project should now have this structure:

```
RecreatePhoto/
├── App/
│   └── RecreatePhotoApp.swift
├── Models/
│   └── PhotoLocation.swift
├── Services/
│   ├── PhotoIndexer.swift
│   ├── LocationManager.swift
│   ├── NotificationManager.swift
│   └── AppSettings.swift
├── Views/
│   ├── ContentView.swift
│   ├── NearbyPhotosView.swift
│   ├── MapView.swift
│   ├── SpotDetailView.swift
│   ├── PhotoDetailView.swift
│   ├── RecreatePhotoView.swift
│   ├── SettingsView.swift
│   └── Components/
│       └── ThumbnailView.swift
├── Utilities/
│   └── SpatialIndex.swift
├── Info.plist
└── Assets.xcassets/
```

### Step 7: Configure Deployment Target

1. Select your project in the navigator
2. Select the `RecreatePhoto` target
3. Go to **General** tab
4. Set **Minimum Deployments** to **iOS 16.0** or later

### Step 8: Build and Test

1. Select a simulator or connect a physical device
   - **Note**: For best results, use a **physical device** with real photos and location
2. Click the **Run** button (⌘R) or **Product > Run**
3. Xcode should compile without errors

## First Launch Testing

### Simulator Testing (Limited)

If testing in the simulator:
- Photo library will be empty (add sample photos with location data)
- Location can be simulated via **Debug > Simulate Location**
- Notifications work but with limitations
- Camera will not work (simulator doesn't have a camera)

### Device Testing (Recommended)

1. Connect your iPhone via USB
2. Select it as the run destination
3. Build and run
4. On first launch, grant all permissions:
   - Photo Library Access
   - Location When In Use
   - Notifications
   - Camera (when entering recreate mode)
5. Wait for photo indexing to complete
6. Move around to test proximity features

## Troubleshooting

### Build Errors

**"No such module 'SwiftUI'"**
- Ensure iOS deployment target is 16.0+
- Clean build folder (⌘⇧K)

**Missing files**
- Verify all source files were imported correctly
- Check target membership (files should be part of RecreatePhoto target)

**Info.plist errors**
- Ensure Info.plist is in the project root
- Verify it's set as the Info.plist in Build Settings

### Runtime Errors

**Photo indexing fails**
- Grant photo library permission
- Check that your photo library has geotagged photos

**Location not updating**
- Grant location permission (When In Use)
- Ensure location services are enabled on device
- Try moving outdoors for better GPS signal

**No nearby photos found**
- Check proximity radius in Settings
- Verify you're actually near a geotagged photo location
- Check that filters (favorites only, minimum age) aren't too restrictive

**Camera doesn't work**
- Grant camera permission
- Use a physical device (simulator doesn't have camera)

**Notifications not appearing**
- Grant notification permission
- Check notification settings in app
- Ensure cooldown period has passed

## Development Tips

### Testing Nearby Photos

1. Add test photos with known locations using the Photos app
2. Use Xcode's location simulation to teleport to those coordinates
3. Adjust proximity radius to make testing easier (increase to 200m)

### Debugging Photo Indexing

Add breakpoints or print statements in:
- `PhotoIndexer.indexPhotoLibrary()`
- `SpatialIndex.findNearby()`

### Simulating Background Behavior

Since the app uses "When In Use" location:
- Background location updates are limited
- Test by keeping app in foreground or recently backgrounded
- For true background, would need "Always" permission (not implemented)

### Testing Notifications

- Lower cooldown period to 1 hour for faster testing
- Clear notification history by reinstalling app
- Check notification center for delivered notifications

## Code Signing

For device deployment:

1. Select your project in the navigator
2. Select the `RecreatePhoto` target
3. Go to **Signing & Capabilities**
4. Select your **Team**
5. Xcode will automatically manage provisioning profiles

## App Store Preparation (Future)

When ready to submit:

1. Add app icon to `Assets.xcassets/AppIcon`
2. Configure bundle version and build number
3. Add privacy manifest if required by Apple
4. Test on multiple devices and iOS versions
5. Create App Store listing
6. Submit for review

## Additional Configuration

### Custom App Icon

1. Design icon in required sizes (20-1024pt)
2. Add to `Assets.xcassets/AppIcon.appiconset/`
3. Use an icon generator tool or create manually

### Launch Screen

The app uses the default SwiftUI launch screen. To customize:

1. Create a `LaunchScreen.storyboard`
2. Add to project and set in Build Settings

### Localization

To add support for multiple languages:

1. Select project in navigator
2. Go to **Info** tab
3. Add languages under **Localizations**
4. Create `.strings` files for each language

## Performance Optimization

For large photo libraries (>10,000 photos):

- Indexing may take several minutes on first launch
- Consider showing a more detailed progress view
- Consider indexing in smaller batches
- May want to add an index rebuild option in Settings

## Privacy Compliance

Ensure your App Store listing explains:
- Why you need photo access (to find locations)
- Why you need location access (to find nearby photos)
- Why you need camera access (to recreate photos)
- That all processing is on-device
- That no data is collected or transmitted

## Next Steps

Once the app is running:

1. Take photos with location services enabled
2. Wait for indexing to complete
3. Return to locations where you took photos
4. Test the recreate feature
5. Experiment with settings and filters
6. Provide feedback or contribute improvements

## Getting Help

If you encounter issues:

1. Check this setup guide
2. Review the README.md for app overview
3. Review ARCHITECTURE.md for technical details
4. Check Xcode console for error messages
5. Ensure all permissions are granted
6. Try on a physical device instead of simulator

## Contributing

To modify or extend the app:

1. Review ARCHITECTURE.md to understand the design
2. Add new features in appropriate directories
3. Follow existing code style and patterns
4. Test on physical devices when possible
5. Update documentation as needed

## Known Issues

- Simulator camera limitations (expected)
- Background location limited to "When In Use" (by design)
- Large photo libraries may slow indexing (optimization opportunity)
- No AR alignment features (simplified implementation)

## Resources

- [Apple PhotoKit Documentation](https://developer.apple.com/documentation/photokit)
- [Core Location Guide](https://developer.apple.com/documentation/corelocation)
- [AVFoundation Camera Guide](https://developer.apple.com/documentation/avfoundation/cameras_and_media_capture)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)

---

**Happy rephotography! 📸**
