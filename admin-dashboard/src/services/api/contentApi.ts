import { apiClient } from '../apiClient';
import { 
  BlogContent, 
  ContentTemplate, 
  PaginatedResponse, 
  ContentGenerationRequest,
  ContentGenerationResponse,
  ContentGenerationStatus,
  ContentPreview
} from '../../types';

export interface ContentListParams {
  page?: number;
  size?: number;
  keyword_id?: number;
  status?: 'draft' | 'published' | 'archived';
}

export interface ContentUpdateData {
  title?: string;
  content?: string;
  meta_description?: string;
  tags?: string[];
  featured_image_url?: string;
  status?: 'draft' | 'published' | 'archived';
}

export const contentApi = {
  // Get paginated list of generated content
  getContent: async (params?: ContentListParams): Promise<PaginatedResponse<BlogContent>> => {
    return apiClient.get<PaginatedResponse<BlogContent>>('/api/v1/content/', { params });
  },

  // Get content by ID
  getContentById: async (id: number): Promise<BlogContent> => {
    return apiClient.get<BlogContent>(`/api/v1/content/${id}`);
  },

  // Generate new content
  generateContent: async (data: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
    return apiClient.post<ContentGenerationResponse>('/api/v1/content/generate', data);
  },

  // Get generation status
  getGenerationStatus: async (taskId: string): Promise<ContentGenerationStatus> => {
    return apiClient.get<ContentGenerationStatus>(`/api/v1/content/generation-status/${taskId}`);
  },

  // Preview content without saving
  previewContent: async (data: ContentGenerationRequest): Promise<ContentPreview> => {
    return apiClient.post<ContentPreview>('/api/v1/content/preview', data);
  },

  // Update content
  updateContent: async (id: number, data: ContentUpdateData): Promise<BlogContent> => {
    return apiClient.put<BlogContent>(`/api/v1/content/${id}`, data);
  },

  // Delete content
  deleteContent: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/api/v1/content/${id}`);
  },

  // Regenerate existing content
  regenerateContent: async (id: number, templateType?: string, customPrompt?: string): Promise<ContentGenerationResponse> => {
    return apiClient.post<ContentGenerationResponse>(`/api/v1/content/${id}/regenerate`, {
      template_type: templateType,
      custom_prompt: customPrompt
    });
  },

  // Get available templates
  getTemplates: async (): Promise<{ templates: ContentTemplate[] }> => {
    return apiClient.get<{ templates: ContentTemplate[] }>('/api/v1/content/templates/');
  },

  // Batch generate content for multiple keywords
  batchGenerateContent: async (keywordIds: number[], options: Partial<ContentGenerationRequest>): Promise<ContentGenerationResponse> => {
    return apiClient.post<ContentGenerationResponse>('/api/v1/content/batch-generate', {
      keyword_ids: keywordIds,
      ...options
    });
  },
};