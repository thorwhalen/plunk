//
//  MapView.swift
//  RecreatePhoto
//
//  Shows all indexed photos on a map
//

import SwiftUI
import MapKit

struct MapView: View {
    @EnvironmentObject var photoIndexer: PhotoIndexer
    @EnvironmentObject var locationManager: LocationManager
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
        span: MKCoordinateSpan(latitudeDelta: 0.5, longitudeDelta: 0.5)
    )
    @State private var selectedPhoto: PhotoLocation?

    var body: some View {
        NavigationView {
            ZStack {
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: photoIndexer.indexedPhotos) { photo in
                    MapAnnotation(coordinate: photo.coordinate) {
                        Button {
                            selectedPhoto = photo
                        } label: {
                            Circle()
                                .fill(photo.isFavorite ? Color.red : Color.blue)
                                .frame(width: 12, height: 12)
                                .overlay(
                                    Circle()
                                        .stroke(Color.white, lineWidth: 2)
                                )
                        }
                    }
                }
                .ignoresSafeArea()

                VStack {
                    Spacer()

                    HStack {
                        Spacer()

                        VStack(spacing: 12) {
                            Button {
                                centerOnUserLocation()
                            } label: {
                                Image(systemName: "location.fill")
                                    .padding()
                                    .background(Color.white)
                                    .clipShape(Circle())
                                    .shadow(radius: 4)
                            }

                            Text("\(photoIndexer.indexedPhotos.count) photos")
                                .font(.caption)
                                .padding(8)
                                .background(Color.white)
                                .cornerRadius(8)
                                .shadow(radius: 4)
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Photo Map")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                centerOnUserLocation()
            }
            .sheet(item: $selectedPhoto) { photo in
                PhotoDetailView(photo: photo)
            }
        }
    }

    private func centerOnUserLocation() {
        if let location = locationManager.currentLocation {
            region = MKCoordinateRegion(
                center: location.coordinate,
                span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
            )
        }
    }
}

#Preview {
    MapView()
        .environmentObject(PhotoIndexer())
        .environmentObject(LocationManager())
}
