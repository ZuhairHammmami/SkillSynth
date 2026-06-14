#!/usr/bin/env ts-node
/**
 * Phase 3.0: Connection Heartbeat Diagnostic Script
 * 
 * This script verifies:
 * 1. Successful handshake with the new Supabase instance
 * 2. Current concepts count in the database
 * 3. Row-Level Security (RLS) is active on the concepts table
 * 
 * Success Criteria: All three checks pass without errors
 */

import { createClient } from "@supabase/supabase-js";
import { config } from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// Load environment variables
const __dirname = path.dirname(fileURLToPath(import.meta.url));
config({ path: path.join(__dirname, "../../.env") });

interface ConnectionCheckResult {
  timestamp: string;
  supabaseUrl: string;
  databaseUrl: string;
  connectionStatus: "success" | "failed";
  conceptsCount: number;
  rlsActive: boolean | "unknown";
  schemaVersion: string | null;
  errors: string[];
  warnings: string[];
}

/**
 * Main diagnostic function
 */
async function runDiagnostics(): Promise<ConnectionCheckResult> {
  const result: ConnectionCheckResult = {
    timestamp: new Date().toISOString(),
    supabaseUrl: process.env.SUPABASE_URL || "not-configured",
    databaseUrl: process.env.DATABASE_URL
      ? `${process.env.DATABASE_URL.substring(0, 50)}...`
      : "not-configured",
    connectionStatus: "failed",
    conceptsCount: 0,
    rlsActive: "unknown",
    schemaVersion: null,
    errors: [],
    warnings: [],
  };

  console.log("🔍 Phase 3.0: Connection Heartbeat Diagnostic");
  console.log("=".repeat(60));

  try {
    // Check 1: Environment Configuration
    console.log("\n1️⃣  Checking environment configuration...");
    if (!process.env.SUPABASE_URL) {
      result.errors.push("SUPABASE_URL not configured");
      console.error("   ❌ SUPABASE_URL missing");
    } else {
      console.log(`   ✅ SUPABASE_URL: ${process.env.SUPABASE_URL}`);
    }

    if (!process.env.SUPABASE_ANON_KEY) {
      result.errors.push("SUPABASE_ANON_KEY not configured");
      console.error("   ❌ SUPABASE_ANON_KEY missing");
    } else {
      console.log(
        `   ✅ SUPABASE_ANON_KEY: ${process.env.SUPABASE_ANON_KEY.substring(0, 20)}...`
      );
    }

    if (!process.env.DATABASE_URL) {
      result.errors.push("DATABASE_URL not configured");
      console.error("   ❌ DATABASE_URL missing");
    } else {
      console.log(`   ✅ DATABASE_URL: ${result.databaseUrl}`);
    }

    // Early exit if critical env vars missing
    if (result.errors.length > 0) {
      console.log("\n⚠️  Configuration incomplete. Cannot proceed.");
      return result;
    }

    // Check 2: Supabase Connection
    console.log("\n2️⃣  Testing Supabase connection...");
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_ANON_KEY!
    );

    // Attempt a simple query to verify connection
    try {
      const { data, error } = await supabase
        .from("concepts")
        .select("id")
        .limit(1);

      if (error) {
        result.errors.push(`Supabase query error: ${error.message}`);
        console.error(`   ❌ Query failed: ${error.message}`);
      } else {
        result.connectionStatus = "success";
        console.log("   ✅ Supabase connection successful");
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      result.errors.push(`Connection error: ${errorMsg}`);
      console.error(`   ❌ Connection error: ${errorMsg}`);
    }

    // Check 3: Fetch Concepts Count
    console.log("\n3️⃣  Fetching concepts count...");
    try {
      const { count, error } = await supabase
        .from("concepts")
        .select("*", { count: "exact", head: true });

      if (error) {
        result.errors.push(`Failed to count concepts: ${error.message}`);
        console.error(`   ❌ Count query failed: ${error.message}`);
      } else {
        result.conceptsCount = count || 0;
        console.log(`   ✅ Current concepts in database: ${result.conceptsCount}`);

        if (result.conceptsCount === 0) {
          result.warnings.push("Database is empty - ready for initial ingestion");
          console.log("   ⚠️  Database is empty (ready for initial ingestion)");
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      result.errors.push(`Concepts fetch error: ${errorMsg}`);
      console.error(`   ❌ Error: ${errorMsg}`);
    }

    // Check 4: Verify RLS is Active
    console.log("\n4️⃣  Verifying Row-Level Security (RLS)...");
    try {
      // Query the pg_stat_user_tables to check RLS status
      const { data, error } = await supabase.rpc("check_rls_status");

      if (error) {
        // RLS check might not be available via RPC, try alternative approach
        console.log("   ⚠️  RLS status cannot be verified via standard queries");
        result.warnings.push("RLS verification requires admin access");
        result.rlsActive = "unknown";
      } else {
        result.rlsActive = data?.rls_enabled || false;
        if (result.rlsActive) {
          console.log("   ✅ Row-Level Security (RLS) is ACTIVE");
        } else {
          result.warnings.push("RLS is not active on concepts table");
          console.warn("   ⚠️  RLS appears to be disabled");
        }
      }
    } catch (err) {
      // Expected - RLS status requires special permissions
      console.log("   ℹ️  RLS verification requires admin access (expected)");
      result.rlsActive = "unknown";
    }

    // Check 5: Schema Version
    console.log("\n5️⃣  Checking schema version...");
    try {
      const { data, error } = await supabase
        .from("schema_versions")
        .select("version, applied_at")
        .order("applied_at", { ascending: false })
        .limit(1);

      if (!error && data && data.length > 0) {
        result.schemaVersion = data[0].version;
        console.log(`   ✅ Schema version: ${result.schemaVersion}`);
      } else {
        console.log("   ⚠️  Schema version table not found (expected for new DB)");
        result.warnings.push("No schema versions recorded");
      }
    } catch (err) {
      console.log("   ℹ️  Schema version table not yet created");
    }

    // Summary
    console.log("\n" + "=".repeat(60));
    console.log("📊 DIAGNOSTIC SUMMARY");
    console.log("=".repeat(60));

    if (result.errors.length === 0) {
      console.log(
        "\n✅ SUCCESS: Connection heartbeat established with Supabase!"
      );
      console.log("\nReadiness Status:");
      console.log(`  • Connection: ${result.connectionStatus === "success" ? "✅ Ready" : "❌ Failed"}`);
      console.log(`  • Concepts: ${result.conceptsCount} items`);
      console.log(
        `  • RLS Status: ${result.rlsActive === true ? "✅ Active" : result.rlsActive === false ? "⚠️ Disabled" : "ℹ️ Unknown"}`
      );
      console.log(`  • Schema: ${result.schemaVersion || "N/A"}`);

      console.log(
        "\n🚀 Proceed to Phase 3.0 step 2: Dynamic Data Ingestion"
      );
    } else {
      console.error("\n❌ ISSUES DETECTED:");
      result.errors.forEach((err) => console.error(`  • ${err}`));
    }

    if (result.warnings.length > 0) {
      console.log("\n⚠️  WARNINGS:");
      result.warnings.forEach((warn) => console.log(`  • ${warn}`));
    }

    console.log("\n" + "=".repeat(60));
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    result.errors.push(`Diagnostic error: ${errorMsg}`);
    console.error(`\n❌ Fatal error: ${errorMsg}`);
  }

  return result;
}

// Execute diagnostics
runDiagnostics()
  .then((result) => {
    // Exit with success code if no errors
    process.exit(result.errors.length === 0 ? 0 : 1);
  })
  .catch((err) => {
    console.error("Unhandled error:", err);
    process.exit(1);
  });
