import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../features/auth/store';
import { ProtectedRoute } from '../features/auth';
import { getMMSEChartData } from '../api/mmse';
import { LoadingSpinner } from '../components';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from 'recharts';

const SEVERITY_BANDS = [
  { min: 24, max: 27, label: 'mmse:historyPage.severityBands.noCognitive', color: '#10b981', bgColor: '#dcfce7' },
  { min: 20, max: 23, label: 'mmse:historyPage.severityBands.mildCognitive', color: '#f59e0b', bgColor: '#fef3c7' },
  { min: 14, max: 19, label: 'mmse:historyPage.severityBands.moderateCognitive', color: '#f97316', bgColor: '#fed7aa' },
  { min: 0, max: 13, label: 'mmse:historyPage.severityBands.severeCognitive', color: '#ef4444', bgColor: '#fecaca' }
];

interface TooltipPayload {
  payload: {
    test_date: string;
    total_score: number;
    max_score: number;
    percentage: number;
    interpretation: string;
    assessment_id: number;
    formattedDate: string;
    shortDate: string;
    scoreDifference?: number | null;
  };
}

interface ChartDataPoint {
  test_date: string;
  total_score: number;
  max_score: number;
  percentage: number;
  interpretation: string;
  assessment_id: number;
  formattedDate: string;
  shortDate: string;
  scoreDifference?: number | null;
}

interface RadarDataPoint {
  section: string;
  percentage: number;
}


const CustomTooltip = ({ active, payload, t }: { active?: boolean; payload?: TooltipPayload[]; t: (key: string, options?: Record<string, unknown>) => string }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const severityBand = SEVERITY_BANDS.find(band => 
      data.total_score >= band.min && data.total_score <= band.max
    );
    
    return (
      <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900 mb-2">{t('mmse:historyPage.tooltip.testNumber', { number: data.assessment_id })}</p>
        <p className="text-sm text-gray-600 mb-1">{t('mmse:historyPage.tooltip.date', { date: data.formattedDate })}</p>
        <p className="text-sm text-gray-600 mb-1">{t('mmse:historyPage.tooltip.score', { score: data.total_score, maxScore: data.max_score })}</p>
        <p className="text-sm text-gray-600 mb-1">{t('mmse:historyPage.tooltip.percentage', { percentage: data.percentage.toFixed(1) })}</p>
        {data.scoreDifference && Math.abs(data.scoreDifference) > 5 && (
          <p className={`text-sm font-medium ${data.scoreDifference > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {t('mmse:historyPage.tooltip.change', { change: data.scoreDifference > 0 ? `+${data.scoreDifference}` : data.scoreDifference })}
          </p>
        )}
        {severityBand && (
          <p className="text-sm font-medium" style={{ color: severityBand.color }}>
            {t(severityBand.label)}
          </p>
        )}
      </div>
    );
  }
  return null;
};

const CustomDot = (props: { cx?: number; cy?: number; payload?: { scoreDifference?: number | null; [key: string]: unknown } }) => {
  const { cx = 0, cy = 0 } = props;
  return <circle cx={cx} cy={cy} r={6} fill="#0891b2" strokeWidth={2} stroke="#0891b2" />;
};

export default function MMSEHistoryPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { t } = useTranslation(['mmse', 'common']);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [radarData, setRadarData] = useState<RadarDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchChartData = useCallback(async () => {
    if (!user?.id) return;

    try {
      setIsLoading(true);
      const response = await getMMSEChartData(user.id);
      
      if (response.success) {
        // Process line chart data - group by day and take latest test
        const lineData = response.data.line_chart.datasets[0];
        const processedData: { [date: string]: ChartDataPoint } = {};
        
        lineData.data.forEach((score, index) => {
          const testDate = response.data.line_chart.labels[index];
          const dateKey = new Date(testDate).toDateString();
          
          const dataPoint: ChartDataPoint = {
            test_date: testDate,
            total_score: score,
            max_score: response.data.line_chart.metadata.max_possible_score,
            percentage: lineData.percentages[index],
            interpretation: lineData.interpretations[index],
            assessment_id: lineData.assessment_ids[index],
            formattedDate: new Date(testDate).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            }),
            shortDate: new Date(testDate).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric'
            }),
          };
          
          // Keep the latest test of each day
          if (!processedData[dateKey] || new Date(testDate).getTime() > new Date(processedData[dateKey].test_date).getTime()) {
            processedData[dateKey] = dataPoint;
          }
        });
        
        // Convert to array and add score differences
        const sortedData = Object.values(processedData)
          .sort((a, b) => new Date(a.test_date).getTime() - new Date(b.test_date).getTime())
          .map((item, index, array) => {
            let scoreDifference = null;
            if (index > 0) {
              scoreDifference = item.total_score - array[index - 1].total_score;
            }
            return { ...item, scoreDifference };
          });
        
        setChartData(sortedData);
        
        // Process radar chart data for latest test
        const radarChart = response.data.radar_chart;
        const radarChartData: RadarDataPoint[] = radarChart.section_labels.map((label, index) => ({
          section: label.length > 20 ? label.substring(0, 20) + '...' : label,
          percentage: radarChart.section_percentages[index]
        }));
        
        setRadarData(radarChartData);
      }
    } catch (error) {
      console.error('Failed to fetch MMSE chart data:', error);
    } finally {
      setIsLoading(false);  
    }
  }, [user?.id]);

  useEffect(() => {
    if (user?.id) {
      fetchChartData();
    }
  }, [user?.id, fetchChartData]);

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner text={t('mmse:historyPage.loading')} />
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <div className="w-full h-full p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('mmse:historyPage.title')}</h1>
          <p className="text-gray-600">{t('mmse:historyPage.subtitle')}</p>
        </div>

        {chartData.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <div className="max-w-md mx-auto">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">{t('mmse:historyPage.noHistory.title')}</h2>
              <p className="text-gray-600 mb-6">{t('mmse:historyPage.noHistory.subtitle')}</p>
              <button
                onClick={() => navigate('/mmse-test')}
                className="bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
              >
                {t('mmse:historyPage.noHistory.takeFirstTest')}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Score Trend Chart */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{t('mmse:historyPage.trendAnalysis.title')}</h2>
                <p className="text-gray-600 text-sm">{t('mmse:historyPage.trendAnalysis.subtitle')}</p>
              </div>

              {/* Severity Legend */}
              <div className="mb-6">
                <div className="flex flex-wrap gap-4 text-sm">
                  {SEVERITY_BANDS.map((band) => (
                    <div key={band.label} className="flex items-center gap-2">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: band.color }}
                      ></div>
                      <span className="text-gray-700">
                        {t(band.label)} ({band.min}-{band.max === 27 ? '27' : band.max})
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="h-96 w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={chartData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    
                    <ReferenceLine y={24} stroke="#10b981" strokeDasharray="5 5" strokeOpacity={0.7} />
                    <ReferenceLine y={20} stroke="#f59e0b" strokeDasharray="5 5" strokeOpacity={0.7} />
                    <ReferenceLine y={14} stroke="#f97316" strokeDasharray="5 5" strokeOpacity={0.7} />
                    
                    <XAxis 
                      dataKey="shortDate"
                      tick={{ fontSize: 12 }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                      interval={0}
                    />
                    <YAxis 
                      domain={[0, 27]}
                      tick={{ fontSize: 12 }}
                      label={{ value: t('mmse:historyPage.chart.yAxisLabel'), angle: -90, position: 'insideLeft' }}
                    />
                    
                    <Tooltip content={<CustomTooltip t={t} />} />
                    
                    <Line 
                      type="monotone" 
                      dataKey="total_score" 
                      stroke="#0891b2"
                      strokeWidth={3}
                      dot={<CustomDot />}
                      activeDot={{ r: 8, stroke: '#0891b2', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                
                {/* Overlay for line segment labels */}
                <div className="absolute inset-0 pointer-events-none">
                  {chartData.length > 1 && chartData.map((item, index) => {
                    if (index === 0 || !item.scoreDifference || Math.abs(item.scoreDifference) <= 5) return null;
                    
                    const difference = item.scoreDifference;
                    const isPositive = difference > 0;
                    
                    
                    const xPercent = ((index - 0.5) / (chartData.length - 1)) * 100;
                    const currentScore = item.total_score;
                    const previousScore = chartData[index - 1].total_score;
                    const yPercent = 100 - (((currentScore + previousScore) / 2) / 27) * 100;
                    
                    return (
                      <div
                        key={`line-label-${index}`}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                          left: `${xPercent}%`,
                          top: `${yPercent}%`
                        }}
                      >
                        <span
                          className={`inline-block px-2 py-1 text-xs font-bold rounded shadow-sm border ${
                            isPositive 
                              ? 'bg-green-50 text-green-700 border-green-200' 
                              : 'bg-red-50 text-red-700 border-red-200'
                          }`}
                        >
                          {isPositive ? `+${difference}` : difference}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="mt-4 text-xs text-gray-500">
                <p>{t('mmse:historyPage.chart.higherScoresBetter')}</p>
                <p>{t('mmse:historyPage.chart.severityThresholds')}</p>
              </div>
            </div>

            {/* Latest Test Domain Analysis */}
            {radarData.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">{t('mmse:historyPage.domainAnalysis.title')}</h2>
                  <p className="text-gray-600 text-sm">{t('mmse:historyPage.domainAnalysis.subtitle')}</p>
                </div>

                <div className="h-96 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={radarData} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
                      <PolarGrid />
                      <PolarAngleAxis 
                        dataKey="section" 
                        tick={{ fontSize: 12 }}
                        className="text-xs"
                      />
                      <PolarRadiusAxis 
                        domain={[0, 100]} 
                        tick={{ fontSize: 10 }}
                        tickCount={6}
                      />
                      <Radar
                        name={t('mmse:historyPage.tooltip.latestTest')}
                        dataKey="percentage"
                        stroke="#0891b2"
                        fill="#0891b2"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Legend />
                      <Tooltip 
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                                <p className="font-semibold text-gray-900 mb-2">{data.section}</p>
                                <p className="text-sm text-cyan-600">
                                  {t('mmse:historyPage.tooltip.scoreLabel', { percentage: data.percentage.toFixed(1) })}
                                </p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                <div className="mt-4 text-xs text-gray-500">
                  <p>{t('mmse:historyPage.chart.cognitiveDomainsAxis')}</p>
                  <p>{t('mmse:historyPage.chart.percentagesShow')}</p>
                  <p>{t('mmse:historyPage.chart.higherValuesBetter')}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
