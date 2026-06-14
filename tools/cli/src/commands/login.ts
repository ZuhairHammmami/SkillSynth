/**
 * tools/cli/src/commands/login.ts
 * 
 * skillsynth login
 * Authenticate using Personal Access Token (PAT)
 */

import { Command } from "commander";
import enquirer from "enquirer";
import chalk from "chalk";
import ora from "ora";
import { configManager } from "../config";
import { apiClient } from "../api";

export const loginCommand = new Command("login")
  .description("Authenticate with your Personal Access Token (PAT)")
  .action(async () => {
    const spinner = ora();

    try {
      // Check if already authenticated
      if (configManager.isAuthenticated()) {
        const currentUser = configManager.getUserId();
        const shouldRelogin = await enquirer.prompt<{ relogin: boolean }>([
          {
            type: "confirm",
            name: "relogin",
            message: `Already authenticated as ${currentUser}. Login again?`,
            initial: false,
          },
        ]);

        if (!shouldRelogin.relogin) {
          console.log(chalk.green("✓ Already authenticated"));
          return;
        }
      }

      // Prompt for token
      const { token } = await enquirer.prompt<{ token: string }>([
        {
          type: "password",
          name: "token",
          message: "Enter your Personal Access Token (PAT):",
          validate: (val: string) => {
            if (!val || val.length < 10) return "Invalid token";
            return true;
          },
        },
      ]);

      spinner.start("Verifying token...");

      // Authenticate via API
      const result = await apiClient.authenticate(token);

      spinner.succeed(`Authenticated as ${result.email}`);
      console.log(chalk.green(`✓ User ID: ${result.userId}`));
      console.log(chalk.green("✓ Configuration saved to ~/.config/skillsynth/config.json"));
    } catch (error: any) {
      spinner.fail(error.message);
      process.exit(1);
    }
  });
