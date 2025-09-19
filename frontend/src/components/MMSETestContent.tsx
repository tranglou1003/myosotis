import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../features/auth/store';
import { getMMSEInfo, submitMMSETest, type MMSETestData, type MMSEAnswer, type MMSETestResult } from '../api/mmse';
import DashboardHeader from './DashboardHeader';
import { useTranslation } from 'react-i18next';

const getMediaUrl = (url: string): string => {
  if (url.startsWith('http')) {
    return url; 
  }
  const baseUrl = import.meta.env.VITE_API_URL
  return `${baseUrl}${url}`;
};

export default function MMSETestContent() {
  const { t } = useTranslation('mmse');
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [testData, setTestData] = useState<MMSETestData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<MMSEAnswer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testComplete, setTestComplete] = useState(false);
  const [testResult, setTestResult] = useState<MMSETestResult | null>(null);

  useEffect(() => {
    fetchTestData();
  }, [t]);

  useEffect(() => {
    if (!testData) return;
    
    const existingAnswer = answers.find(
      a => a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex
    );
    
    if (existingAnswer) {
      const question = testData.sections[currentSectionIndex]?.questions[currentQuestionIndex];
      if (question?.type === 'multi-select') {
        if (Array.isArray(existingAnswer.answer)) {
          setSelectedOptions(existingAnswer.answer);
        } else {
          setSelectedOptions(existingAnswer.answer.split(',').filter(v => v.length > 0));
        }
        setCurrentAnswer('');
      } else {
        setCurrentAnswer(Array.isArray(existingAnswer.answer) ? existingAnswer.answer[0] || '' : existingAnswer.answer);
        setSelectedOptions([]);
      }
    } else {
      setCurrentAnswer('');
      setSelectedOptions([]);
    }
  }, [currentSectionIndex, currentQuestionIndex, answers, testData]);

  useEffect(() => {
    if (!testData || !currentAnswer.trim()) return;
    
    const question = testData.sections[currentSectionIndex]?.questions[currentQuestionIndex];
    if (!question) return;
    if (question.type !== 'text' && question.type !== 'number') return;

    const timeoutId = setTimeout(() => {
      const newAnswer: MMSEAnswer = {
        section_index: currentSectionIndex,
        question_index: currentQuestionIndex,
        answer: currentAnswer
      };

      setAnswers(prev => {
        const filtered = prev.filter(
          a => !(a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex)
        );
        return [...filtered, newAnswer];
      });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [currentAnswer, currentSectionIndex, currentQuestionIndex, testData]);

  const fetchTestData = async () => {
    try {
      setIsLoading(true);
      const response = await getMMSEInfo();
      setTestData(response.data);
    } catch (error) {
      console.error('Failed to fetch MMSE test data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getCurrentQuestion = () => {
    if (!testData) return null;
    return testData.sections[currentSectionIndex]?.questions[currentQuestionIndex];
  };

  const getCurrentSection = () => {
    if (!testData) return null;
    return testData.sections[currentSectionIndex];
  };

  const getTotalQuestions = () => {
    if (!testData) return 0;
    return testData.sections.reduce((total, section) => total + section.questions.length, 0);
  };

  const getCurrentQuestionNumber = () => {
    if (!testData) return 0;
    let count = 0;
    for (let i = 0; i < currentSectionIndex; i++) {
      count += testData.sections[i].questions.length;
    }
    return count + currentQuestionIndex + 1;
  };

  const handleAnswerChange = (value: string) => {
    setCurrentAnswer(value);
    setSelectedOptions([value]);
    
    setTimeout(() => {
      const question = getCurrentQuestion();
      if (!question) return;

      const newAnswer: MMSEAnswer = {
        section_index: currentSectionIndex,
        question_index: currentQuestionIndex,
        answer: value
      };

      setAnswers(prev => {
        const filtered = prev.filter(
          a => !(a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex)
        );
        return [...filtered, newAnswer];
      });
    }, 0);
  };

  const handleMultiSelectChange = (value: string) => {
    const newSelectedOptions = selectedOptions.includes(value)
      ? selectedOptions.filter(v => v !== value)
      : [...selectedOptions, value];
    
    setSelectedOptions(newSelectedOptions);
    
    setTimeout(() => {
      const question = getCurrentQuestion();
      if (!question) return;

      const newAnswer: MMSEAnswer = {
        section_index: currentSectionIndex,
        question_index: currentQuestionIndex,
        answer: newSelectedOptions
      };

      setAnswers(prev => {
        const filtered = prev.filter(
          a => !(a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex)
        );
        return [...filtered, newAnswer];
      });
    }, 0);
  };

  const saveCurrentAnswer = () => {
    const question = getCurrentQuestion();
    if (!question) return;

    const answerValue = question.type === 'multi-select' 
      ? selectedOptions 
      : currentAnswer;   

    const newAnswer: MMSEAnswer = {
      section_index: currentSectionIndex,
      question_index: currentQuestionIndex,
      answer: answerValue
    };

    setAnswers(prev => {
      const filtered = prev.filter(
        a => !(a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex)
      );
      return [...filtered, newAnswer];
    });
  };

  const handleNext = () => {
    saveCurrentAnswer();
    
    if (!testData) return;

    const currentSection = testData.sections[currentSectionIndex];
    
    if (currentQuestionIndex < currentSection.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else if (currentSectionIndex < testData.sections.length - 1) {
      setCurrentSectionIndex(prev => prev + 1);
      setCurrentQuestionIndex(0);
    } else {
      handleSubmitTest();
      return;
    }

    setCurrentAnswer('');
    setSelectedOptions([]);
  };

  const handlePrevious = () => {
    saveCurrentAnswer();
    
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    } else if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
      const prevSection = testData?.sections[currentSectionIndex - 1];
      if (prevSection) {
        setCurrentQuestionIndex(prevSection.questions.length - 1);
      }
    }
    
    setCurrentAnswer('');
    setSelectedOptions([]);
  };

  const handleSubmitTest = async () => {
    if (!user?.id) return;

    try {
      setIsSubmitting(true);
      saveCurrentAnswer();

      setTimeout(async () => {
        try {
          const finalAnswers = [...answers];
          
          const currentQuestion = getCurrentQuestion();
          if (currentQuestion) {
            const answerValue = currentQuestion.type === 'multi-select' 
              ? selectedOptions 
              : currentAnswer;   

            const currentAnswerExists = finalAnswers.some(
              a => a.section_index === currentSectionIndex && a.question_index === currentQuestionIndex
            );

            if (!currentAnswerExists && ((typeof answerValue === 'string' && answerValue.trim()) || (Array.isArray(answerValue) && answerValue.length > 0))) {
              finalAnswers.push({
                section_index: currentSectionIndex,
                question_index: currentQuestionIndex,
                answer: answerValue
              });
            }
          }

          const payload = {
            user_id: user.id,
            answers: finalAnswers
          };

          const result = await submitMMSETest(payload);
          setTestResult(result.data);
          setTestComplete(true);
        } catch (error) {
          console.error('Failed to submit test:', error);
          setIsSubmitting(false);
        }
      }, 100);
      
    } catch (error) {
      console.error('Failed to submit test:', error);
      setIsSubmitting(false);
    }
  };

  const renderQuestion = () => {
    const question = getCurrentQuestion();
    if (!question) return null;

    const commonInputClass = "w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-lg bg-white transition-colors";

    switch (question.type) {
      case 'select':
        return (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <label key={option.value} className="flex items-center space-x-3 cursor-pointer p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-indigo-300 transition-colors">
                <input
                  type="radio"
                  name="answer"
                  value={option.value}
                  checked={currentAnswer === option.value}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  className="w-5 h-5 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-lg flex-1">{option.label}</span>
                {option.media && (
                  <img src={getMediaUrl(option.media.url)} alt={option.media.description} className="w-16 h-16 object-cover rounded-lg" />
                )}
              </label>
            ))}
          </div>
        );

      case 'multi-select':
        return (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <label key={option.value} className="flex items-center space-x-3 cursor-pointer p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-indigo-300 transition-colors">
                <input
                  type="checkbox"
                  value={option.value}
                  checked={selectedOptions.includes(option.value)}
                  onChange={(e) => handleMultiSelectChange(e.target.value)}
                  className="w-5 h-5 text-indigo-600 focus:ring-indigo-500 rounded"
                />
                <span className="text-lg flex-1">{option.label}</span>
                {option.media && (
                  <img src={getMediaUrl(option.media.url)} alt={option.media.description} className="w-16 h-16 object-cover rounded-lg" />
                )}
              </label>
            ))}
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            value={currentAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            placeholder={question.placeholder || t('testContent.placeholders.enterAnswer')}
            className={commonInputClass}
          />
        );

      case 'text':
        return (
          <input
            type="text"
            value={currentAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            placeholder={question.placeholder || t('testContent.placeholders.enterAnswer')}
            className={commonInputClass}
          />
        );

      default:
        return null;
    }
  };

  const isAnswerValid = () => {
    const question = getCurrentQuestion();
    if (!question) return false;

    if (question.type === 'multi-select') {
      return selectedOptions.length > 0;
    }
    return currentAnswer.trim() !== '';
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      
      if (target.tagName === 'INPUT' && (target as HTMLInputElement).type === 'text' || (target as HTMLInputElement).type === 'number') {
        if (event.key !== 'Enter') {
          return;
        }
      }
      
      if (target.tagName === 'TEXTAREA') {
        return;
      }

      if (isSubmitting) {
        return;
      }

      if (event.key === 'Enter') {
        event.preventDefault();
        const question = getCurrentQuestion();
        if (!question) return;
        
        const isValid = question.type === 'multi-select' 
          ? selectedOptions.length > 0 
          : currentAnswer.trim() !== '';
          
        if (isValid) {
          handleNext();
        } else {
        }
      } else if (event.key === 'Backspace') {
        event.preventDefault();
        const isFirstQuestion = currentSectionIndex === 0 && currentQuestionIndex === 0;
        if (!isFirstQuestion) {
          handlePrevious();
        } else {
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentSectionIndex, currentQuestionIndex, isSubmitting, currentAnswer, selectedOptions]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <DashboardHeader 
          title={t('testContent.title')} 
          description={t('testContent.subtitle')}
        />
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">{t('testContent.loading')}</p>
          </div>
        </div>
      </div>
    );
  }

  if (testComplete && testResult) {
    const { data: result } = testResult;
    const scorePercentage = Math.round(result.percentage);
    const completedDate = new Date(result.completed_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    const getScoreColor = (percentage: number): [string, string, string] => {
      if (percentage >= 89) return ['text-green-600', 'bg-green-50', 'border-green-200'];
      if (percentage >= 70) return ['text-yellow-600', 'bg-yellow-50', 'border-yellow-200'];
      return ['text-red-600', 'bg-red-50', 'border-red-200'];
    };

    const [textColor, bgColor, borderColor] = getScoreColor(scorePercentage);

    return (
      <div className="space-y-6">
        <DashboardHeader 
          title={t('testContent.results.title')} 
          description={t('testContent.results.subtitle')}
        />
        
        {/* Results Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 px-8 py-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">{t('testContent.results.testCompletedSuccessfully')}</h2>
                <p className="text-indigo-100">{t('testContent.results.completedOn', { date: completedDate })}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">{result.total_score}/{result.max_score}</div>
                <div className="text-indigo-100">{t('testContent.results.totalScore')}</div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div className="text-center">
                <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${bgColor} ${borderColor} border-2 mb-4`}>
                  <span className={`text-2xl font-bold ${textColor}`}>{scorePercentage}%</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('testContent.results.details.scorePercentage')}</h3>
                <p className="text-gray-600">{t('testContent.results.details.yourPerformance')}</p>
              </div>

              <div className="text-center">
                <div className="bg-indigo-50 text-indigo-800 px-6 py-4 rounded-lg mb-4 border border-indigo-200">
                  <div className="text-xl font-semibold">{result.interpretation.level}</div>
                  <div className="text-sm text-indigo-600 mt-1">{t('testContent.results.details.scoreRange')} {result.interpretation.score_range}</div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('testContent.results.details.assessmentResult')}</h3>
                <p className="text-gray-600">{t('testContent.results.details.basedOnResponses')}</p>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">{t('testContent.results.details.testDetails')}</h3>
              <div className="grid sm:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="text-sm text-gray-600 mb-1">{t('testContent.results.details.assessmentId')}</div>
                  <div className="font-semibold text-gray-900">#{result.assessment_id}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="text-sm text-gray-600 mb-1">{t('testContent.results.details.questionsAnswered')}</div>
                  <div className="font-semibold text-gray-900">{getTotalQuestions()} {t('testContent.results.details.questions')}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="text-sm text-gray-600 mb-1">{t('testContent.results.details.maximumPossibleScore')}</div>
                  <div className="font-semibold text-gray-900">{result.max_score} {t('testContent.results.details.points')}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="text-sm text-gray-600 mb-1">{t('testContent.results.details.dataStatus')}</div>
                  <div className="font-semibold text-green-600">
                    {result.saved_to_database ? t('testContent.results.details.successfullySaved') : t('testContent.results.details.notSaved')}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="border-t border-gray-200 pt-8 mt-8">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => navigate('/dashboard/mmse-history')}
                  className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  {t('testContent.results.buttons.viewTestHistory')}
                </button>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="px-8 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011 1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  {t('testContent.results.buttons.returnToDashboard')}
                </button>
                <button
                  onClick={() => window.location.reload()}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {t('testContent.results.buttons.takeTestAgain')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!testData) {
    return (
      <div className="space-y-6">
        <DashboardHeader 
          title={t('testContent.title')} 
          description={t('testContent.subtitle')}
        />
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <p className="text-lg text-gray-600 mb-4">{t('testContent.failedToLoad')}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {t('testContent.backToDashboard')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const question = getCurrentQuestion();
  const section = getCurrentSection();
  const isFirstQuestion = currentSectionIndex === 0 && currentQuestionIndex === 0;
  const isLastQuestion = currentSectionIndex === testData.sections.length - 1 && 
                         currentQuestionIndex === testData.sections[currentSectionIndex].questions.length - 1;
  const progressPercentage = (getCurrentQuestionNumber() / getTotalQuestions()) * 100;

  return (
    <div className="space-y-6">
      <DashboardHeader 
        title={t('testContent.title')} 
        description={t('testContent.question', { current: getCurrentQuestionNumber(), total: getTotalQuestions() })}
      />

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between text-sm text-gray-600 mb-3">
          <span>{t('testContent.progress')}</span>
          <span>{Math.round(progressPercentage)}% {t('testContent.complete')}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-indigo-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Section Info */}
      {section && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{section.title}</h2>
          <p className="text-gray-600 mb-4">{section.description}</p>
          {section.instruction && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <p className="text-indigo-700 font-medium">{section.instruction}</p>
            </div>
          )}
          
          {section.media && section.media.length > 0 && (
            <div className="mt-6 space-y-4">
              {section.media.map((media, index: number) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  {media.type === 'audio' && (
                    <div>
                      <p className="text-sm text-gray-600 mb-3">{media.description}</p>
                      <audio controls className="w-full">
                        <source src={getMediaUrl(media.url)} type="audio/mpeg" />
                        {t('testContent.audioNotSupported')}
                      </audio>
                    </div>
                  )}
                  {media.type === 'image' && (
                    <div>
                      <p className="text-sm text-gray-600 mb-3">{media.description}</p>
                      <img 
                        src={getMediaUrl(media.url)} 
                        alt={media.description}
                        className="max-w-md mx-auto rounded-lg shadow-md"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Question */}
      {question && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {question.media && question.media.length > 0 && (
            <div className="mb-8 space-y-4">
              {question.media.map((media, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  {media.type === 'audio' && (
                    <audio controls className="w-full">
                      <source src={getMediaUrl(media.url)} type="audio/mpeg" />
                      {t('testContent.audioNotSupported')}
                    </audio>
                  )}
                  {media.type === 'image' && (
                    <img 
                      src={getMediaUrl(media.url)} 
                      alt={media.description}
                      className="max-w-md mx-auto rounded-lg shadow-md"
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          <h3 className="text-2xl font-semibold text-gray-900 mb-8">{question.text}</h3>

          <div className="mb-8">
            {renderQuestion()}
          </div>

          <div className="flex justify-between pt-6 border-t border-gray-200">
            <button
              onClick={handlePrevious}
              disabled={isFirstQuestion}
              className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
                isFirstQuestion
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-600 text-white hover:bg-gray-700'
              }`}
            >
              <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              {t('testContent.navigation.previous')}
            </button>

            <button
              onClick={handleNext}
              disabled={!isAnswerValid() || isSubmitting}
              className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
                !isAnswerValid() || isSubmitting
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('testContent.navigation.submitting')}
                </>
              ) : (
                <>
                  {isLastQuestion ? t('testContent.navigation.submit') : t('testContent.navigation.next')}
                  <svg className="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
