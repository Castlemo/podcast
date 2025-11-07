import React from 'react';
import type { PodcastRequest, VoicesResponse } from '../services/api';

interface PodcastFormProps {
  formData: PodcastRequest;
  loading: boolean;
  podcastId: string | null;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  onReset: () => void;
  availableVoices: VoicesResponse | null;
  selectedVoices: Record<string, string>;
  onVoiceChange: (speaker: string, voiceId: string) => void;
  pdfFile: File | null;
  onPdfChange: (file: File | null) => void;
}

const PodcastForm: React.FC<PodcastFormProps> = ({
  formData,
  loading,
  podcastId,
  onInputChange,
  onSubmit,
  onReset,
  availableVoices,
  selectedVoices,
  onVoiceChange,
  pdfFile,
  onPdfChange,
}) => {
  const [activeTab, setActiveTab] = React.useState<'topic' | 'url' | 'pdf'>('topic');

  // 화자 수에 따른 화자 레이블 생성
  const getSpeakerLabels = () => {
    const numSpeakers = formData.num_speakers || 2;
    const labels = [];
    for (let i = 0; i < numSpeakers; i++) {
      labels.push(`화자${String.fromCharCode(65 + i)}`); // 화자A, 화자B, 화자C
    }
    return labels;
  };

  // 탭 전환 시 다른 탭의 입력값 초기화
  const handleTabChange = (tab: 'topic' | 'url' | 'pdf') => {
    setActiveTab(tab);
    // 탭 전환 시 다른 탭의 값들 초기화
    if (tab === 'topic') {
      const urlEvent = {
        target: { name: 'url', value: '' }
      } as React.ChangeEvent<HTMLInputElement>;
      onInputChange(urlEvent);
      onPdfChange(null);
    } else if (tab === 'url') {
      const topicEvent = {
        target: { name: 'topic', value: '' }
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onInputChange(topicEvent);
      onPdfChange(null);
    } else if (tab === 'pdf') {
      const topicEvent = {
        target: { name: 'topic', value: '' }
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onInputChange(topicEvent);
      const urlEvent = {
        target: { name: 'url', value: '' }
      } as React.ChangeEvent<HTMLInputElement>;
      onInputChange(urlEvent);
    }
  };

  const handlePdfFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file && !file.name.toLowerCase().endsWith('.pdf')) {
      alert('PDF 파일만 업로드 가능합니다.');
      e.target.value = '';
      return;
    }
    onPdfChange(file);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
      <form onSubmit={onSubmit} className="space-y-6">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              type="button"
              onClick={() => handleTabChange('topic')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'topic'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              disabled={loading}
            >
              주제로 생성
            </button>
            <button
              type="button"
              onClick={() => handleTabChange('url')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'url'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              disabled={loading}
            >
              URL로 생성
            </button>
            <button
              type="button"
              onClick={() => handleTabChange('pdf')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'pdf'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              disabled={loading}
            >
              PDF로 생성
            </button>
          </nav>
        </div>

        {/* Topic Tab */}
        {activeTab === 'topic' && (
          <div>
            <label htmlFor="topic" className="block text-sm font-semibold text-gray-700 mb-2">
              주제 <span className="text-red-500">*</span>
            </label>
            <textarea
              id="topic"
              name="topic"
              value={formData.topic || ''}
              onChange={onInputChange}
              placeholder="팟캐스트 주제를 입력하세요... (예: 인공지능의 미래, 건강한 식습관, 투자 전략 등)"
              rows={4}
              disabled={loading}
              required
              className="input-field resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              원하는 주제를 입력하면 AI가 자동으로 대화형 팟캐스트 스크립트를 생성합니다.
            </p>
          </div>
        )}

        {/* URL Tab */}
        {activeTab === 'url' && (
          <div>
            <label htmlFor="url" className="block text-sm font-semibold text-gray-700 mb-2">
              웹페이지 URL <span className="text-red-500">*</span>
            </label>
            <input
              type="url"
              id="url"
              name="url"
              value={formData.url || ''}
              onChange={onInputChange}
              placeholder="팟캐스트로 만들 웹페이지 URL을 입력하세요... (예: https://example.com/article)"
              disabled={loading}
              required
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              웹페이지의 핵심 내용을 AI가 추출하여 대화형 팟캐스트로 변환합니다.
            </p>
          </div>
        )}

        {/* PDF Tab */}
        {activeTab === 'pdf' && (
          <div>
            <label htmlFor="pdf" className="block text-sm font-semibold text-gray-700 mb-2">
              PDF 파일 업로드 <span className="text-red-500">*</span>
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-400 transition-colors">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="pdf-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                  >
                    <span>PDF 파일 선택</span>
                    <input
                      id="pdf-upload"
                      name="pdf-upload"
                      type="file"
                      accept=".pdf"
                      onChange={handlePdfFileChange}
                      disabled={loading}
                      required
                      className="sr-only"
                    />
                  </label>
                  <p className="pl-1">또는 드래그 앤 드롭</p>
                </div>
                <p className="text-xs text-gray-500">
                  PDF 파일 (최대 50MB)
                </p>
              </div>
            </div>
            {pdfFile && (
              <div className="mt-3 flex items-center justify-between p-3 bg-indigo-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <svg className="h-5 w-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm font-medium text-gray-700">{pdfFile.name}</span>
                  <span className="text-xs text-gray-500">({(pdfFile.size / 1024 / 1024).toFixed(2)} MB)</span>
                </div>
                <button
                  type="button"
                  onClick={() => onPdfChange(null)}
                  disabled={loading}
                  className="text-red-600 hover:text-red-800"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
            <p className="text-xs text-gray-500 mt-2">
              PDF 파일의 내용을 AI가 추출하여 핵심 내용을 정리한 후 대화형 팟캐스트로 변환합니다.
            </p>
          </div>
        )}

        {/* Options Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {/* Duration */}
          <div>
            <label htmlFor="duration_minutes" className="block text-sm font-semibold text-gray-700 mb-2">
              길이 (분)
            </label>
            <input
              type="number"
              id="duration_minutes"
              name="duration_minutes"
              value={formData.duration_minutes}
              onChange={onInputChange}
              min={1}
              max={5}
              disabled={loading}
              className="input-field"
            />
          </div>

          {/* Number of Speakers */}
          <div>
            <label htmlFor="num_speakers" className="block text-sm font-semibold text-gray-700 mb-2">
              화자 수
            </label>
            <div className="relative">
              <select
                id="num_speakers"
                name="num_speakers"
                value={formData.num_speakers}
                onChange={onInputChange}
                disabled={loading}
                className="select-field"
              >
                <option value={2}>2명 (대화)</option>
                <option value={3}>3명 (토론)</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Style */}
          <div>
            <label htmlFor="style" className="block text-sm font-semibold text-gray-700 mb-2">
              스타일
            </label>
            <div className="relative">
              <select
                id="style"
                name="style"
                value={formData.style || 'casual'}
                onChange={onInputChange}
                disabled={loading}
                className="select-field"
              >
                <option value="casual">친근한 대화</option>
                <option value="professional">전문적</option>
                <option value="educational">교육적</option>
                <option value="storytelling">스토리텔링</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Language */}
          <div>
            <label htmlFor="language" className="block text-sm font-semibold text-gray-700 mb-2">
              언어
            </label>
            <div className="relative">
              <select
                id="language"
                name="language"
                value={formData.language}
                onChange={onInputChange}
                disabled={loading}
                className="select-field"
              >
                <option value="ko">한국어</option>
                <option value="en">English</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
              </div>
            </div>
          </div>

          {/* TTS Engine */}
          <div>
            <label htmlFor="tts_engine" className="block text-sm font-semibold text-gray-700 mb-2">
              TTS 엔진
            </label>
            <div className="relative">
              <select
                id="tts_engine"
                name="tts_engine"
                value={formData.tts_engine}
                onChange={onInputChange}
                disabled={loading}
                className="select-field"
              >
                <option value="elevenlabs">ElevenLabs</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Voice Selection Section */}
        {availableVoices && (
          <div className="border-t pt-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              화자별 음성 선택 <span className="text-red-500">*</span>
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              각 화자별로 원하는 음성을 선택해주세요. 모든 화자의 음성 선택은 필수입니다.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {getSpeakerLabels().map((speaker) => (
                <div key={speaker}>
                  <label htmlFor={`voice-${speaker}`} className="block text-sm font-semibold text-gray-700 mb-2">
                    {speaker} 음성 <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      id={`voice-${speaker}`}
                      value={selectedVoices[speaker] || ''}
                      onChange={(e) => onVoiceChange(speaker, e.target.value)}
                      disabled={loading}
                      required
                      className="select-field"
                    >
                      <option value="">음성을 선택하세요</option>
                      {Object.entries(availableVoices.speakers).map(([key, voice]) => (
                        <option key={key} value={key}>
                          {voice.name} ({voice.gender}) - {voice.description}
                        </option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700">
                      <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <button
            type="submit"
            disabled={
              loading ||
              (activeTab === 'topic' && !formData.topic?.trim()) ||
              (activeTab === 'url' && !formData.url?.trim()) ||
              (activeTab === 'pdf' && !pdfFile)
            }
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                생성 중...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                팟캐스트 생성
              </>
            )}
          </button>
          {podcastId && (
            <button
              type="button"
              onClick={onReset}
              className="btn-secondary flex-1 flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              새로 생성
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default PodcastForm;
