/**
 * tools/cli/src/config.ts
 * 
 * CLI Configuration Manager
 * Stores and retrieves user authentication tokens and preferences
 * Uses Conf for persistent storage in ~/.config/skillsynth
 */

import Conf from "conf";
import path from "path";

interface CLIConfig {
  apiUrl: string;
  token?: string;
  userId?: string;
  lastUpdated?: number;
}

export class ConfigManager {
  private config: Conf<CLIConfig>;

  constructor() {
    this.config = new Conf<CLIConfig>({
      projectName: "skillsynth",
      configFileLocation: path.join(process.env.HOME || "", ".config", "skillsynth", "config.json"),
      defaults: {
        apiUrl: process.env.SKILLSYNTH_API_URL || "http://localhost:3000",
      },
    });
  }

  /**
   * Set authentication token (Personal Access Token)
   */
  setToken(token: string, userId: string): void {
    this.config.set("token", token);
    this.config.set("userId", userId);
    this.config.set("lastUpdated", Date.now());
  }

  /**
   * Get authentication token
   */
  getToken(): string | undefined {
    return this.config.get("token");
  }

  /**
   * Get user ID
   */
  getUserId(): string | undefined {
    return this.config.get("userId");
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getUserId();
  }

  /**
   * Clear authentication (logout)
   */
  clearAuth(): void {
    this.config.delete("token");
    this.config.delete("userId");
    this.config.delete("lastUpdated");
  }

  /**
   * Get API URL
   */
  getApiUrl(): string {
    return this.config.get("apiUrl", "http://localhost:3000");
  }

  /**
   * Set API URL
   */
  setApiUrl(url: string): void {
    this.config.set("apiUrl", url);
  }

  /**
   * Get all config
   */
  getAll(): CLIConfig {
    return this.config.store;
  }
}

export const configManager = new ConfigManager();
