import React, { useEffect, useRef, useState } from 'react';
import type { GoogleMapsLocation, PlaceResult, MemoryLocation } from '../types/google-maps';

interface GoogleMapComponentProps {
  center: GoogleMapsLocation;
  zoom?: number;
  onLocationSelect?: (location: GoogleMapsLocation) => void;
  onPlaceSelect?: (place: PlaceResult) => void;
  markers?: MemoryLocation[];
  showStreetView?: boolean;
  searchQuery?: string;
  className?: string;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
declare global {
  interface Window {
    google: any;
    initGoogleMaps: () => void;
  }
}

export const GoogleMapComponent: React.FC<GoogleMapComponentProps> = ({
  center,
  zoom = 15,
  onLocationSelect,
  onPlaceSelect,
  markers = [],
  showStreetView = false,
  searchQuery,
  className = "w-full h-96"
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const streetViewRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [placesService, setPlacesService] = useState<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const initializeMap = () => {
      if (!window.google || !mapRef.current) return;

      const mapInstance = new window.google.maps.Map(mapRef.current, {
        center,
        zoom,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
      });

      setMap(mapInstance);
      setPlacesService(new window.google.maps.places.PlacesService(mapInstance));

      // Add click listener for location selection
      if (onLocationSelect) {
        mapInstance.addListener('click', (event: any) => {
          onLocationSelect({
            lat: event.latLng.lat(),
            lng: event.latLng.lng(),
          });
        });
      }

      if (showStreetView && streetViewRef.current) {
        const streetViewInstance = new window.google.maps.StreetViewPanorama(
          streetViewRef.current,
          {
            position: center,
            pov: { heading: 34, pitch: 10 },
            addressControl: true,
            showRoadLabels: true,
          }
        );
        mapInstance.setStreetView(streetViewInstance);
      }

      setIsLoaded(true);
    };

    if (window.google) {
      initializeMap();
    } else {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${import.meta.env.VITE_GOOGLE_MAP_API}&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = initializeMap;
      document.head.appendChild(script);

      return () => {
        if (document.head.contains(script)) {
          document.head.removeChild(script);
        }
      };
    }
  }, [center, zoom, showStreetView, onLocationSelect]);

  useEffect(() => {
    if (map && isLoaded) {
      map.setCenter(center);
      map.setZoom(zoom);
    }
  }, [map, center, zoom, isLoaded]);

  useEffect(() => {
    if (!map || !placesService || !searchQuery) return;

    const request = {
      query: searchQuery,
      location: center,
      radius: 5000,
    };

    placesService.textSearch(request, (results: PlaceResult[], status: any) => {
      if (status === window.google.maps.places.PlacesServiceStatus.OK && results) {
        results.forEach((place) => {
          const marker = new window.google.maps.Marker({
            position: place.geometry.location,
            map,
            title: place.name,
            icon: {
              url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
              scaledSize: new window.google.maps.Size(32, 32),
            },
          });

          marker.addListener('click', () => {
            if (onPlaceSelect) {
              onPlaceSelect(place);
            }
          });
        });

        if (results.length > 0) {
          const bounds = new window.google.maps.LatLngBounds();
          results.forEach((place) => {
            bounds.extend(place.geometry.location);
          });
          map.fitBounds(bounds);
        }
      }
    });
  }, [searchQuery, map, placesService, center, onPlaceSelect]);

  useEffect(() => {
    if (!map || !isLoaded) return;

    markers.forEach((marker) => {
      const mapMarker = new window.google.maps.Marker({
        position: marker.coordinates,
        map,
        title: marker.name,
        icon: {
          url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
          scaledSize: new window.google.maps.Size(32, 32),
        },
      });

      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div class="p-2">
            <h3 class="font-semibold text-lg">${marker.name}</h3>
            <p class="text-sm text-gray-600">${marker.address}</p>
            ${marker.memory_note ? `<p class="text-sm mt-1 italic">${marker.memory_note}</p>` : ''}
          </div>
        `,
      });

      mapMarker.addListener('click', () => {
        infoWindow.open(map, mapMarker);
      });
    });
  }, [markers, map, isLoaded]);

  return (
    <div className={`relative ${className}`}>
      <div ref={mapRef} className="w-full h-full rounded-lg" />
      {showStreetView && (
        <div 
          ref={streetViewRef} 
          className="absolute top-0 right-0 w-1/2 h-2/3 border-2 border-white rounded-lg shadow-lg"
        />
      )}
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
};
