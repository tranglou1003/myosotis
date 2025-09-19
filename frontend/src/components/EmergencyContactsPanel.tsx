import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { EmergencyContact, EmergencyContactPayload } from '../types/user';
import { getEmergencyContacts, createEmergencyContact, updateEmergencyContact, deleteEmergencyContact } from '../api/user';
import { EmergencyContactModal, ConfirmDeleteModal } from './index';

interface EmergencyContactsPanelProps {
  userId: number | undefined;
}

export const EmergencyContactsPanel: React.FC<EmergencyContactsPanelProps> = ({ userId }) => {
  const { t } = useTranslation(['dashboard', 'common']);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [isLoadingContacts, setIsLoadingContacts] = useState(false);
  const [contactsError, setContactsError] = useState<string | null>(null);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [editingContact, setEditingContact] = useState<EmergencyContact | null>(null);
  const [deletingContact, setDeletingContact] = useState<EmergencyContact | null>(null);
  const [isSubmittingContact, setIsSubmittingContact] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setIsLoadingContacts(true);
    getEmergencyContacts(userId)
      .then(res => {
        setEmergencyContacts(res.data || []);
        setContactsError(null);
      })
      .catch(error => {
        setContactsError(error instanceof Error ? error.message : t('dashboard:emergencyContacts.errors.fetchFailed'));
      })
      .finally(() => setIsLoadingContacts(false));
  }, [userId, t]);

  const handleAddContact = () => {
    setEditingContact(null);
    setIsContactModalOpen(true);
  };

  const handleEditContact = (contact: EmergencyContact) => {
    setEditingContact(contact);
    setIsContactModalOpen(true);
  };

  const handleDeleteContact = (contact: EmergencyContact) => {
    setDeletingContact(contact);
    setIsDeleteModalOpen(true);
  };

  const handleSaveContact = async (payload: EmergencyContactPayload) => {
    if (!userId) return;
    setIsSubmittingContact(true);
    try {
      if (editingContact) {
        await updateEmergencyContact(editingContact.id, payload);
      } else {
        await createEmergencyContact(userId, payload);
      }
      const response = await getEmergencyContacts(userId);
      setEmergencyContacts(response.data || []);
      setIsContactModalOpen(false);
      setEditingContact(null);
    } finally {
      setIsSubmittingContact(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!userId || !deletingContact) return;
    setIsSubmittingContact(true);
    try {
      await deleteEmergencyContact(deletingContact.id);
      const response = await getEmergencyContacts(userId);
      setEmergencyContacts(response.data || []);
      setIsDeleteModalOpen(false);
      setDeletingContact(null);
    } finally {
      setIsSubmittingContact(false);
    }
  };

  return (
    <div className="p-4 lg:p-6 mb-4 lg:mb-6">
      <div className="flex items-center justify-between mb-4 lg:mb-6">
        <h3 className="text-lg lg:text-xl font-semibold text-[#333333]">{t('dashboard:emergencyContacts.title')}</h3>
        <button
          onClick={handleAddContact}
          className="bg-[#5A6DD0] text-white px-4 py-2 rounded-[12px] font-semibold hover:bg-[#5A6DD0]/90 transition-colors text-sm lg:text-base"
        >
          {t('dashboard:emergencyContacts.addContact')}
        </button>
      </div>
      {contactsError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-800">{contactsError}</span>
          </div>
        </div>
      )}
      {isLoadingContacts ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#5A6DD0]"></div>
          <span className="ml-3 text-gray-600">{t('dashboard:emergencyContacts.loading')}</span>
        </div>
      ) : emergencyContacts.length > 0 ? (
        <div className="space-y-4">
          {emergencyContacts.map((contact, index) => (
            <div key={contact.id || index} className="flex items-center justify-between p-4 rounded-[12px] border border-gray-100 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-[#5A6DD0]/10 rounded-full flex items-center justify-center">
                  <svg className="h-6 w-6 text-[#5A6DD0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-[#333333]">{contact.contact_name}</div>
                  <div className="text-[#888888]">{contact.relation}</div>
                  <div className="text-[#888888]">{contact.phone}</div>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => window.open(`tel:${contact.phone}`, '_self')}
                  className="bg-[#5A6DD0] text-white px-4 py-2 rounded-[8px] font-medium hover:bg-[#5A6DD0]/90 transition-colors"
                >
                  {t('dashboard:emergencyContacts.actions.call')}
                </button>
                {contact.email && (
                  <button
                    onClick={() => window.open(`mailto:${contact.email}`, '_self')}
                    className="bg-white border border-gray-300 text-[#333333] px-4 py-2 rounded-[8px] hover:bg-gray-50 transition-colors"
                  >
                    {t('dashboard:emergencyContacts.actions.email')}
                  </button>
                )}
                <button
                  onClick={() => handleEditContact(contact)}
                  className="bg-white border border-[#5A6DD0] text-[#5A6DD0] px-4 py-2 rounded-[8px] font-medium hover:bg-[#5A6DD0]/10 transition-colors"
                >
                  {t('dashboard:emergencyContacts.actions.edit')}
                </button>
                <button
                  onClick={() => handleDeleteContact(contact)}
                  className="bg-white border border-red-300 text-red-600 px-4 py-2 rounded-[8px] font-medium hover:bg-red-50 transition-colors"
                >
                  {t('dashboard:emergencyContacts.actions.delete')}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h4 className="text-lg font-semibold text-[#333333] mb-2">{t('dashboard:emergencyContacts.noContacts.title')}</h4>
          <p className="text-[#888888] mb-4">{t('dashboard:emergencyContacts.noContacts.subtitle')}</p>
          <button
            onClick={handleAddContact}
            className="bg-[#5A6DD0] text-white px-6 py-3 rounded-[12px] font-semibold hover:bg-[#5A6DD0]/90 transition-colors"
          >
            {t('dashboard:emergencyContacts.noContacts.addButton')}
          </button>
        </div>
      )}
      <EmergencyContactModal
        isOpen={isContactModalOpen}
        onClose={() => {
          setIsContactModalOpen(false);
          setEditingContact(null);
        }}
        onSave={handleSaveContact}
        contact={editingContact}
        isLoading={isSubmittingContact}
      />
      <ConfirmDeleteModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setDeletingContact(null);
        }}
        onConfirm={handleConfirmDelete}
        contactName={deletingContact?.contact_name || ''}
        isLoading={isSubmittingContact}
      />
    </div>
  );
};
