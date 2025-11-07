import React from 'react';
import type { DialogueMetadata } from '../services/api';

interface SpeakerPanelProps {
  metadata: DialogueMetadata[];
  currentTime: number;
}

const SpeakerPanel: React.FC<SpeakerPanelProps> = ({ metadata, currentTime }) => {
  // 현재 재생 중인 대사 찾기
  const currentDialogue = metadata.find(
    (dialogue) => currentTime >= dialogue.start_time && currentTime < dialogue.end_time
  );

  // 고유한 화자 목록 추출
  const uniqueSpeakers = Array.from(
    new Set(metadata.map((d) => d.speaker))
  ).map((speakerId) => {
    const dialogue = metadata.find((d) => d.speaker === speakerId);
    return {
      id: speakerId,
      name: dialogue?.speaker_name || speakerId,
      gender: dialogue?.gender || 'unknown',
    };
  });

  // 화자별 아바타 이미지 (성별에 따라)
  const getAvatarEmoji = (gender: string) => {
    return gender === 'female' ? '👩' : '👨';
  };

  return (
    <div className="speaker-panel bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">화자</h3>
      <div className="flex gap-6 justify-center">
        {uniqueSpeakers.map((speaker) => {
          const isActive = currentDialogue?.speaker === speaker.id;
          return (
            <div
              key={speaker.id}
              className={`speaker-card transition-all duration-300 ${
                isActive ? 'scale-110' : 'scale-100 opacity-60'
              }`}
            >
              <div
                className={`relative flex flex-col items-center p-4 rounded-xl ${
                  isActive
                    ? 'bg-white shadow-2xl ring-4 ring-blue-400 ring-opacity-50'
                    : 'bg-white shadow-md'
                }`}
              >
                {/* 아바타 */}
                <div
                  className={`text-6xl mb-2 transition-transform duration-300 ${
                    isActive ? 'animate-pulse' : ''
                  }`}
                >
                  {getAvatarEmoji(speaker.gender)}
                </div>

                {/* 화자 이름 */}
                <div className="text-center">
                  <p
                    className={`font-bold ${
                      isActive ? 'text-blue-600 text-lg' : 'text-gray-600 text-sm'
                    }`}
                  >
                    {speaker.name}
                  </p>
                </div>

                {/* 활성 인디케이터 */}
                {isActive && (
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                    <div className="absolute top-0 left-0 w-2 h-2 bg-blue-500 rounded-full"></div>
                  </div>
                )}
              </div>

              {/* 현재 대사 표시 */}
              {isActive && currentDialogue && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg shadow-sm">
                  <p className="text-sm text-gray-700 text-center italic line-clamp-2">
                    "{currentDialogue.text}"
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SpeakerPanel;
