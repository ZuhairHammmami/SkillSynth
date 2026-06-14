/**
 * tools/cli/src/api.ts
 * 
 * API Client
 * Communicates with SkillSynth backend using stored authentication token
 */

import axios, { AxiosInstance } from "axios";
import { configManager } from "./config";

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface MasteryPath {
  id: string;
  userId: string;
  currentNode: string;
  pathHistory: string[];
  allowedPaths: string[];
}

export interface KnowledgeNode {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  prerequisites: string[];
  prerequisites_met?: number;
}

export interface UnlockInfo {
  nodeId: string;
  requiresQuiz: boolean;
  requiresProject: boolean;
  quizId?: string;
  projectId?: string;
}

export class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: configManager.getApiUrl(),
      timeout: 10000,
    });

    // Add authorization header if token exists
    this.client.interceptors.request.use((config) => {
      const token = configManager.getToken();
      const userId = configManager.getUserId();
      if (token && userId) {
        config.headers["Authorization"] = `Bearer ${token}`;
        config.headers["x-user-id"] = userId;
      }
      return config;
    });
  }

  /**
   * Authenticate with Personal Access Token
   */
  async authenticate(token: string): Promise<{ userId: string; email: string }> {
    try {
      const response = await this.client.post<APIResponse<{ userId: string; email: string }>>(
        "/api/auth/verify-token",
        { token }
      );

      if (response.data.success && response.data.data) {
        configManager.setToken(token, response.data.data.userId);
        return response.data.data;
      }
      throw new Error(response.data.error || "Authentication failed");
    } catch (error: any) {
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }

  /**
   * Get user's current mastery path
   */
  async getMasteryPath(): Promise<MasteryPath> {
    const userId = configManager.getUserId();
    if (!userId) throw new Error("Not authenticated");

    const response = await this.client.get<APIResponse<MasteryPath>>(`/api/mastery/path/${userId}`);
    if (!response.data.success) throw new Error(response.data.error);
    return response.data.data!;
  }

  /**
   * Get knowledge node details
   */
  async getNode(nodeId: string): Promise<KnowledgeNode> {
    const response = await this.client.get<APIResponse<KnowledgeNode>>(`/api/nodes/${nodeId}`);
    if (!response.data.success) throw new Error(response.data.error);
    return response.data.data!;
  }

  /**
   * Get unlock info for a node (quiz vs project)
   */
  async getUnlockInfo(nodeId: string): Promise<UnlockInfo> {
    const userId = configManager.getUserId();
    if (!userId) throw new Error("Not authenticated");

    const response = await this.client.get<APIResponse<UnlockInfo>>(
      `/api/mastery/unlock-info/${nodeId}`,
      {
        headers: { "x-user-id": userId },
      }
    );
    if (!response.data.success) throw new Error(response.data.error);
    return response.data.data!;
  }

  /**
   * Search for nodes using vector search
   */
  async searchNodes(query: string, limit: number = 5): Promise<KnowledgeNode[]> {
    const response = await this.client.get<APIResponse<KnowledgeNode[]>>(`/api/search/discover`, {
      params: { query, limit },
    });
    if (!response.data.success) throw new Error(response.data.error);
    return response.data.data || [];
  }
}

export const apiClient = new APIClient();
