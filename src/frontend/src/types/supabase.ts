export type Database = {
  public: {
    Tables: {
      concepts: {
        Row: {
          id: string;
          label: string;
          confidence_score: number;
          source_type: string;
          source_url: string | null;
          last_updated: string | null;
          reliability_score: number | null;
          created_at: string | null;
        };
        Insert: {
          id?: string;
          label: string;
          confidence_score: number;
          source_type: string;
          source_url?: string | null;
          last_updated?: string | null;
          reliability_score?: number | null;
          created_at?: string | null;
        };
        Update: {
          id?: string;
          label?: string;
          confidence_score?: number;
          source_type?: string;
          source_url?: string | null;
          last_updated?: string | null;
          reliability_score?: number | null;
          created_at?: string | null;
        };
      };
      user_mastery: {
        Row: {
          id: string;
          user_id: string;
          current_node_id: string | null;
          path_history: string[];
          allowed_paths: string[];
          custom_skill_overrides: Record<string, unknown>;
          created_at: string | null;
          updated_at: string | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          current_node_id?: string | null;
          path_history?: string[];
          allowed_paths?: string[];
          custom_skill_overrides?: Record<string, unknown>;
          created_at?: string | null;
          updated_at?: string | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          current_node_id?: string | null;
          path_history?: string[];
          allowed_paths?: string[];
          custom_skill_overrides?: Record<string, unknown>;
          created_at?: string | null;
          updated_at?: string | null;
        };
      };
      user_path: {
        Row: {
          id: string;
          user_id: string;
          title: string;
          description: string | null;
          nodes: unknown[];
          current_node_id: string | null;
          progress: number;
          completed_at: string | null;
          created_at: string | null;
          updated_at: string | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          title: string;
          description?: string | null;
          nodes?: unknown[];
          current_node_id?: string | null;
          progress?: number;
          completed_at?: string | null;
          created_at?: string | null;
          updated_at?: string | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          title?: string;
          description?: string | null;
          nodes?: unknown[];
          current_node_id?: string | null;
          progress?: number;
          completed_at?: string | null;
          created_at?: string | null;
          updated_at?: string | null;
        };
      };
      assessment_results: {
        Row: {
          id: string;
          user_id: string;
          concept_id: string;
          score: number;
          total_questions: number;
          correct_answers: number;
          attempt_number: number;
          passed: boolean;
          time_spent_seconds: number | null;
          answers: Record<string, unknown>;
          created_at: string | null;
          updated_at: string | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          concept_id: string;
          score: number;
          total_questions?: number;
          correct_answers: number;
          attempt_number?: number;
          passed?: boolean;
          time_spent_seconds?: number | null;
          answers?: Record<string, unknown>;
          created_at?: string | null;
          updated_at?: string | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          concept_id?: string;
          score?: number;
          total_questions?: number;
          correct_answers?: number;
          attempt_number?: number;
          passed?: boolean;
          time_spent_seconds?: number | null;
          answers?: Record<string, unknown>;
          created_at?: string | null;
          updated_at?: string | null;
        };
      };
    };
    Views: {};
    Functions: {};
    Enums: {};
  };
};

export type Tables<T extends keyof Database["public"]["Tables"]> = Database["public"]["Tables"][T]["Row"];
export type InsertTables<T extends keyof Database["public"]["Tables"]> = Database["public"]["Tables"][T]["Insert"];
export type UpdateTables<T extends keyof Database["public"]["Tables"]> = Database["public"]["Tables"][T]["Update"];