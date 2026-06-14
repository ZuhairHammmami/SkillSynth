/**
 * tools/cli/src/commands/path.ts
 * 
 * skillsynth path
 * Display the user's current mastery path as an ASCII tree
 */

import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";
import { configManager } from "../config";
import { apiClient } from "../api";
import { renderMasteryTree } from "../utils";

export const pathCommand = new Command("path")
  .description("Display your current mastery path")
  .action(async () => {
    const spinner = ora();

    try {
      // Check authentication
      if (!configManager.isAuthenticated()) {
        console.log(chalk.red("❌ Not authenticated. Run 'skillsynth login' first."));
        process.exit(1);
      }

      spinner.start("Loading your mastery path...");

      // Fetch mastery path
      const path = await apiClient.getMasteryPath();

      // Fetch node details for all nodes in the path
      const nodeMap = new Map();
      const allNodeIds = new Set([
        path.currentNode,
        ...path.pathHistory,
        ...path.allowedPaths,
      ]);

      for (const nodeId of allNodeIds) {
        const node = await apiClient.getNode(nodeId);
        nodeMap.set(nodeId, {
          title: node.title,
          difficulty: node.difficulty,
        });
      }

      spinner.stop();

      // Render and display tree
      const tree = renderMasteryTree(
        path.currentNode,
        path.pathHistory,
        path.allowedPaths,
        nodeMap
      );

      console.log("\n" + tree + "\n");

      // Display legend
      console.log(chalk.dim("Legend:"));
      console.log(chalk.dim("  ● = Current node"));
      console.log(chalk.dim("  ✓ = Completed nodes"));
      console.log(chalk.dim("  → = Available next steps\n"));
    } catch (error: any) {
      spinner.fail(error.message);
      process.exit(1);
    }
  });
