import React, { useState, useEffect } from 'react';
import { podcastApi } from '../services/api';
import type { PodcastRequest, PodcastStatus, VoicesResponse } from '../services/api';
import Header from './Header';
import PodcastForm from './PodcastForm';
import ErrorMessage from './ErrorMessage';
import StatusIndicator from './StatusIndicator';
import PodcastResult from './PodcastResult';

const PodcastGenerator: React.FC = () => {
  const [formData, setFormData] = useState<PodcastRequest>({
    duration_minutes: 2,
    language: 'ko',
    tts_engine: 'elevenlabs',
    num_speakers: 2,
    style: 'casual',
  });
  const [loading, setLoading] = useState(false);
  const [podcastId, setPodcastId] = useState<string | null>(null);
  const [status, setStatus] = useState<PodcastStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [availableVoices, setAvailableVoices] = useState<VoicesResponse | null>(null);
  const [selectedVoices, setSelectedVoices] = useState<Record<string, string>>({});
  const [pdfFile, setPdfFile] = useState<File | null>(null);

  // 컴포넌트 마운트 시 사용 가능한 음성 목록 불러오기
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const voices = await podcastApi.getVoices();
        setAvailableVoices(voices);
      } catch (err) {
        console.error('음성 목록 불러오기 실패:', err);
      }
    };
    fetchVoices();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // 화자 수가 변경되면 선택된 화자 초기화
    if (name === 'num_speakers') {
      setSelectedVoices({});
    }
  };

  const handleVoiceChange = (speaker: string, voiceId: string) => {
    setSelectedVoices(prev => ({
      ...prev,
      [speaker]: voiceId,
    }));
  };

  const handlePdfChange = (file: File | null) => {
    setPdfFile(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // topic, url, PDF 중 하나는 필수
    if (!formData.topic?.trim() && !formData.url?.trim() && !pdfFile) {
      setError('주제, URL 또는 PDF 파일 중 하나를 입력해주세요.');
      return;
    }

    // 화자 수에 따라 필요한 화자 확인
    const numSpeakers = formData.num_speakers || 2;
    const requiredSpeakers = Array.from({ length: numSpeakers }, (_, i) => `화자${String.fromCharCode(65 + i)}`);

    // 모든 필수 화자가 선택되었는지 확인
    const missingVoices = requiredSpeakers.filter(speaker => !selectedVoices[speaker]);
    if (missingVoices.length > 0) {
      setError(`모든 화자의 음성을 선택해주세요. 미선택: ${missingVoices.join(', ')}`);
      return;
    }

    setLoading(true);
    setError(null);
    setStatus(null);
    setPodcastId(null);

    try {
      let response;

      // PDF 파일이 있으면 PDF API 사용
      if (pdfFile) {
        response = await podcastApi.createPodcastFromPDF(
          pdfFile,
          formData.duration_minutes || 2,
          formData.language || 'ko',
          formData.tts_engine || 'elevenlabs',
          formData.num_speakers || 2,
          selectedVoices,
          formData.style || 'casual'
        );
      } else {
        // 선택한 화자를 custom_voices로 전달 (필수)
        const requestData: PodcastRequest = {
          ...formData,
          custom_voices: selectedVoices,
        };

        response = await podcastApi.createPodcast(requestData);
      }

      setPodcastId(response.podcast_id);
      setStatus({
        podcast_id: response.podcast_id,
        status: response.status as 'completed' | 'processing' | 'failed',
        message: response.message,
        script_path: response.script_path,
        audio_path: response.audio_path,
      });
      setLoading(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : '팟캐스트 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      duration_minutes: 2,
      language: 'ko',
      tts_engine: 'elevenlabs',
      num_speakers: 2,
      style: 'casual'
    });
    setSelectedVoices({});
    setPdfFile(null);
    setPodcastId(null);
    setStatus(null);
    setError(null);
    setLoading(false);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <Header />

        <PodcastForm
          formData={formData}
          loading={loading}
          podcastId={podcastId}
          onInputChange={handleInputChange}
          onSubmit={handleSubmit}
          onReset={resetForm}
          availableVoices={availableVoices}
          selectedVoices={selectedVoices}
          onVoiceChange={handleVoiceChange}
          pdfFile={pdfFile}
          onPdfChange={handlePdfChange}
        />

        {error && <ErrorMessage error={error} />}

        {podcastId && status && (
          <>
            <StatusIndicator podcastId={podcastId} status={status} />
            {status.status === 'completed' && (
              <div className="bg-white rounded-2xl shadow-xl p-8 mt-8">
                <PodcastResult
                  podcastId={podcastId}
                  scriptPath={status.script_path}
                  audioPath={status.audio_path}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default PodcastGenerator;
