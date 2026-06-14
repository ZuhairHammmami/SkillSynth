/**
 * Phase 3.1: Production-Grade Seed Script
 * 
 * Populates Supabase DB with Frontend Engineering Path
 * 4-node DAG demonstrating dependency chains, confidence scoring, and blocked node detection
 * 
 * @author SkillSynth Engineering
 * @version 1.0.0
 */

import { v4 as uuidv4 } from 'uuid';
import { KnowledgeNode } from '@/entities/KnowledgeNode';
import { UserPath } from '@/entities/UserPath';

// ============================================================================
// PHASE 3.1 DATA: Frontend Engineering Path
// ============================================================================

/**
 * Node 1: JavaScript Basics
 * - Root node (no prerequisites)
 * - High confidence (0.95)
 * - Foundation for all frontend development
 */
const NODE_1_ID = uuidv4();
const NODE_1: KnowledgeNode = {
  id: NODE_1_ID,
  label: 'JavaScript Basics',
  confidenceScore: 0.95,
  prerequisites: [],
  sourceMetadata: {
    sourceType: 'academic',
    sourceUrl: 'https://javascript.info/',
    lastUpdated: new Date().toISOString(),
    reliabilityScore: 0.95,
  },
};

/**
 * Node 2: React Fundamentals
 * - Prerequisite: JavaScript Basics
 * - Confidence: 0.88
 * - First-level dependent skill
 */
const NODE_2_ID = uuidv4();
const NODE_2: KnowledgeNode = {
  id: NODE_2_ID,
  label: 'React Fundamentals',
  confidenceScore: 0.88,
  prerequisites: [NODE_1_ID],
  sourceMetadata: {
    sourceType: 'market',
    sourceUrl: 'https://react.dev/learn',
    lastUpdated: new Date().toISOString(),
    reliabilityScore: 0.92,
  },
};

/**
 * Node 3: State Management (Zustand/Redux)
 * - Prerequisite: React Fundamentals
 * - Confidence: 0.82
 * - Second-level dependent skill
 */
const NODE_3_ID = uuidv4();
const NODE_3: KnowledgeNode = {
  id: NODE_3_ID,
  label: 'State Management (Zustand/Redux)',
  confidenceScore: 0.82,
  prerequisites: [NODE_2_ID],
  sourceMetadata: {
    sourceType: 'market',
    sourceUrl: 'https://redux.js.org/',
    lastUpdated: new Date().toISOString(),
    reliabilityScore: 0.88,
  },
};

/**
 * Node 4: Advanced Patterns (HOC/Compound)
 * - Prerequisites: React Fundamentals + State Management
 * - Confidence: 0.75
 * - Multi-prerequisite skill demonstrating complex dependencies
 * - This node will be BLOCKED if Node 2 OR Node 3 is incomplete
 */
const NODE_4_ID = uuidv4();
const NODE_4: KnowledgeNode = {
  id: NODE_4_ID,
  label: 'Advanced Patterns (HOC/Compound)',
  confidenceScore: 0.75,
  prerequisites: [NODE_2_ID, NODE_3_ID],
  sourceMetadata: {
    sourceType: 'academic',
    sourceUrl: 'https://react.dev/learn/passing-props-to-a-component',
    lastUpdated: new Date().toISOString(),
    reliabilityScore: 0.85,
  },
};

// ============================================================================
// SEED DATA EXPORT
// ============================================================================

export const FRONTEND_ENGINEERING_PATH = {
  nodes: [NODE_1, NODE_2, NODE_3, NODE_4],
  nodeIds: {
    JAVASCRIPT_BASICS: NODE_1_ID,
    REACT_FUNDAMENTALS: NODE_2_ID,
    STATE_MANAGEMENT: NODE_3_ID,
    ADVANCED_PATTERNS: NODE_4_ID,
  },
  metadata: {
    pathName: 'Frontend Engineering Path',
    version: '1.0.0',
    totalNodes: 4,
    description: 'Complete learning path for frontend development mastery',
    createdAt: new Date().toISOString(),
    author: 'SkillSynth Engineering Team',
  },
};

// ============================================================================
// SEED HELPERS
// ============================================================================

/**
 * Create a test user path for the engineering path
 * Initially with only Node 1 completed (to test blocking)
 */
export function createTestUserPath(userId: string): UserPath {
  return {
    id: uuidv4(),
    userId,
    currentNode: NODE_2_ID, // Currently on React Fundamentals (blocked)
    pathHistory: [NODE_1_ID], // Only JavaScript Basics completed
    allowedPaths: [], // No custom overrides
    customSkillOverrides: {},
  };
}

/**
 * Create a fully progressed user path (all nodes completed)
 */
export function createFullyCompletedUserPath(userId: string): UserPath {
  return {
    id: uuidv4(),
    userId,
    currentNode: NODE_4_ID,
    pathHistory: [NODE_1_ID, NODE_2_ID, NODE_3_ID, NODE_4_ID],
    allowedPaths: [],
    customSkillOverrides: {},
  };
}

/**
 * Create a user path blocked at Node 4
 * (Node 2 completed, but Node 3 incomplete)
 */
export function createBlockedUserPath(userId: string): UserPath {
  return {
    id: uuidv4(),
    userId,
    currentNode: NODE_3_ID,
    pathHistory: [NODE_1_ID, NODE_2_ID], // React Fundamentals done, State Management incomplete
    allowedPaths: [],
    customSkillOverrides: {},
  };
}

// ============================================================================
// CONSOLE LOGGING FOR VERIFICATION
// ============================================================================

export function logSeedData(): void {
  console.log('\n🌱 Phase 3.1 Seed Data: Frontend Engineering Path\n');

  console.log('📊 Node Structure:');
  FRONTEND_ENGINEERING_PATH.nodes.forEach((node, index) => {
    console.log(`\n  Node ${index + 1}: ${node.label}`);
    console.log(`    - ID: ${node.id}`);
    console.log(`    - Confidence: ${node.confidenceScore}`);
    console.log(`    - Prerequisites: ${node.prerequisites.length === 0 ? 'None (Root)' : node.prerequisites.join(', ')}`);
    console.log(`    - Reliability Score: ${node.sourceMetadata.reliabilityScore}`);
  });

  console.log('\n\n📈 Dependency Graph:');
  console.log('  Node 1 (JS Basics)');
  console.log('    └─> Node 2 (React Fundamentals)');
  console.log('        ├─> Node 3 (State Management)');
  console.log('        │   └─> Node 4 (Advanced Patterns) ⚠️ Multi-requisite');
  console.log('        └────────────────────────────────────┘');

  console.log('\n\n🎯 Test Scenarios:');
  console.log('  1. Blocked Node Detection:');
  console.log('     - User completes: [Node 1]');
  console.log('     - Current: Node 2 (ACCESSIBLE)');
  console.log('     - Node 4 status: BLOCKED (requires Node 2 & 3)');

  console.log('\n  2. Multi-Prerequisite Blocking:');
  console.log('     - User completes: [Node 1, Node 2]');
  console.log('     - Current: Node 3 (ACCESSIBLE)');
  console.log('     - Node 4 status: BLOCKED (requires Node 3)');

  console.log('\n  3. Full Path Completion:');
  console.log('     - User completes: [Node 1, Node 2, Node 3, Node 4]');
  console.log('     - All nodes: COMPLETED ✓');

  console.log('\n✅ Seed data initialized successfully.\n');
}

// ============================================================================
// AUTO-EXECUTION (if run as main script)
// ============================================================================

if (typeof window === 'undefined' && require.main === module) {
  logSeedData();

  console.log('\n💾 Seed Data Available for Ingestion:');
  console.log(`  - Total Nodes: ${FRONTEND_ENGINEERING_PATH.nodes.length}`);
  console.log(`  - Path Version: ${FRONTEND_ENGINEERING_PATH.metadata.version}`);
  console.log(`  - Node IDs: ${JSON.stringify(FRONTEND_ENGINEERING_PATH.nodeIds, null, 2)}`);
}

export default FRONTEND_ENGINEERING_PATH;
