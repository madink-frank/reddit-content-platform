import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { io, Socket } from 'socket.io-client';
import { queryKeys } from '../services/queryClient';
import { useNotificationStore } from '../stores/notificationStore';
import { config } from '../config/env';

interface TrendUpdateEvent {
  type: 'trend_analysis_complete' | 'trend_data_updated';
  data: {
    keyword_id?: number;
    task_id?: string;
    status?: string;
    metrics?: any;
  };
}

export const useRealtimeTrends = (enabled: boolean = true) => {
  const socketRef = useRef<Socket | null>(null);
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  useEffect(() => {
    if (!enabled) return;

    // Initialize WebSocket connection
    const socket = io(config.wsUrl, {
      transports: ['websocket'],
      autoConnect: true,
    });

    socketRef.current = socket;

    // Handle connection events
    socket.on('connect', () => {
      console.log('Connected to trend updates WebSocket');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from trend updates WebSocket');
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    // Handle trend update events
    socket.on('trend_update', (event: TrendUpdateEvent) => {
      handleTrendUpdate(event);
    });

    // Handle trend analysis completion
    socket.on('trend_analysis_complete', (data: any) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.trends.all });
      
      addNotification({
        type: 'success',
        title: 'Trend Analysis Complete',
        message: `Analysis for ${data.keyword_count || 'all'} keywords has been completed.`,
        duration: 5000,
      });
    });

    // Handle trend analysis errors
    socket.on('trend_analysis_error', (data: any) => {
      addNotification({
        type: 'error',
        title: 'Trend Analysis Failed',
        message: data.error || 'An error occurred during trend analysis.',
        duration: 8000,
      });
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [enabled, queryClient, addNotification]);

  const handleTrendUpdate = (event: TrendUpdateEvent) => {
    switch (event.type) {
      case 'trend_analysis_complete':
        // Invalidate all trend queries to refresh data
        queryClient.invalidateQueries({ queryKey: queryKeys.trends.all });
        
        // Show success notification
        addNotification({
          type: 'success',
          title: 'Trends Updated',
          message: 'New trend analysis data is available.',
          duration: 3000,
        });
        break;

      case 'trend_data_updated':
        // Invalidate specific keyword trend if available
        if (event.data.keyword_id) {
          queryClient.invalidateQueries({ 
            queryKey: queryKeys.trends.detail(event.data.keyword_id) 
          });
        } else {
          // Invalidate all trend queries
          queryClient.invalidateQueries({ queryKey: queryKeys.trends.all });
        }
        break;

      default:
        console.log('Unknown trend update event:', event);
    }
  };

  const subscribeToKeyword = (keywordId: number) => {
    if (socketRef.current) {
      socketRef.current.emit('subscribe_keyword_trends', { keyword_id: keywordId });
    }
  };

  const unsubscribeFromKeyword = (keywordId: number) => {
    if (socketRef.current) {
      socketRef.current.emit('unsubscribe_keyword_trends', { keyword_id: keywordId });
    }
  };

  const subscribeToAllTrends = () => {
    if (socketRef.current) {
      socketRef.current.emit('subscribe_all_trends');
    }
  };

  const unsubscribeFromAllTrends = () => {
    if (socketRef.current) {
      socketRef.current.emit('unsubscribe_all_trends');
    }
  };

  return {
    isConnected: socketRef.current?.connected || false,
    subscribeToKeyword,
    unsubscribeFromKeyword,
    subscribeToAllTrends,
    unsubscribeFromAllTrends,
  };
};