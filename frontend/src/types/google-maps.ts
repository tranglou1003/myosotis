export interface GoogleMapsLocation {
  lat: number;
  lng: number;
}

export interface PlaceResult {
  place_id: string;
  name: string;
  formatted_address: string;
  geometry: {
    location: GoogleMapsLocation;
  };
  photos?: {
    photo_reference: string;
  }[];
  rating?: number;
  types: string[];
}

export interface MemoryLocation {
  id?: string;
  place_id: string;
  name: string;
  address: string;
  coordinates: GoogleMapsLocation;
  memory_note?: string;
  visit_date?: string;
  photos?: string[];
  created_at?: string;
}

export interface GoogleStreetViewPanorama {
  pano: string;
  location: GoogleMapsLocation;
  description: string;
}

export interface MapSearchFilters {
  query?: string;
  location?: GoogleMapsLocation;
  radius?: number;
  type?: string;
}
