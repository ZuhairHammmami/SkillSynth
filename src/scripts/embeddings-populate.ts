/**
 * src/scripts/embeddings-populate.ts
 * 
 * Populate Embeddings for Existing Knowledge Nodes
 * 
 * This script generates and stores embeddings for all knowledge nodes
 * in the database. It uses the VectorSearchService with the hybrid provider.
 * 
 * Usage:
 *   npx ts-node src/scripts/embeddings-populate.ts
 * 
 * Options:
 *   --batch-size=50        Number of concepts to process per batch
 *   --provider=hybrid      Force provider: openai, local, or hybrid
 *   --dry-run             Show what would be done without actually doing it
 */

import * as fs from "fs";
import * as path from "path";
import { VectorSearchService } from "../services/VectorSearchService";
import { Database } from "../backend/lib/db";

interface Options {
  batchSize: number;
  provider?: "openai" | "local" | "hybrid";
  dryRun: boolean;
}

const parseArgs = (): Options => {
  const args = process.argv.slice(2);
  const options: Options = {
    batchSize: 50,
    dryRun: false,
  };

  for (const arg of args) {
    if (arg.startsWith("--batch-size=")) {
      options.batchSize = parseInt(arg.split("=")[1]);
    } else if (arg.startsWith("--provider=")) {
      options.provider = arg.split("=")[1] as "openai" | "local" | "hybrid";
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    }
  }

  return options;
};

const main = async () => {
  const options = parseArgs();

  console.log("🚀 SkillSynth Vector Embeddings Population Script");
  console.log("================================================\n");

  if (options.dryRun) {
    console.log("📋 DRY RUN MODE - No changes will be made\n");
  }

  console.log(`Configuration:`);
  console.log(`  Batch Size: ${options.batchSize}`);
  console.log(`  Provider: ${options.provider || process.env.EMBEDDING_PROVIDER || "hybrid"}`);
  console.log(`  API URL: ${process.env.DATABASE_URL ? "✓ Configured" : "✗ Not configured"}\n`);

  // Validate configuration
  if (!process.env.DATABASE_URL) {
    console.error("❌ DATABASE_URL not configured in .env");
    process.exit(1);
  }

  if (!process.env.OPENAI_API_KEY && (process.env.EMBEDDING_PROVIDER || "hybrid") !== "local") {
    console.warn("⚠️  OPENAI_API_KEY not configured - will attempt local provider only\n");
  }

  try {
    const db = new Database();
    const vectorSearch = new VectorSearchService(db);

    // Fetch all concepts
    console.log("📚 Fetching concepts from database...");
    const conceptResult = await db.query(
      `SELECT id, title, description FROM concepts ORDER BY created_at DESC`
    );
    const concepts = conceptResult.rows;

    console.log(`   Found ${concepts.length} concepts\n`);

    if (concepts.length === 0) {
      console.warn("⚠️  No concepts found to embed");
      return;
    }

    // Check existing embeddings
    console.log("🔍 Checking existing embeddings...");
    const existingResult = await db.query(
      `SELECT DISTINCT concept_id FROM concept_embeddings`
    );
    const embeddedConceptIds = new Set(
      existingResult.rows.map((r) => r.concept_id)
    );

    const newConcepts = concepts.filter(
      (c) => !embeddedConceptIds.has(c.id)
    );

    console.log(`   Already embedded: ${embeddedConceptIds.size}`);
    console.log(`   Needs embedding: ${newConcepts.length}\n`);

    if (newConcepts.length === 0) {
      console.log("✅ All concepts are already embedded!");
      return;
    }

    // Process in batches
    let processed = 0;
    let successful = 0;
    let failed = 0;
    let totalCost = 0;

    for (let i = 0; i < newConcepts.length; i += options.batchSize) {
      const batch = newConcepts.slice(i, i + options.batchSize);
      const batchNum = Math.floor(i / options.batchSize) + 1;
      const totalBatches = Math.ceil(newConcepts.length / options.batchSize);

      console.log(`\n📦 Processing batch ${batchNum}/${totalBatches} (${batch.length} concepts)...`);

      if (!options.dryRun) {
        try {
          const result = await vectorSearch.generateEmbeddingsForConcepts(
            batch.map((c) => c.id)
          );

          successful += result.successful;
          failed += result.failed;
          totalCost += result.cost;
          processed += batch.length;

          console.log(`   ✓ ${result.successful} successful, ${result.failed} failed`);
          console.log(`   💰 Cost: $${result.cost.toFixed(4)}`);

          // Progress indicator
          const progress = Math.floor((processed / newConcepts.length) * 100);
          console.log(`   Progress: ${processed}/${newConcepts.length} (${progress}%)`);
        } catch (error: any) {
          console.error(`   ❌ Batch failed: ${error.message}`);
          failed += batch.length;
        }
      } else {
        console.log(`   [DRY RUN] Would process ${batch.length} concepts`);
        processed += batch.length;
      }
    }

    // Summary
    console.log("\n" + "=".repeat(50));
    console.log("✅ Embedding Population Complete!");
    console.log("=".repeat(50));

    if (!options.dryRun) {
      console.log(`\nResults:`);
      console.log(`  Total Processed: ${processed}`);
      console.log(`  Successful: ${successful}`);
      console.log(`  Failed: ${failed}`);
      console.log(`  Total Cost: $${totalCost.toFixed(4)}`);

      const avgCostPerConcept = (totalCost / (successful || 1)).toFixed(4);
      console.log(`  Average Cost per Concept: $${avgCostPerConcept}`);
    } else {
      console.log(`\n[DRY RUN] Would have processed ${processed} concepts`);
    }

    console.log("\n📝 Next Steps:");
    console.log("  1. Verify embeddings: SELECT COUNT(*) FROM concept_embeddings;");
    console.log("  2. Test search: GET /api/search/discover?query=distributed%20systems");
    console.log("  3. Monitor costs: SELECT SUM(total_cost_usd) FROM embedding_metadata;");

    process.exit(0);
  } catch (error: any) {
    console.error("\n❌ Error during embedding population:");
    console.error(error);
    process.exit(1);
  }
};

main();
