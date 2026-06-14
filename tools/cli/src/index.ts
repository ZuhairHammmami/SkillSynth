#!/usr/bin/env node
/**
 * tools/cli/src/index.ts
 * 
 * SkillSynth CLI - Main Entry Point
 * 
 * Usage:
 *   skillsynth login                          - Authenticate with PAT
 *   skillsynth path                           - Display mastery path
 *   skillsynth unlock <nodeId>                - Unlock a node
 *   skillsynth find <query>                   - Search for nodes
 */

import { Program } from "commander";
import chalk from "chalk";
import { loginCommand } from "./commands/login";
import { pathCommand } from "./commands/path";
import { unlockCommand } from "./commands/unlock";
import { findCommand } from "./commands/find";

const program = new Program();

program
  .name("skillsynth")
  .description(chalk.bold.cyan("🚀 SkillSynth Terminal - Engineer's Interface for Mastery Paths"))
  .version("1.0.0")
  .helpOption("-h, --help", "Display help for command");

// Register commands
program.addCommand(loginCommand);
program.addCommand(pathCommand);
program.addCommand(unlockCommand);
program.addCommand(findCommand);

// Add default help
program.action(() => {
  program.outputHelp();
});

// Parse and execute
program.parse(process.argv);

// Show help if no args
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
