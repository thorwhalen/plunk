//
//  SpotDetailView.swift
//  RecreatePhoto
//
//  Shows details of a photo spot with all photos taken there
//

import SwiftUI
import Photos
import MapKit

struct SpotDetailView: View {
    let spot: PhotoSpot
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @State private var selectedPhoto: PhotoLocation?
    @State private var showingRecreateView = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Map showing spot location
                Map(coordinateRegion: .constant(MKCoordinateRegion(
                    center: spot.centerCoordinate,
                    span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
                )), annotationItems: [spot]) { spot in
                    MapMarker(coordinate: spot.centerCoordinate, tint: .blue)
                }
                .frame(height: 200)
                .cornerRadius(12)
                .padding(.horizontal)

                // Photos grid
                VStack(alignment: .leading, spacing: 12) {
                    Text("Photos at this location")
                        .font(.headline)
                        .padding(.horizontal)

                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 8) {
                        ForEach(spot.photos) { photo in
                            if let asset = photoIndexer.getAsset(for: photo) {
                                Button {
                                    selectedPhoto = photo
                                } label: {
                                    ThumbnailView(asset: asset)
                                        .aspectRatio(1, contentMode: .fill)
                                        .cornerRadius(8)
                                }
                            }
                        }
                    }
                    .padding(.horizontal)
                }
            }
            .padding(.vertical)
        }
        .navigationTitle("Photo Spot")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $selectedPhoto) { photo in
            PhotoDetailView(photo: photo)
        }
    }
}

// MARK: - Photo Detail View

struct PhotoDetailView: View {
    let photo: PhotoLocation
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @Environment(\.dismiss) var dismiss
    @State private var showingRecreateView = false
    @State private var image: UIImage?

    var body: some View {
        NavigationView {
            VStack {
                if let image = image {
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                } else {
                    ProgressView()
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text(photo.captureDate.formatted(date: .long, time: .shortened))
                        .font(.headline)

                    if photo.isFavorite {
                        Label("Favorite", systemImage: "heart.fill")
                            .foregroundColor(.red)
                    }

                    Button {
                        showingRecreateView = true
                    } label: {
                        Label("Recreate This Photo", systemImage: "camera.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .padding(.top)
                }
                .padding()
            }
            .navigationTitle("Photo")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .onAppear {
                loadImage()
            }
            .fullScreenCover(isPresented: $showingRecreateView) {
                RecreatePhotoView(originalPhoto: photo, originalImage: image)
            }
        }
    }

    private func loadImage() {
        guard let asset = photoIndexer.getAsset(for: photo) else { return }

        let manager = PHImageManager.default()
        let options = PHImageRequestOptions()
        options.deliveryMode = .highQualityFormat
        options.isNetworkAccessAllowed = true

        manager.requestImage(
            for: asset,
            targetSize: CGSize(width: 1024, height: 1024),
            contentMode: .aspectFit,
            options: options
        ) { image, _ in
            self.image = image
        }
    }
}

#Preview {
    let samplePhoto = PhotoLocation(
        id: "sample",
        latitude: 37.7749,
        longitude: -122.4194,
        captureDate: Date(),
        albumName: nil,
        isFavorite: false,
        focalLength: nil,
        orientation: nil
    )

    let spot = PhotoSpot(
        centerCoordinate: samplePhoto.coordinate,
        photos: [samplePhoto],
        radius: 15.0
    )

    return SpotDetailView(spot: spot)
        .environmentObject(PhotoIndexer())
}
