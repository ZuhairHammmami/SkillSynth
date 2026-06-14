/**
 * tools/cli/src/commands/find.ts
 * 
 * skillsynth find <query>
 * Search for knowledge nodes using semantic/vector search
 */

import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";
import enquirer from "enquirer";
import { configManager } from "../config";
import { apiClient } from "../api";
import { renderSearchResults } from "../utils";

export const findCommand = new Command("find")
  .argument("<query>", "Search query (e.g., 'distributed systems', 'scalable APIs')")
  .option("-l, --limit <number>", "Maximum results to show", "5")
  .description("Search for knowledge nodes using semantic/vector search")
  .action(async (query: string, options: { limit: string }) => {
    const spinner = ora();

    try {
      // Validate query
      if (query.length < 2) {
        console.log(chalk.red("❌ Search query must be at least 2 characters"));
        process.exit(1);
      }

      spinner.start(`Searching for "${query}"...`);

      // Perform search
      const limit = Math.min(parseInt(options.limit, 10), 20);
      const results = await apiClient.searchNodes(query, limit);

      spinner.stop();

      if (results.length === 0) {
        console.log(chalk.yellow(`\n⚠️  No results found for "${query}"`));
        return;
      }

      // Render results
      console.log("\n");
      const formattedResults = results.map((r, idx) => ({
        title: r.title,
        difficulty: r.difficulty,
        relevance: 1 - idx * 0.15, // Mock relevance score
      }));
      console.log(renderSearchResults(formattedResults));

      // Prompt for action
      const { selectedIdx } = await enquirer.prompt<{ selectedIdx: number }>([
        {
          type: "select",
          name: "selectedIdx",
          message: "Select a node to view details:",
          choices: [
            ...results.map((r, idx) => ({
              name: `${idx + 1}. ${r.title} [${r.difficulty}]`,
              value: idx,
            })),
            { name: "Back", value: -1 },
          ],
        },
      ]);

      if (selectedIdx === -1) {
        console.log(chalk.yellow("Cancelled."));
        return;
      }

      // Display selected node
      const selected = results[selectedIdx];
      console.log(`\n${chalk.bold.cyan(selected.title)}`);
      console.log(`Difficulty: ${chalk.yellow(selected.difficulty)}`);
      console.log(`Description: ${selected.description}`);

      // Option to unlock
      const { action } = await enquirer.prompt<{ action: string }>([
        {
          type: "select",
          name: "action",
          choices: [
            { name: "Unlock Node", value: "unlock" },
            { name: "View Online", value: "web" },
            { name: "Back", value: "back" },
          ],
        },
      ]);

      if (action === "unlock") {
        // Delegate to unlock command
        console.log(chalk.blue(`\nRunning: skillsynth unlock ${selected.id}\n`));
        // This would normally call the unlock command, but for now we'll provide the link
        const webUrl = `${configManager.getApiUrl()}/nodes/${selected.id}`;
        console.log(chalk.blue(`Open: ${webUrl}`));
      } else if (action === "web") {
        const webUrl = `${configManager.getApiUrl()}/nodes/${selected.id}`;
        console.log(chalk.blue(`\n🌐 ${webUrl}\n`));
      }
    } catch (error: any) {
      spinner.fail(error.message);
      process.exit(1);
    }
  });
