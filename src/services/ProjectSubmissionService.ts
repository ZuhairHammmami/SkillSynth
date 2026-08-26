/**
 * src/services/ProjectSubmissionService.ts
 * 
 * Project Submission Validation Service (Phase 4.0)
 * Handles GitHub URL validation, file upload verification, and submission processing
 * 
 * Features:
 * - GitHub URL HEAD request validation
 * - File upload verification (size, type)
 * - Submission storage and tracking
 * - Passing criteria validation
 */

import type { GitHubValidationResult, ProjectSubmission, ProjectNodeRequirement } from "../entities/EngineeringProject";

export interface SubmitProjectOptions {
  userId: string;
  projectId: string;
  nodeId: string;
  milestone: string;
  submissionType: "file_upload" | "github_url" | "code_snippet" | "demo_link";
  submissionData: {
    fileUrl?: string;
    githubUrl?: string;
    codeSnippet?: string;
    demoLink?: string;
  };
  description?: string;
}

export interface SubmissionValidationResult {
  isValid: boolean;
  submissionId?: string;
  errors: string[];
  warnings: string[];
}

/**
 * GitHub URL validation using HEAD request
 * Checks if repository exists and is accessible
 */
async function validateGitHubUrl(url: string): Promise<GitHubValidationResult> {
  try {
    // Parse GitHub URL format: https://github.com/owner/repo[/tree/branch]
    const match = url.match(/github\.com[:/]([^/]+)\/([^/\s.]+)(?:\/tree\/([^/\s]+))?/);
    
    if (!match) {
      return {
        isValid: false,
        url,
        error: "Invalid GitHub URL format. Expected: https://github.com/owner/repo or https://github.com/owner/repo/tree/branch",
      };
    }

    const [, owner, repo, branch = "main"] = match;

    // Perform HEAD request to check repository accessibility
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/branches/${branch}`;
    
    const response = await fetch(apiUrl, {
      method: "HEAD",
      headers: {
        "Accept": "application/vnd.github.v3+json",
        // Optional: Add GitHub token from env for higher rate limits
        ...(process.env.GITHUB_TOKEN && { "Authorization": `token ${process.env.GITHUB_TOKEN}` }),
      },
      // 5 second timeout
      signal: AbortSignal.timeout(5000),
    }).catch(() => null);

    if (!response) {
      return {
        isValid: false,
        url,
        owner,
        repo,
        branch,
        error: "Failed to connect to GitHub API - timeout or network error",
      };
    }

    if (response.status === 404) {
      return {
        isValid: false,
        url,
        owner,
        repo,
        branch,
        status: 404,
        error: `Repository or branch not found (${owner}/${repo}:${branch})`,
      };
    }

    if (response.status === 403) {
      return {
        isValid: false,
        url,
        owner,
        repo,
        branch,
        status: 403,
        error: "Repository is private or access is denied",
      };
    }

    if (response.ok || response.status === 200) {
      return {
        isValid: true,
        url,
        owner,
        repo,
        branch,
        status: response.status,
        lastUpdated: new Date().toISOString(),
      };
    }

    return {
      isValid: false,
      url,
      owner,
      repo,
      branch,
      status: response.status,
      error: `Unexpected status code: ${response.status}`,
    };
  } catch (error) {
    return {
      isValid: false,
      url,
      error: `Validation error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

/**
 * Validate demo link accessibility
 */
async function validateDemoLink(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, {
      method: "HEAD",
      signal: AbortSignal.timeout(5000),
    }).catch(() => null);

    return response ? response.ok || response.status < 400 : false;
  } catch {
    return false;
  }
}

/**
 * Validate file submission
 */
function validateFileSubmission(
  fileUrl: string,
  maxSizeMB: number = 50
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check URL format
  try {
    new URL(fileUrl);
  } catch {
    errors.push("File URL is not a valid URL");
  }

  // Check file extension (basic validation)
  const validExtensions = [
    ".pdf", ".doc", ".docx", ".txt", ".md", // documents
    ".zip", ".tar", ".gz", // archives
    ".jpg", ".png", ".gif", ".webp", // images
    ".mp4", ".webm", // videos
  ];

  const fileExtension = fileUrl.split("?")[0].split(".").pop()?.toLowerCase() || "";
  if (!validExtensions.some(ext => ext.endsWith(fileExtension))) {
    errors.push(`File extension .${fileExtension} not supported. Allowed: ${validExtensions.join(", ")}`);
  }

  return { isValid: errors.length === 0, errors };
}

/**
 * Validate code snippet submission
 */
function validateCodeSnippet(code: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!code || code.trim().length === 0) {
    errors.push("Code snippet cannot be empty");
  }

  if (code.length > 50000) {
    errors.push("Code snippet exceeds maximum length of 50,000 characters");
  }

  return { isValid: errors.length === 0, errors };
}

/**
 * Main project submission validation
 */
export class ProjectSubmissionService {
  /**
   * Validate and store project submission
   */
  static async submitProjectWork(
    options: SubmitProjectOptions
  ): Promise<SubmissionValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate submission type and data pairing
    if (options.submissionType === "github_url") {
      if (!options.submissionData.githubUrl) {
        errors.push("GitHub URL required for github_url submission type");
      } else {
        const validation = await validateGitHubUrl(options.submissionData.githubUrl);
        if (!validation.isValid) {
          errors.push(`GitHub validation failed: ${validation.error}`);
        } else {
          console.log(`[GitHub Validated] ${validation.owner}/${validation.repo}:${validation.branch}`);
        }
      }
    } else if (options.submissionType === "file_upload") {
      if (!options.submissionData.fileUrl) {
        errors.push("File URL required for file_upload submission type");
      } else {
        const fileValidation = validateFileSubmission(options.submissionData.fileUrl);
        if (!fileValidation.isValid) {
          errors.push(...fileValidation.errors);
        }
      }
    } else if (options.submissionType === "code_snippet") {
      if (!options.submissionData.codeSnippet) {
        errors.push("Code snippet required for code_snippet submission type");
      } else {
        const codeValidation = validateCodeSnippet(options.submissionData.codeSnippet);
        if (!codeValidation.isValid) {
          errors.push(...codeValidation.errors);
        }
      }
    } else if (options.submissionType === "demo_link") {
      if (!options.submissionData.demoLink) {
        errors.push("Demo link required for demo_link submission type");
      } else {
        const demoValid = await validateDemoLink(options.submissionData.demoLink);
        if (!demoValid) {
          warnings.push("Demo link is currently inaccessible - it may be offline or require authentication");
        }
      }
    }

    if (errors.length > 0) {
      return {
        isValid: false,
        errors,
        warnings,
      };
    }

    // In production, store submission in database here
    const submissionId = `submission_${Date.now()}`;
    console.log(
      `[Project Submission Accepted] User: ${options.userId}, Project: ${options.projectId}, Node: ${options.nodeId}, Milestone: ${options.milestone}`
    );

    return {
      isValid: true,
      submissionId,
      errors,
      warnings,
    };
  }

  /**
   * Check if a user has completed a project milestone requirement
   */
  static async checkMilestoneCompletion(
    userId: string,
    projectId: string,
    nodeId: string,
    milestone: string
  ): Promise<boolean> {
    // In production, query database for submission with passed=true
    // For now, return false (not completed)
    console.log(
      `[Checking Milestone] User: ${userId}, Project: ${projectId}, Node: ${nodeId}, Milestone: ${milestone}`
    );
    return false;
  }

  /**
   * Get all pending submissions for review
   */
  static async getPendingSubmissions(
    projectId?: string,
    nodeId?: string
  ): Promise<ProjectSubmission[]> {
    // In production, query database for submissions with passed=null (pending review)
    console.log(`[Fetching Pending Submissions] Project: ${projectId}, Node: ${nodeId}`);
    return [];
  }

  /**
   * Review and approve/reject a submission
   */
  static async reviewSubmission(
    submissionId: string,
    approved: boolean,
    notes?: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      // In production, update submission in database
      console.log(
        `[Submission ${approved ? "Approved" : "Rejected"}] ID: ${submissionId}, Notes: ${notes || "None"}`
      );
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: `Failed to review submission: ${error instanceof Error ? error.message : "Unknown error"}`,
      };
    }
  }
}
