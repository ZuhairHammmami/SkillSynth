/**
 * tools/cli/src/utils.ts
 * 
 * Utility Functions
 * Helpers for CLI display, trees, and formatting
 */

import chalk from "chalk";

/**
 * Render ASCII tree of mastery path
 * Shows current node, visited nodes, and allowed paths
 */
export function renderMasteryTree(
  currentNodeId: string,
  pathHistory: string[],
  allowedPaths: string[],
  nodeMap: Map<string, { title: string; difficulty: string }>
): string {
  const lines: string[] = [];

  lines.push(chalk.bold.cyan("📚 Mastery Path DAG\n"));

  // Render current node
  const currentNode = nodeMap.get(currentNodeId);
  lines.push(chalk.bold.green("● Current Node"));
  lines.push(`  └─ ${currentNode?.title || currentNodeId} [${currentNode?.difficulty}]\n`);

  // Render completed nodes
  if (pathHistory.length > 0) {
    lines.push(chalk.bold.blue("✓ Completed Nodes"));
    pathHistory.forEach((nodeId, idx) => {
      const node = nodeMap.get(nodeId);
      const prefix = idx === pathHistory.length - 1 ? "└─" : "├─";
      lines.push(`  ${prefix} ${node?.title || nodeId} [${node?.difficulty}]`);
    });
    lines.push("");
  }

  // Render allowed/next nodes
  if (allowedPaths.length > 0) {
    lines.push(chalk.bold.yellow("→ Available Next Steps"));
    allowedPaths.forEach((nodeId, idx) => {
      const node = nodeMap.get(nodeId);
      const prefix = idx === allowedPaths.length - 1 ? "└─" : "├─";
      lines.push(`  ${prefix} ${node?.title || nodeId} [${node?.difficulty}]`);
    });
  }

  return lines.join("\n");
}

/**
 * Render search results as a formatted table
 */
export function renderSearchResults(
  results: Array<{ title: string; difficulty: string; relevance: number }>
): string {
  const lines: string[] = [];

  lines.push(chalk.bold.cyan("🔍 Search Results\n"));

  results.forEach((result, idx) => {
    const score = (result.relevance * 100).toFixed(1);
    const diffColor = result.difficulty === "beginner"
      ? chalk.green
      : result.difficulty === "intermediate"
      ? chalk.yellow
      : chalk.red;

    lines.push(`${idx + 1}. ${result.title}`);
    lines.push(
      `   Difficulty: ${diffColor(result.difficulty)} | Relevance: ${chalk.blue(score + "%")}`
    );
    lines.push("");
  });

  return lines.join("\n");
}

/**
 * Format error message
 */
export function formatError(error: string): string {
  return chalk.red(`❌ Error: ${error}`);
}

/**
 * Format success message
 */
export function formatSuccess(message: string): string {
  return chalk.green(`✅ ${message}`);
}

/**
 * Format info message
 */
export function formatInfo(message: string): string {
  return chalk.blue(`ℹ️ ${message}`);
}
