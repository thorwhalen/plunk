//
//  RecreatePhotoView.swift
//  RecreatePhoto
//
//  Camera view with overlay to help recreate a photo
//

import SwiftUI
import AVFoundation

struct RecreatePhotoView: View {
    let originalPhoto: PhotoLocation
    let originalImage: UIImage?

    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appSettings: AppSettings
    @StateObject private var cameraManager = CameraManager()
    @State private var overlayOpacity: Double
    @State private var showingControls = true

    init(originalPhoto: PhotoLocation, originalImage: UIImage?) {
        self.originalPhoto = originalPhoto
        self.originalImage = originalImage
        _overlayOpacity = State(initialValue: AppSettings().overlayOpacity)
    }

    var body: some View {
        ZStack {
            // Camera preview
            CameraPreview(cameraManager: cameraManager)
                .ignoresSafeArea()

            // Original photo overlay
            if let image = originalImage {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .opacity(overlayOpacity)
                    .allowsHitTesting(false)
            }

            // Controls
            VStack {
                // Top bar
                HStack {
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.black.opacity(0.5))
                            .clipShape(Circle())
                    }

                    Spacer()

                    Button {
                        withAnimation {
                            showingControls.toggle()
                        }
                    } label: {
                        Image(systemName: showingControls ? "eye.fill" : "eye.slash.fill")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.black.opacity(0.5))
                            .clipShape(Circle())
                    }
                }
                .padding()

                Spacer()

                // Bottom controls
                if showingControls {
                    VStack(spacing: 16) {
                        // Opacity slider
                        VStack(spacing: 8) {
                            Text("Overlay: \(Int(overlayOpacity * 100))%")
                                .font(.caption)
                                .foregroundColor(.white)

                            Slider(value: $overlayOpacity, in: 0.1...0.9)
                                .accentColor(.white)
                        }
                        .padding(.horizontal, 32)
                        .padding(.vertical, 12)
                        .background(Color.black.opacity(0.5))
                        .cornerRadius(12)

                        // Capture button
                        Button {
                            cameraManager.capturePhoto()
                        } label: {
                            Circle()
                                .strokeBorder(Color.white, lineWidth: 4)
                                .frame(width: 70, height: 70)
                                .overlay(
                                    Circle()
                                        .fill(Color.white)
                                        .frame(width: 60, height: 60)
                                )
                        }
                    }
                    .padding(.bottom, 32)
                }
            }
        }
        .onAppear {
            cameraManager.setupCamera()
        }
        .onDisappear {
            cameraManager.stopCamera()
        }
    }
}

// MARK: - Camera Manager

class CameraManager: NSObject, ObservableObject {
    @Published var previewLayer: AVCaptureVideoPreviewLayer?

    private var captureSession: AVCaptureSession?
    private var photoOutput: AVCapturePhotoOutput?

    func setupCamera() {
        checkPermissions()
    }

    func stopCamera() {
        captureSession?.stopRunning()
    }

    func capturePhoto() {
        guard let photoOutput = photoOutput else { return }

        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    private func checkPermissions() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            setupCaptureSession()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                if granted {
                    DispatchQueue.main.async {
                        self?.setupCaptureSession()
                    }
                }
            }
        default:
            break
        }
    }

    private func setupCaptureSession() {
        let session = AVCaptureSession()
        session.beginConfiguration()

        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else {
            return
        }

        if session.canAddInput(input) {
            session.addInput(input)
        }

        let output = AVCapturePhotoOutput()
        if session.canAddOutput(output) {
            session.addOutput(output)
            photoOutput = output
        }

        session.commitConfiguration()

        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill

        DispatchQueue.main.async {
            self.previewLayer = previewLayer
            self.captureSession = session
        }

        DispatchQueue.global(qos: .userInitiated).async {
            session.startRunning()
        }
    }
}

extension CameraManager: AVCapturePhotoCaptureDelegate {
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let data = photo.fileDataRepresentation(),
              let image = UIImage(data: data) else {
            return
        }

        // Save to photo library
        UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
    }
}

// MARK: - Camera Preview

struct CameraPreview: UIViewRepresentable {
    @ObservedObject var cameraManager: CameraManager

    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: .zero)
        view.backgroundColor = .black
        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {
        if let previewLayer = cameraManager.previewLayer {
            // Remove old layer if exists
            uiView.layer.sublayers?.forEach { $0.removeFromSuperlayer() }

            previewLayer.frame = uiView.bounds
            uiView.layer.addSublayer(previewLayer)
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

    return RecreatePhotoView(originalPhoto: samplePhoto, originalImage: nil)
        .environmentObject(AppSettings())
}
