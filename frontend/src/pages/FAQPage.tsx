import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface FAQItem {
  id: string;
  category: string;
  question: string;
  answer: string;
}

export default function FAQPage() {
  const { t } = useTranslation(['faq']);
  const [searchTerm, setSearchTerm] = useState('');
  const [openAccordion, setOpenAccordion] = useState<string | null>(null);

  
  const faqCategories = [
    'memoryAssessment',
    'nutritionSleep', 
    'communicationPatient',
    'emergencyDifficult',
    'memoryCognitive',
    'dailyCare',
    'communicationSupport',
    'safetyEmergency',
    'familySupport',
    'appRelated'
  ];

  
  const faqData: FAQItem[] = [];
  
  faqCategories.forEach(categoryKey => {
    const categoryTitle = t(`categories.${categoryKey}.title`);
    const questions = t(`categories.${categoryKey}.questions`, { returnObjects: true }) as Array<{question: string, answer: string}>;
    
    if (Array.isArray(questions)) {
      questions.forEach((item, index) => {
        faqData.push({
          id: `${categoryKey}-${index + 1}`,
          category: categoryTitle,
          question: item.question,
          answer: item.answer
        });
      });
    }
  });

  
  const filteredFAQs = faqData.filter(faq =>
    faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  
  const groupedFAQs = filteredFAQs.reduce((acc, faq) => {
    if (!acc[faq.category]) {
      acc[faq.category] = [];
    }
    acc[faq.category].push(faq);
    return acc;
  }, {} as Record<string, FAQItem[]>);

  const toggleAccordion = (id: string) => {
    setOpenAccordion(openAccordion === id ? null : id);
  };

  return (
    <div className="max-w-8xl">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <img src="/faq.png" alt="FAQ" className="h-8 w-8" />
          <h1 className="text-3xl font-bold text-[#333333]">{t('title')}</h1>
        </div>
        <p className="text-[#888888] text-lg">
          {t('description')}
        </p>
      </div>

      <div className="mb-8">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder={t('searchPlaceholder')}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-[12px] focus:outline-none focus:ring-2 focus:ring-[#5A6DD0] focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(groupedFAQs).map(([category, faqs]) => (
          <div key={category} className="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-[#333333]">{category}</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {faqs.map((faq) => (
                <div key={faq.id} className="accordion-item">
                  <button
                    onClick={() => toggleAccordion(faq.id)}
                    className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-medium text-[#333333] pr-4">{faq.question}</span>
                    <svg
                      className={`h-5 w-5 text-gray-400 transform transition-transform ${
                        openAccordion === faq.id ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {openAccordion === faq.id && (
                    <div className="px-6 pb-4 pt-0">
                      <div className="text-[#666666] leading-relaxed bg-gray-50 p-4 rounded-[8px]">
                        {faq.answer}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {filteredFAQs.length === 0 && searchTerm && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="h-16 w-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-600 mb-2">{t('noResults.title')}</h3>
          <p className="text-gray-500">{t('noResults.description')}</p>
        </div>
      )}

      {/* Contact Support */}
      <div className="mt-12 bg-[#5A6DD0]/5 rounded-[16px] p-6 text-center">
        <h3 className="text-lg font-semibold text-[#333333] mb-2">{t('contactSupport.title')}</h3>
        <p className="text-[#666666] mb-4">
          {t('contactSupport.description')}
        </p>
        <button className="bg-[#5A6DD0] text-white px-6 py-3 rounded-[12px] font-medium hover:bg-[#5A6DD0]/90 transition-colors">
          {t('contactSupport.button')}
        </button>
      </div>
    </div>
  );
}