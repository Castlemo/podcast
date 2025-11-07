import React, { useState, useEffect, useRef } from 'react';
import { podcastApi } from '../services/api';
import type { PodcastMetadata } from '../services/api';
import SpeakerPanel from './SpeakerPanel';

interface PodcastResultProps {
  podcastId: string;
  scriptPath?: string;
  audioPath?: string;
}

const PodcastResult: React.FC<PodcastResultProps> = ({ podcastId, scriptPath, audioPath }) => {
  const [metadata, setMetadata] = useState<PodcastMetadata | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  // 메타데이터 로드
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const data = await podcastApi.getMetadata(podcastId);
        setMetadata(data);
      } catch (error) {
        console.error('메타데이터 로드 실패:', error);
      }
    };

    if (podcastId && audioPath) {
      loadMetadata();
    }
  }, [podcastId, audioPath]);

  // 오디오 재생 시간 추적
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, []);

  return (
    <div className="space-y-6 pt-4">
      {scriptPath && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            생성된 스크립트
          </h4>
          <a
            href={podcastApi.downloadScript(podcastId)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 text-blue-700 font-semibold py-3 px-6 rounded-lg border border-blue-200 transition-all duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            스크립트 보기/다운로드
          </a>
        </div>
      )}

      {audioPath && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            생성된 오디오
          </h4>

          {/* 화자 패널 */}
          {metadata && metadata.dialogues.length > 0 && (
            <div className="mb-6">
              <SpeakerPanel metadata={metadata.dialogues} currentTime={currentTime} />
            </div>
          )}

          <div className="space-y-4">
            <audio
              ref={audioRef}
              controls
              className="w-full rounded-lg shadow-sm"
              style={{ height: '54px' }}
            >
              <source src={podcastApi.downloadAudio(podcastId)} type="audio/mp3" />
              브라우저가 오디오를 지원하지 않습니다.
            </audio>
            <a
              href={podcastApi.downloadAudio(podcastId)}
              download
              className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-50 to-purple-50 hover:from-indigo-100 hover:to-purple-100 text-indigo-700 font-semibold py-3 px-6 rounded-lg border border-indigo-200 transition-all duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              오디오 파일 다운로드
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default PodcastResult;
