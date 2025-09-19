import React, { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { GoogleMapComponent } from '../../components/GoogleMapComponent';
import DashboardHeader from '../../components/DashboardHeader';
import { useAuthStore } from '../../features/auth/store';
import { useMemoryMapStore } from '../../features/memory-map/store';
import type { GoogleMapsLocation, PlaceResult, MemoryLocation } from '../../types/google-maps';

export default function DashboardMemoryMapPage() {
  const { t } = useTranslation('memoryMap');
  const { isAuthenticated } = useAuthStore();
  const { savedLocations, currentMapCenter, addMemoryLocation, updateMapCenter } = useMemoryMapStore();
  
  const [currentLocation, setCurrentLocation] = useState<GoogleMapsLocation>(currentMapCenter);
  const [currentZoom, setCurrentZoom] = useState(15);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlace, setSelectedPlace] = useState<PlaceResult | null>(null);
  const [showStreetView, setShowStreetView] = useState(false);
  const [isAddingMemory, setIsAddingMemory] = useState(false);
  const [memoryNote, setMemoryNote] = useState('');

  useEffect(() => {
    updateMapCenter(currentLocation);
  }, [currentLocation, updateMapCenter]);

  useEffect(() => {
    if (!isAuthenticated) {
      setSelectedPlace(null);
      setMemoryNote('');
      setIsAddingMemory(false);
    }
  }, [isAuthenticated]);

  
  const getCurrentLocation = useCallback(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);

  const handleLocationSelect = useCallback((location: GoogleMapsLocation) => {
    setCurrentLocation(location);
  }, []);

  const handlePlaceSelect = useCallback((place: PlaceResult) => {
    setSelectedPlace(place);
    setCurrentLocation(place.geometry.location);
  }, []);

  const handleAddMemory = useCallback(() => {
    if (selectedPlace && memoryNote.trim()) {
      const newMemory: MemoryLocation = {
        id: Date.now().toString(),
        place_id: selectedPlace.place_id,
        name: selectedPlace.name,
        address: selectedPlace.formatted_address,
        coordinates: selectedPlace.geometry.location,
        memory_note: memoryNote,
        visit_date: new Date().toISOString().split('T')[0],
        created_at: new Date().toISOString(),
      };

      addMemoryLocation(newMemory);
      setMemoryNote('');
      setIsAddingMemory(false);
      setSelectedPlace(null);
    }
  }, [selectedPlace, memoryNote, addMemoryLocation]);

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
  }, []);

  const navigateToMemory = useCallback((location: MemoryLocation) => {
    setCurrentLocation(location.coordinates);
    setCurrentZoom(18);
    setSelectedPlace(null); 
  }, []);

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('title')} 
        description={t('description')}
      />

      <div className="space-y-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex flex-col lg:flex-row gap-4">
            <form onSubmit={handleSearch} className="flex-1">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {t('search.button')}
                </button>
              </div>
            </form>

            <div className="flex gap-2">
              <button
                onClick={getCurrentLocation}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {t('buttons.myLocation')}
              </button>
              <button
                onClick={() => setShowStreetView(!showStreetView)}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                  showStreetView 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {t('buttons.streetView')}
              </button>
            </div>
          </div>
        </div>


        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <GoogleMapComponent
            center={currentLocation}
            zoom={currentZoom}
            onLocationSelect={handleLocationSelect}
            onPlaceSelect={handlePlaceSelect}
            markers={savedLocations}
            showStreetView={showStreetView}
            searchQuery={searchQuery}
            className="w-full h-96 lg:h-[500px]"
          />
        </div>

        {selectedPlace && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">{selectedPlace.name}</h3>
                <p className="text-gray-600 mt-1">{selectedPlace.formatted_address}</p>
                {selectedPlace.rating && (
                  <div className="flex items-center mt-2">
                    <span className="text-yellow-500">★</span>
                    <span className="text-sm text-gray-600 ml-1">{t('place.rating', { rating: selectedPlace.rating })}</span>
                  </div>
                )}
              </div>
              <button
                onClick={() => setIsAddingMemory(true)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                {t('buttons.addMemory')}
              </button>
            </div>

            {isAddingMemory && (
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-2">{t('memory.addTitle')}</h4>
                <textarea
                  value={memoryNote}
                  onChange={(e) => setMemoryNote(e.target.value)}
                  placeholder={t('memory.placeholder')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={3}
                />
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={handleAddMemory}
                    disabled={!memoryNote.trim()}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {t('buttons.save')}
                  </button>
                  <button
                    onClick={() => {
                      setIsAddingMemory(false);
                      setMemoryNote('');
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    {t('buttons.cancel')}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {savedLocations.length > 0 && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">{t('memory.savedTitle')}</h3>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {savedLocations.map((location) => (
                <div key={location.id} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900">{location.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{location.address}</p>
                  {location.memory_note && (
                    <p className="text-sm text-purple-700 mt-2 italic">"{location.memory_note}"</p>
                  )}
                  {location.visit_date && (
                    <p className="text-xs text-gray-500 mt-2">{t('memory.visited', { date: location.visit_date })}</p>
                  )}
                  <button
                    onClick={() => navigateToMemory(location)}
                    className="mt-3 text-sm text-blue-600 hover:text-blue-800 underline"
                  >
                    {t('buttons.viewOnMap')}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
