/**
 * src/frontend/src/app/components/ErrorBoundary.tsx
 * 
 * React Error Boundary Components
 * Catches errors in complex components and provides fallback UI
 * Ensures that if DAG renderer or analytics fail, core learning room stays functional
 * 
 * Features:
 * - Catch render errors before they crash the app
 * - Graceful fallback UI with helpful error messages
 * - Error logging for debugging
 * - Recovery options
 */

"use client";

import React, { ReactNode, ReactElement } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactElement;
  componentName?: string;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorCount: number;
}

interface ErrorInfo {
  componentStack: string;
}

/**
 * Generic Error Boundary Component
 * Wraps components that might throw errors during render
 */
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error for debugging
    console.error(
      `[ErrorBoundary${this.props.componentName ? `: ${this.props.componentName}` : ""}]`,
      error
    );
    console.error("Error Info:", errorInfo);

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Increment error count
    this.setState((prevState) => ({
      errorCount: prevState.errorCount + 1,
    }));
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      // Default fallback UI
      return (
        <DefaultErrorFallback
          error={this.state.error}
          componentName={this.props.componentName}
          retry={this.handleRetry}
          errorCount={this.state.errorCount}
        />
      );
    }

    return this.props.children;
  }
}

/**
 * Default Error Fallback UI
 */
function DefaultErrorFallback({
  error,
  componentName,
  retry,
  errorCount,
}: {
  error: Error;
  componentName?: string;
  retry: () => void;
  errorCount: number;
}) {
  const shouldShowDetails = process.env.NODE_ENV === "development";
  const maxRetries = 3;
  const canRetry = errorCount < maxRetries;

  return (
    <div className="w-full p-6 bg-red-50 border border-red-200 rounded-lg">
      <div className="flex items-start gap-4">
        <span className="text-4xl">⚠️</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-red-900 mb-2">
            {componentName ? `${componentName} Error` : "Something went wrong"}
          </h3>
          <p className="text-sm text-red-800 mb-4">
            {componentName
              ? `The ${componentName} component encountered an error and couldn't load.`
              : "An unexpected error occurred. The page may not function correctly."}
          </p>

          {shouldShowDetails && (
            <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded text-xs text-red-900 font-mono overflow-auto max-h-32">
              <div className="font-bold mb-1">Error details:</div>
              <div>{error.message}</div>
              {error.stack && (
                <div className="mt-2 text-red-800 text-xs opacity-75">
                  {error.stack.split("\n").slice(0, 3).join("\n")}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3">
            {canRetry && (
              <button
                onClick={retry}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold rounded transition-colors"
              >
                Try Again {errorCount > 0 && `(${errorCount}/${maxRetries})`}
              </button>
            )}
            <a
              href="/app/learn"
              className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-900 text-sm font-semibold rounded transition-colors"
            >
              Go Back
            </a>
          </div>

          {!canRetry && (
            <p className="text-xs text-red-800 mt-3">
              ⚠️ Multiple errors occurred. Please refresh the page or contact support if
              this persists.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Error Boundary specifically for Analytics Components
 * Provides domain-specific error messaging
 */
export class AnalyticsErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[AnalyticsErrorBoundary]", error);
    console.error("Error Info:", errorInfo);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    this.setState((prevState) => ({
      errorCount: prevState.errorCount + 1,
    }));
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full p-6 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start gap-4">
            <span className="text-4xl">📊</span>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-amber-900 mb-2">
                Analytics Unavailable
              </h3>
              <p className="text-sm text-amber-800 mb-4">
                We couldn&apos;t load your analytics dashboard. Your learning progress is safe,
                but these statistics are temporarily unavailable.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={this.handleRetry}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold rounded transition-colors"
                >
                  Reload Dashboard
                </button>
                <a
                  href="/app/learn"
                  className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-900 text-sm font-semibold rounded transition-colors"
                >
                  Back to Learning
                </a>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Error Boundary specifically for DAG Renderer
 * Keeps learning room functional even if graph fails
 */
export class DAGErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[DAGErrorBoundary]", error);
    console.error("Error Info:", errorInfo);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    this.setState((prevState) => ({
      errorCount: prevState.errorCount + 1,
    }));
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-4">
            <span className="text-4xl">🗺️</span>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-blue-900 mb-2">
                Learning Path Map Unavailable
              </h3>
              <p className="text-sm text-blue-800 mb-4">
                The learning path visualization couldn&apos;t load, but you can still learn!
                Your progress is saved and the content is available.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={this.handleRetry}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold rounded transition-colors"
                >
                  Reload Map
                </button>
                <a
                  href="/app/learn"
                  className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-900 text-sm font-semibold rounded transition-colors"
                >
                  Continue Learning
                </a>
              </div>
              <p className="text-xs text-blue-700 mt-3">
                💡 The learning room and all your content is still accessible. Only the map visualization is offline.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
