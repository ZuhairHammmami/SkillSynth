/**
 * tools/cli/src/commands/unlock.ts
 * 
 * skillsynth unlock <nodeId>
 * Attempt to unlock a node by triggering assessment or project submission flow
 */

import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";
import enquirer from "enquirer";
import { configManager } from "../config";
import { apiClient } from "../api";

export const unlockCommand = new Command("unlock")
  .argument("<nodeId>", "Node ID to unlock")
  .description("Unlock a knowledge node by triggering assessment or project submission")
  .action(async (nodeId: string) => {
    const spinner = ora();

    try {
      // Check authentication
      if (!configManager.isAuthenticated()) {
        console.log(chalk.red("❌ Not authenticated. Run 'skillsynth login' first."));
        process.exit(1);
      }

      spinner.start("Checking unlock requirements...");

      // Fetch node details
      const node = await apiClient.getNode(nodeId);
      const unlockInfo = await apiClient.getUnlockInfo(nodeId);

      spinner.stop();

      console.log(`\n${chalk.bold.cyan(`🔓 Unlocking: ${node.title}`)}\n`);
      console.log(`Difficulty: ${chalk.yellow(node.difficulty)}`);
      console.log(`Description: ${node.description}\n`);

      // Determine what's required
      const requirements: string[] = [];
      if (unlockInfo.requiresQuiz) requirements.push("Quiz Assessment");
      if (unlockInfo.requiresProject) requirements.push("Project Submission");

      if (requirements.length === 0) {
        console.log(chalk.green("✓ Node is already unlocked!"));
        return;
      }

      console.log(chalk.bold("Required to Unlock:"));
      requirements.forEach((req) => console.log(`  • ${req}`));
      console.log("");

      // Prompt user for action
      const { action } = await enquirer.prompt<{ action: string }>([
        {
          type: "select",
          name: "action",
          message: "What would you like to do?",
          choices: [
            unlockInfo.requiresQuiz && { name: "Take Quiz", value: "quiz" },
            unlockInfo.requiresProject && { name: "Submit Project", value: "project" },
            { name: "View Details Online", value: "web" },
            { name: "Cancel", value: "cancel" },
          ].filter(Boolean),
        },
      ]);

      // Handle actions
      if (action === "quiz") {
        const webUrl = `${configManager.getApiUrl()}/quiz/${unlockInfo.quizId}`;
        console.log(chalk.blue(`\n📝 Open this link to take the quiz:\n${webUrl}\n`));
      } else if (action === "project") {
        const webUrl = `${configManager.getApiUrl()}/projects/${unlockInfo.projectId}/submit`;
        console.log(chalk.blue(`\n🚀 Open this link to submit your project:\n${webUrl}\n`));
      } else if (action === "web") {
        const webUrl = `${configManager.getApiUrl()}/nodes/${nodeId}`;
        console.log(chalk.blue(`\n🌐 Open this link for more details:\n${webUrl}\n`));
      } else {
        console.log(chalk.yellow("Cancelled."));
      }
    } catch (error: any) {
      spinner.fail(error.message);
      process.exit(1);
    }
  });
