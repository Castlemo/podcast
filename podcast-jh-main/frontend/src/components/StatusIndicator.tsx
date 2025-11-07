import React from 'react';
import type { PodcastStatus } from '../services/api';

interface StatusIndicatorProps {
  podcastId: string;
  status: PodcastStatus;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ podcastId, status }) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900">생성 상태</h3>
        <span className="text-sm text-gray-500 font-mono">ID: {podcastId.slice(0, 8)}...</span>
      </div>

      <div className="flex items-center gap-4 p-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl">
        {status.status === 'processing' && (
          <>
            <div className="flex-shrink-0">
              <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg font-semibold text-gray-900">처리 중...</span>
              </div>
              <p className="text-sm text-gray-600">{status.message}</p>
            </div>
          </>
        )}
        {status.status === 'completed' && (
          <>
            <div className="flex-shrink-0 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="flex-1">
              <span className="text-lg font-semibold text-green-700">완료</span>
              <p className="text-sm text-gray-600">{status.message}</p>
            </div>
          </>
        )}
        {status.status === 'failed' && (
          <>
            <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div className="flex-1">
              <span className="text-lg font-semibold text-red-700">실패</span>
              <p className="text-sm text-gray-600">{status.message}</p>
            </div>
          </>
        )}
      </div>

      {/* Failed State Message */}
      {status.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mt-6">
          <p className="text-red-800 font-medium">팟캐스트 생성에 실패했습니다.</p>
          <p className="text-sm text-red-600 mt-2">다시 시도하거나 다른 주제로 생성해보세요.</p>
        </div>
      )}
    </div>
  );
};

export default StatusIndicator;
