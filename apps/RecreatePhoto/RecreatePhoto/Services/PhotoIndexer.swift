//
//  PhotoIndexer.swift
//  RecreatePhoto
//
//  Handles photo library access, indexing, and spatial queries
//

import Foundation
import Photos
import CoreLocation
import Combine

class PhotoIndexer: ObservableObject {
    @Published var indexedPhotos: [PhotoLocation] = []
    @Published var isIndexing = false
    @Published var authorizationStatus: PHAuthorizationStatus = .notDetermined
    @Published var indexProgress: Double = 0.0

    private var spatialIndex: SpatialIndex?
    private let cacheURL: URL
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Setup cache directory
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        cacheURL = documentsPath.appendingPathComponent("photo_index_cache.json")

        // Load cached index
        loadCachedIndex()

        // Check current authorization status
        authorizationStatus = PHPhotoLibrary.authorizationStatus(for: .readWrite)

        // Register for photo library changes
        PHPhotoLibrary.shared().register(self)
    }

    deinit {
        PHPhotoLibrary.shared().unregisterChangeObserver(self)
    }

    // MARK: - Permission Handling

    func requestPhotoLibraryAccess() {
        PHPhotoLibrary.requestAuthorization(for: .readWrite) { [weak self] status in
            DispatchQueue.main.async {
                self?.authorizationStatus = status
                if status == .authorized || status == .limited {
                    self?.indexPhotoLibrary()
                }
            }
        }
    }

    // MARK: - Indexing

    func indexPhotoLibrary(forceReindex: Bool = false) {
        guard authorizationStatus == .authorized || authorizationStatus == .limited else {
            print("Photo library access not authorized")
            return
        }

        guard !isIndexing else {
            print("Already indexing")
            return
        }

        isIndexing = true
        indexProgress = 0.0

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let fetchOptions = PHFetchOptions()
            fetchOptions.includeAssetSourceTypes = [.typeUserLibrary, .typeiTunesSynced, .typeCloudShared]

            let allPhotos = PHAsset.fetchAssets(with: .image, options: fetchOptions)
            let totalCount = allPhotos.count

            var photoLocations: [PhotoLocation] = []

            allPhotos.enumerateObjects { asset, index, _ in
                // Only index photos with valid location data
                if let location = asset.location,
                   location.coordinate.latitude != 0 || location.coordinate.longitude != 0 {
                    let photoLocation = PhotoLocation(asset: asset)
                    photoLocations.append(photoLocation)
                }

                // Update progress
                if index % 100 == 0 {
                    DispatchQueue.main.async {
                        self.indexProgress = Double(index) / Double(totalCount)
                    }
                }
            }

            // Build spatial index
            let spatialIndex = SpatialIndex(photos: photoLocations)

            // Update on main thread
            DispatchQueue.main.async {
                self.indexedPhotos = photoLocations
                self.spatialIndex = spatialIndex
                self.isIndexing = false
                self.indexProgress = 1.0

                // Save to cache
                self.saveCachedIndex()

                print("Indexed \(photoLocations.count) photos with location data out of \(totalCount) total")
            }
        }
    }

    // MARK: - Spatial Queries

    func getPhotosNear(location: CLLocation, radius: Double, filters: PhotoFilters? = nil) -> [PhotoLocation] {
        guard let spatialIndex = spatialIndex else {
            return []
        }

        var results = spatialIndex.findNearby(location: location, radiusMeters: radius)

        // Apply filters
        if let filters = filters {
            results = applyFilters(to: results, filters: filters)
        }

        return results
    }

    func getSpotsNear(location: CLLocation, radius: Double, clusterRadius: Double = 15.0, filters: PhotoFilters? = nil) -> [PhotoSpot] {
        var photos = getPhotosNear(location: location, radius: radius, filters: filters)

        // Cluster photos into spots
        return clusterPhotosIntoSpots(photos, clusterRadius: clusterRadius)
    }

    // MARK: - Filtering

    private func applyFilters(to photos: [PhotoLocation], filters: PhotoFilters) -> [PhotoLocation] {
        var filtered = photos

        // Filter by favorites only
        if filters.favoritesOnly {
            filtered = filtered.filter { $0.isFavorite }
        }

        // Filter by minimum age
        if let minAge = filters.minimumAgeMonths {
            let cutoffDate = Calendar.current.date(byAdding: .month, value: -minAge, to: Date()) ?? Date()
            filtered = filtered.filter { $0.captureDate < cutoffDate }
        }

        return filtered
    }

    // MARK: - Clustering

    private func clusterPhotosIntoSpots(_ photos: [PhotoLocation], clusterRadius: Double) -> [PhotoSpot] {
        var spots: [PhotoSpot] = []
        var remainingPhotos = photos

        while !remainingPhotos.isEmpty {
            let anchor = remainingPhotos.removeFirst()
            let anchorLocation = anchor.location

            // Find all photos within cluster radius of anchor
            var spotPhotos = [anchor]
            remainingPhotos = remainingPhotos.filter { photo in
                let distance = anchorLocation.distance(from: photo.location)
                if distance <= clusterRadius {
                    spotPhotos.append(photo)
                    return false
                }
                return true
            }

            // Calculate center of cluster
            let centerLat = spotPhotos.map { $0.latitude }.reduce(0, +) / Double(spotPhotos.count)
            let centerLon = spotPhotos.map { $0.longitude }.reduce(0, +) / Double(spotPhotos.count)
            let center = CLLocationCoordinate2D(latitude: centerLat, longitude: centerLon)

            let spot = PhotoSpot(centerCoordinate: center, photos: spotPhotos, radius: clusterRadius)
            spots.append(spot)
        }

        return spots.sorted { $0.photos.count > $1.photos.count }
    }

    // MARK: - Caching

    private func loadCachedIndex() {
        guard FileManager.default.fileExists(atPath: cacheURL.path) else {
            return
        }

        do {
            let data = try Data(contentsOf: cacheURL)
            let cache = try JSONDecoder().decode(PhotoIndexCache.self, from: data)

            // Check if cache is recent (less than 7 days old)
            if cache.version == PhotoIndexCache.currentVersion,
               Date().timeIntervalSince(cache.lastUpdated) < 7 * 24 * 3600 {
                self.indexedPhotos = cache.photos
                self.spatialIndex = SpatialIndex(photos: cache.photos)
                print("Loaded \(cache.photos.count) photos from cache")
            }
        } catch {
            print("Error loading cached index: \(error)")
        }
    }

    private func saveCachedIndex() {
        let cache = PhotoIndexCache(
            photos: indexedPhotos,
            lastUpdated: Date(),
            version: PhotoIndexCache.currentVersion
        )

        do {
            let data = try JSONEncoder().encode(cache)
            try data.write(to: cacheURL)
            print("Saved index cache with \(indexedPhotos.count) photos")
        } catch {
            print("Error saving index cache: \(error)")
        }
    }

    // MARK: - Photo Asset Retrieval

    func getAsset(for photoLocation: PhotoLocation) -> PHAsset? {
        let fetchResult = PHAsset.fetchAssets(withLocalIdentifiers: [photoLocation.id], options: nil)
        return fetchResult.firstObject
    }
}

// MARK: - PHPhotoLibraryChangeObserver

extension PhotoIndexer: PHPhotoLibraryChangeObserver {
    func photoLibraryDidChange(_ changeInstance: PHChange) {
        // Re-index when photos change (debounced)
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            self?.indexPhotoLibrary()
        }
    }
}

// MARK: - Supporting Types

struct PhotoFilters {
    var favoritesOnly: Bool = false
    var minimumAgeMonths: Int? = nil
    var albumNames: [String]? = nil
}
