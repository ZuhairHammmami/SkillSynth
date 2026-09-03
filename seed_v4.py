#!/usr/bin/env python3
"""seed_v4.py — deterministic 15-table seed (superset of seed_v3).

Ports the canonical static data from seed_v3.py and extends it with richer
topics, 3 additional learner users, ~50 new skills, ~140 additional
prerequisite edges, ~55 more resources (incl. Arabic), 7 more learning paths,
weak-points data on user_skills, and a Kahn topological-order validation of the
global skill DAG (raises SystemExit on cycle, otherwise prints the order).

Run: PYTHONPATH=src python seed_v4.py  (drop/create + insert + FK gate +
per-table count printout + kahn order). Idempotent: run twice -> identical.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datetime import datetime, timedelta, UTC  # noqa: E402
import json  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from sqlalchemy import text  # noqa: E402

from backend.entities.base import Base  # noqa: E402
from backend.entities import (  # noqa: E402
    ActivityLog,
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
    Category,
    JobRole,
    JobRoleSkill,
    Path,
    PathStep,
    Resource,
    Skill,
    SkillPrerequisite,
    StepProgress,
    User,
    UserSkill,
)
from backend.services.auth_service import hash_password  # noqa: E402

# ──────────────────────────────────────────────────────────────────────
# Static data (ported verbatim from seed_v3.py, then extended)
# ──────────────────────────────────────────────────────────────────────

USERS = [
    ("admin@skillsynth.io", "Admin@123456", "Super Admin", True),
    ("veteran@skillsynth.io", "Veteran@123456", "Veteran User", False),
    ("demo@demo.com", "demo123", "Demo User", False),
    ("editor@skillsynth.io", "Editor@123456", "Editor User", False),
    ("student2@skillsynth.io", "Student@123456", "Student Two", False),
    ("learner1@skillsynth.io", "Learner@123456", "Learner One", False),
    ("learner2@skillsynth.io", "Learner@123456", "Learner Two", False),
    ("learner3@skillsynth.io", "Learner@123456", "Learner Three", False),
]

QUESTION_BANK = {
    "HTML": [
        {"question": "What does HTML stand for?", "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"], "correct": 0},
        {"question": "Which tag creates a hyperlink?", "options": ["<link>", "<a>", "<href>", "<nav>"], "correct": 1},
        {"question": "What is the correct HTML for inserting an image?", "options": ["<img src='image.jpg' alt='My Image'>", "<image src='image.jpg'>", "<img alt='My Image'>image.jpg</img>", "<img href='image.jpg'>"], "correct": 0},
        {"question": "Which HTML element is used for the largest heading?", "options": ["<h1>", "<heading>", "<h6>", "<head>"], "correct": 0},
        {"question": "What does the <article> tag represent?", "options": ["A self-contained composition", "A navigation menu", "An article in a blog", "A sidebar"], "correct": 0},
    ],
    "CSS": [
        {"question": "What does CSS stand for?", "options": ["Cascading Style Sheets", "Creative Style System", "Computer Style Sheets", "Colorful Style Sheets"], "correct": 0},
        {"question": "Which property changes the background color?", "options": ["background-color", "color", "bgcolor", "background"], "correct": 0},
        {"question": "What does 'display: flex' do?", "options": ["Creates a flex container", "Makes text flexible", "Hides the element", "Adds spacing"], "correct": 0},
        {"question": "Which CSS property controls the text size?", "options": ["font-size", "text-size", "font-style", "text-style"], "correct": 0},
        {"question": "What is the box model composed of?", "options": ["Content, Padding, Border, Margin", "Content, Margin, Padding", "Width, Height, Depth", "Inner, Outer, Border"], "correct": 0},
    ],
    "JavaScript": [
        {"question": "Which keyword declares a constant variable?", "options": ["const", "let", "var", "static"], "correct": 0},
        {"question": "What does 'typeof' operator return for an array?", "options": ["object", "array", "undefined", "list"], "correct": 0},
        {"question": "Which method adds an element to the end of an array?", "options": ["push()", "pop()", "shift()", "unshift()"], "correct": 0},
        {"question": "What is a closure?", "options": ["A function with access to its outer scope", "A closed function", "A private variable", "A loop construct"], "correct": 0},
        {"question": "What does '===' do?", "options": ["Strict equality (type + value)", "Loose equality", "Assignment", "Comparison"], "correct": 0},
    ],
    "TypeScript": [
        {"question": "How do you specify a number type in TypeScript?", "options": [": number", ": int", ": float", ": numeric"], "correct": 0},
        {"question": "What does 'any' type mean?", "options": ["Opt out of type checking", "Any value allowed but checked", "A generic type", "A union of all types"], "correct": 0},
        {"question": "What is an interface in TypeScript?", "options": ["A structure for object shapes", "A class implementation", "A function type", "A module"], "correct": 0},
        {"question": "What are generics used for?", "options": ["Reusable components with multiple types", "Creating generic functions", "Type aliases", "Module imports"], "correct": 0},
        {"question": "What does 'readonly' modifier do?", "options": ["Prevents property modification after init", "Makes property read-only in class", "Creates a constant", "Prevents serialization"], "correct": 0},
    ],
    "React": [
        {"question": "What is JSX?", "options": ["JavaScript XML syntax extension", "A state management tool", "A React component", "A build tool"], "correct": 0},
        {"question": "What hook manages state in React?", "options": ["useState", "useEffect", "useContext", "useReducer"], "correct": 0},
        {"question": "What does useEffect handle?", "options": ["Side effects", "State changes", "Rendering", "Event handling"], "correct": 0},
        {"question": "What is virtual DOM?", "options": ["Lightweight copy of real DOM for performance", "A separate DOM for React", "A browser API", "A rendering engine"], "correct": 0},
        {"question": "How do you pass data from parent to child?", "options": ["Props", "State", "Context", "Refs"], "correct": 0},
    ],
}

def _validate_question_bank():
    """Assert all question bank entries have valid correct indices."""
    for questions in QUESTION_BANK.values():
        for entry in questions:
            assert isinstance(entry.get("correct"), int), f"bad correct type: {entry['question']}"
            assert 0 <= entry["correct"] < len(entry["options"]), (
                f"correct index {entry['correct']} out of range for {len(entry['options'])} options: {entry['question']}"
            )

_validate_question_bank()

# Detailed sub-topics for major skills; everything else falls back to
# [name] + [c for c in cats if c != name] (see _seed_skills).
TOPICS = {
    "JavaScript": ["Variables", "Functions", "Closures", "Async/Await", "DOM", "ES6 Modules"],
    "CSS": ["Selectors", "Box Model", "Flexbox", "Grid", "Responsive", "Animations"],
    "Python": ["Syntax", "Data Types", "Functions", "OOP", "Decorators", "Async IO"],
    "React": ["JSX", "Components", "Hooks", "State", "Effects", "Context", "Routing"],
    "HTML": ["Semantics", "Forms", "Media", "Accessibility", "Metadata"],
    "TypeScript": ["Types", "Interfaces", "Generics", "Enums", "Decorators", "Modules"],
    "Node.js": ["Event Loop", "Streams", "Modules", "npm", "CLI", "HTTP"],
    "Docker": ["Images", "Containers", "Volumes", "Networks", "Compose", "Registry"],
    "Kubernetes": ["Pods", "Services", "Deployments", "Ingress", "ConfigMap", "Operators"],
    "PostgreSQL": ["Schema", "Joins", "Indexes", "Transactions", "Functions", "Replication"],
    "MongoDB": ["Documents", "Collections", "Aggregation", "Indexes", "Sharding", "Atlas"],
    "Redis": ["Strings", "Hashes", "Lists", "Sets", "Pub/Sub", "Persistence"],
    "AWS": ["EC2", "S3", "Lambda", "RDS", "IAM", "CloudWatch"],
    "Linux": ["Shell", "Permissions", "Processes", "Networking", "Cron", "Systemd"],
    "Git": ["Commits", "Branches", "Merging", "Rebasing", "Remotes", "Hooks"],
    "GraphQL": ["Schema", "Resolvers", "Queries", "Mutations", "Subscriptions", "Federation"],
    "Vue.js": ["Templates", "Reactivity", "Components", "Composables", "Router", "Pinia"],
    "Angular": ["Components", "Modules", "Services", "RxJS", "Forms", "CLI"],
    "Svelte": ["Reactivity", "Components", "Stores", "Transitions", "Actions", "Kit"],
    "Next.js": ["Routing", "SSR", "SSG", "API Routes", "Middleware", "Images"],
    "Express.js": ["Routing", "Middleware", "Validation", "Auth", "Error Handling", "Static"],
    "Django": ["ORM", "Views", "Templates", "Admin", "Forms", "Migrations"],
    "FastAPI": ["Routing", "Pydantic", "Dependency Injection", "Auth", "Docs", "Async"],
    "Flask": ["Routing", "Blueprints", "Context", "Jinja", "Extensions", "Config"],
    "Terraform": ["Resources", "Modules", "State", "Providers", "Variables", "Outputs"],
    "Ansible": ["Playbooks", "Roles", "Inventory", "Modules", "Handlers", "Vars"],
    "Jenkins": ["Pipelines", "Stages", "Agents", "Credentials", "Plugins", "Webhooks"],
    "Selenium": ["Locators", "Waits", "Actions", "Grid", "Page Objects", "Drivers"],
    "Cypress": ["Commands", "Assertions", "Hooks", "Fixtures", "Network", "Plugins"],
    "Pandas": ["DataFrames", "Indexing", "GroupBy", "Merge", "Reshape", "IO"],
    "NumPy": ["Arrays", "Broadcasting", "Indexing", "Ufuncs", "Linear Algebra", "Random"],
    "TensorFlow": ["Tensors", "Graphs", "Keras", "Training", "Serving", "Distributed"],
    "PyTorch": ["Tensors", "Autograd", "Modules", "Training", "CUDA", "TorchScript"],
    "Swift": ["Syntax", "Optionals", "Protocols", "Structs", "Closures", "Concurrency"],
    "Kotlin": ["Syntax", "Null Safety", "Coroutines", "Extensions", "Sealed Classes", "DSL"],
    "Figma": ["Frames", "Components", "Auto Layout", "Variants", "Prototyping", "Dev Mode"],
    "UI/UX Design Principles": ["Hierarchy", "Contrast", "Alignment", "Proximity", "Color", "Typography"],
    "Jest": ["Matchers", "Mocks", "Snapshots", "Hooks", "Coverage", "Watch"],
    "pytest": ["Fixtures", "Parametrize", "Marks", "Assertions", "Plugins", "Coverage"],
    "Go": ["Syntax", "Goroutines", "Channels", "Interfaces", "Modules", "Testing"],
    "Rust": ["Ownership", "Borrowing", "Traits", "Lifetimes", "Pattern Matching", "Cargo"],
    "Java": ["Syntax", "OOP", "Streams", "Collections", "JVM", "Concurrency"],
    "Deno": ["Permissions", "Modules", "Std Library", "Testing", "Linting", "Format"],
    "NestJS": ["Modules", "Controllers", "Services", "DI", "Pipes", "Guards"],
    "Prisma": ["Schema", "Migrations", "Client", "Relations", "Seeding", "Studio"],
    "Kafka": ["Topics", "Producers", "Consumers", "Partitions", "Brokers", "Streams"],
    "RabbitMQ": ["Exchanges", "Queues", "Bindings", "Routing", "Pub/Sub", "Dead Letter"],
    "Grafana": ["Dashboards", "Panels", "Queries", "Alerts", "Variables", "Plugins"],
    "Prometheus": ["Metrics", "Queries", "Alerts", "Exporters", "Targets", "Storage"],
    "Vault": ["Secrets", "Policies", "Auth Methods", "Dynamic Secrets", "Transit", "KV"],
    "Helm": ["Charts", "Templates", "Values", "Releases", "Hooks", "Repositories"],
    "Istio": ["Sidecar", "Gateways", "Virtual Services", "Destination Rules", "mTLS", "Telemetry"],
    "Snowflake": ["Warehouses", "Stages", "Tables", "Streams", "Tasks", "Sharing"],
    "dbt": ["Models", "Sources", "Tests", "Snapshots", "Macros", "Docs"],
    "Airflow": ["DAGs", "Operators", "Schedules", "Sensors", "XCom", "Pools"],
    "Spark": ["RDDs", "DataFrames", "SQL", "Streaming", "MLlib", "Catalyst"],
    "Keras": ["Layers", "Models", "Training", "Callbacks", "Sequential", "Functional"],
    "XGBoost": ["Trees", "Boosting", "Params", "CV", "Early Stop", "Feature Importance"],
    "Plotly": ["Figures", "Traces", "Layout", "Subplots", "Express", "Dash"],
    "Three.js": ["Scene", "Camera", "Renderer", "Geometry", "Material", "Lights"],
    "WebGL": ["Context", "Shaders", "Buffers", "Textures", "Matrices", "Programs"],
    "Sass": ["Variables", "Nesting", "Mixins", "Functions", "Modules", "Control"],
    "Less": ["Variables", "Nesting", "Mixins", "Functions", "Operations", "Imports"],
    "Storybook": ["Stories", "Controls", "Actions", "Decorators", "Addons", "Docs"],
    "Vitest": ["Config", "Suites", "Mocks", "Coverage", "Watch", "Snapshots"],
    "Testing Library": ["Queries", "Events", "Async", "Mocks", "Roles", "FireEvent"],
    "AXIOS": ["Requests", "Interceptors", "Cancel", "Config", "Adapters", "Errors"],
    "Zod": ["Schemas", "Parsing", "Inference", "Refinements", "Effects", "Errors"],
    "tRPC": ["Routers", "Procedures", "Context", "Middlewares", "Clients", "Types"],
    "Drizzle": ["Schema", "Queries", "Migrations", "Relations", "Filters", "Transactions"],
    "Redis Pub/Sub": ["Channels", "Publish", "Subscribe", "Patterns", "Messages", "Clients"],
    "gRPC": ["Services", "Messages", "Streaming", "Interceptors", "Channels", "Codegen"],
    "OAuth2": ["Authorization Code", "Tokens", "Scopes", "Refresh", "PKCE", "Clients"],
    "JWT Auth": ["Tokens", "Signing", "Verification", "Claims", "Expiry", "Refresh"],
    "Rate Limiting": ["Tokens", "Windows", "Algorithms", "Headers", "Backoff", "Thresholds"],
    "WebSockets": ["Handshake", "Frames", "Events", "Heartbeat", "Binary", "Close"],
    "Service Workers": ["Lifecycle", "Cache", "Fetch", "Events", "Sync", "Push"],
    "PWA": ["Manifest", "Install", "Offline", "Notifications", "Caching", "Audits"],
    "WASM": ["Modules", "Memory", "Tables", "Imports", "Exports", "Linear"],
    "Bun": ["Runtime", "Bundler", "Test", "Transpiler", "Package Manager", "HTTP"],
    "Electron": ["Main", "Renderer", "IPC", "Packaging", "Auto Update", "Tray"],
    "Capacitor": ["Plugins", "Native", "Bridge", "Config", "Live Reload", "Build"],
    "Expo": ["Components", "Router", "Modules", "Build", "Updates", "Native"],
    "SwiftUI": ["Views", "State", "Bindings", "Layout", "Navigation", "Animations"],
    "Jetpack Compose": ["Composables", "State", "Layout", "Modifiers", "Navigation", "Animation"],
    "KMM": ["Shared", "Expect", "Actual", "Coroutines", "Platform", "Gradle"],
    "Go Modules": ["Init", "Versions", "Proxy", "Sum", "Replace", "Tidy"],
    "Rust Macros": ["Declarative", "Procedural", "Attributes", "Metavars", "Hygiene", "Derive"],
    "Rust Async": ["Futures", "Await", "Tokio", "Streams", "Channels", "Tasks"],
    "SQL Tuning": ["Explain", "Plans", "Joins", "Filters", "Statistics", "Rewrites"],
    "Indexing": ["B-Tree", "Composite", "Covering", "Partial", "Unique", "Maintenance"],
    "GraphQL Subscriptions": ["Schema", "Resolver", "Transport", "Filtering", "Scalability", "Auth"],
}

CATEGORIES = [
    "Web Development", "Backend Development", "Databases", "DevOps",
    "Mobile Development", "AI & Machine Learning", "Design",
    "Testing & QA", "Programming Languages", "Cloud & Infrastructure",
    "Data Science", "Security", "Game Development", "Blockchain",
    "Soft Skills", "Tools & Utilities",
]

SKILLS = [
    ("HTML", "Hypertext Markup Language for structuring web content", 1, "html5", "#E34F26", 8, ["Web Development"]),
    ("CSS", "Cascading Style Sheets for styling web pages", 1, "css3", "#1572B6", 10, ["Web Development"]),
    ("JavaScript", "Dynamic programming language for web interactivity", 2, "javascript", "#F7DF1E", 20, ["Web Development", "Programming Languages"]),
    ("TypeScript", "Typed superset of JavaScript that compiles to plain JS", 3, "typescript", "#3178C6", 15, ["Web Development", "Programming Languages"]),
    ("React", "Component-based UI library for building user interfaces", 3, "react", "#61DAFB", 25, ["Web Development"]),
    ("Vue.js", "Progressive JavaScript framework for building UIs", 2, "vuejs", "#4FC08D", 20, ["Web Development"]),
    ("Angular", "Platform for building mobile and desktop web applications", 3, "angular", "#DD0031", 25, ["Web Development"]),
    ("Svelte", "Cybernetically enhanced web framework that compiles at build time", 3, "svelte", "#FF3E00", 15, ["Web Development"]),
    ("Next.js", "React framework with SSR, SSG, and API routes", 3, "nextjs", "#000000", 20, ["Web Development"]),
    ("Nuxt.js", "Vue.js framework with SSR, SSG, and file-system routing", 3, "nuxtjs", "#00DC82", 20, ["Web Development"]),
    ("Tailwind CSS", "Utility-first CSS framework for rapid UI development", 2, "tailwindcss", "#06B6D4", 10, ["Web Development"]),
    ("Bootstrap", "Popular CSS framework for responsive, mobile-first sites", 1, "bootstrap", "#7952B3", 8, ["Web Development"]),
    ("Redux", "Predictable state container for JavaScript apps", 3, "redux", "#764ABC", 12, ["Web Development"]),
    ("GraphQL", "Query language for APIs and runtime for executing queries", 3, "graphql", "#E10098", 15, ["Web Development", "Backend Development"]),
    ("Webpack", "Static module bundler for JavaScript applications", 3, "webpack", "#8DD6F9", 10, ["Web Development", "Tools & Utilities"]),
    ("Vite", "Next-gen frontend build tool for faster development", 2, "vite", "#646CFF", 6, ["Web Development", "Tools & Utilities"]),
    ("Node.js", "JavaScript runtime built on Chrome's V8 engine for server-side apps", 2, "nodejs", "#339933", 20, ["Backend Development", "Programming Languages"]),
    ("Express.js", "Fast, unopinionated Node.js web framework", 2, "express", "#000000", 15, ["Backend Development"]),
    ("Python", "High-level general-purpose programming language", 1, "python", "#3776AB", 20, ["Backend Development", "Programming Languages", "Data Science"]),
    ("FastAPI", "Modern Python web framework for building APIs", 2, "fastapi", "#009688", 12, ["Backend Development"]),
    ("Django", "High-level Python web framework for rapid development", 2, "django", "#092E20", 20, ["Backend Development"]),
    ("Flask", "Lightweight Python web framework for simple applications", 1, "flask", "#000000", 10, ["Backend Development"]),
    ("REST API Design", "Architectural style for designing networked applications", 2, "restapi", "#25A162", 12, ["Backend Development"]),
    ("PostgreSQL", "Advanced open-source relational database system", 2, "postgresql", "#4169E1", 20, ["Databases"]),
    ("MySQL", "Popular open-source relational database management system", 2, "mysql", "#4479A1", 15, ["Databases"]),
    ("MongoDB", "NoSQL document-oriented database for modern apps", 2, "mongodb", "#47A248", 15, ["Databases"]),
    ("Redis", "In-memory data structure store used as cache and message broker", 2, "redis", "#DC382D", 10, ["Databases"]),
    ("SQLite", "Self-contained, serverless relational database engine", 1, "sqlite", "#003B57", 5, ["Databases"]),
    ("Docker", "Platform for developing and running containerized applications", 2, "docker", "#2496ED", 15, ["DevOps"]),
    ("Kubernetes", "Container orchestration platform for automated deployment", 4, "kubernetes", "#326CE5", 30, ["DevOps"]),
    ("AWS", "Amazon Web Services cloud computing platform", 3, "aws", "#FF9900", 30, ["Cloud & Infrastructure", "DevOps"]),
    ("Google Cloud", "Google's suite of cloud computing services", 3, "gcp", "#4285F4", 25, ["Cloud & Infrastructure", "DevOps"]),
    ("Azure", "Microsoft's cloud computing platform and services", 3, "azure", "#0078D4", 25, ["Cloud & Infrastructure", "DevOps"]),
    ("Terraform", "Infrastructure as Code tool by HashiCorp", 3, "terraform", "#7B42BC", 20, ["DevOps"]),
    ("Ansible", "Automation tool for configuration management and deployment", 2, "ansible", "#EE0000", 15, ["DevOps"]),
    ("Jenkins", "Open-source automation server for CI/CD", 3, "jenkins", "#D24939", 15, ["DevOps"]),
    ("GitHub Actions", "CI/CD platform integrated with GitHub", 2, "githubactions", "#2088FF", 10, ["DevOps"]),
    ("GitLab CI", "CI/CD tool built into GitLab", 2, "gitlabci", "#FC6D26", 10, ["DevOps"]),
    ("Linux", "Open-source operating system and command-line proficiency", 2, "linux", "#FCC624", 20, ["DevOps", "Tools & Utilities"]),
    ("React Native", "Framework for building native mobile apps with React", 3, "reactnative", "#61DAFB", 25, ["Mobile Development"]),
    ("Flutter", "Google's UI toolkit for building natively compiled mobile apps", 3, "flutter", "#02569B", 20, ["Mobile Development"]),
    ("Swift", "Apple's programming language for iOS development", 3, "swift", "#F05138", 20, ["Mobile Development", "Programming Languages"]),
    ("iOS Development", "Building applications for Apple's iOS platform", 3, "ios", "#000000", 30, ["Mobile Development"]),
    ("Android Development", "Building applications for the Android platform", 3, "android", "#3DDC84", 30, ["Mobile Development"]),
    ("Kotlin", "Cross-platform language on JVM, used for Android and backend", 3, "kotlin", "#7F52FF", 20, ["Mobile Development", "Backend Development", "Programming Languages"]),
    ("TensorFlow", "Open-source ML platform by Google for deep learning", 4, "tensorflow", "#FF6F00", 30, ["AI & Machine Learning"]),
    ("PyTorch", "Open-source ML framework by Facebook for deep learning", 4, "pytorch", "#EE4C2C", 30, ["AI & Machine Learning"]),
    ("scikit-learn", "ML library for Python with classic algorithms", 3, "scikitlearn", "#F7931E", 20, ["AI & Machine Learning", "Data Science"]),
    ("Pandas", "Python library for data manipulation and analysis", 2, "pandas", "#150458", 15, ["Data Science", "AI & Machine Learning"]),
    ("NumPy", "Python library for numerical computing", 2, "numpy", "#013243", 10, ["Data Science", "AI & Machine Learning"]),
    ("LangChain", "Framework for developing LLM-powered applications", 3, "langchain", "#1C3C3C", 15, ["AI & Machine Learning"]),
    ("OpenAI API", "API for integrating GPT models into applications", 2, "openai", "#412991", 10, ["AI & Machine Learning"]),
    ("Hugging Face", "Platform for sharing and using transformer models", 3, "huggingface", "#FFD21E", 12, ["AI & Machine Learning"]),
    ("Natural Language Processing", "AI field focused on processing human language", 4, "nlp", "#4285F4", 30, ["AI & Machine Learning"]),
    ("Computer Vision", "AI field for enabling machines to interpret visual data", 4, "computervision", "#34A853", 30, ["AI & Machine Learning"]),
    ("Jupyter Notebooks", "Interactive computing environment for data science", 1, "jupyter", "#F37626", 5, ["Data Science", "Tools & Utilities"]),
    ("Matplotlib", "Python plotting library for data visualization", 2, "matplotlib", "#11557C", 8, ["Data Science"]),
    ("Figma", "Collaborative interface design tool", 2, "figma", "#F24E1E", 15, ["Design"]),
    ("Adobe XD", "Adobe's vector-based design and prototyping tool", 2, "adobexd", "#FF61F6", 12, ["Design"]),
    ("UI/UX Design Principles", "Fundamentals of user interface and experience design", 2, "uiux", "#FF3366", 15, ["Design"]),
    ("Wireframing", "Creating low-fidelity visual guides for app layout", 1, "wireframe", "#666666", 6, ["Design"]),
    ("Prototyping", "Creating interactive mockups for user testing", 2, "prototyping", "#FF6B35", 10, ["Design"]),
    ("Design Systems", "Comprehensive set of design standards and components", 3, "designsystems", "#1E1E1E", 20, ["Design"]),
    ("Accessibility (a11y)", "Designing for users with disabilities", 2, "a11y", "#005A9C", 10, ["Design", "Web Development"]),
    ("Responsive Design", "Designing websites that work on all screen sizes", 2, "responsive", "#4285F4", 10, ["Design", "Web Development"]),
    ("Jest", "JavaScript testing framework by Facebook", 2, "jest", "#C21325", 10, ["Testing & QA"]),
    ("Cypress", "End-to-end testing framework for web apps", 2, "cypress", "#17202C", 12, ["Testing & QA"]),
    ("Playwright", "Browser automation for cross-browser testing", 2, "playwright", "#2EAD33", 12, ["Testing & QA"]),
    ("Selenium", "Portable framework for testing web applications", 3, "selenium", "#43B02A", 15, ["Testing & QA"]),
    ("pytest", "Python testing framework for unit and integration tests", 2, "pytest", "#0A9EDC", 8, ["Testing & QA"]),
    ("Unit Testing", "Testing individual units of source code", 2, "unittesting", "#25A162", 8, ["Testing & QA"]),
    ("OWASP Top 10", "Knowledge of critical web application security risks", 2, "owasp", "#000000", 10, ["Security"]),
    ("Penetration Testing", "Simulated security attacks to identify vulnerabilities", 4, "pentest", "#CC0000", 30, ["Security"]),
    ("Cryptography", "Secure communication through encryption techniques", 4, "crypto", "#006666", 25, ["Security"]),
    ("Network Security", "Securing network infrastructure from attacks", 3, "networksec", "#004080", 20, ["Security"]),
    ("Unity", "Cross-platform game engine for 2D and 3D games", 3, "unity", "#000000", 30, ["Game Development"]),
    ("Unreal Engine", "Advanced game engine for high-fidelity 3D games", 4, "unreal", "#313131", 40, ["Game Development"]),
    ("Blender", "Open-source 3D creation suite for modeling and animation", 3, "blender", "#F5792A", 25, ["Game Development", "Design"]),
    ("Solidity", "Smart contract programming language for Ethereum", 4, "solidity", "#363636", 20, ["Blockchain"]),
    ("Web3.js", "JavaScript library for interacting with Ethereum blockchain", 3, "web3", "#F16822", 15, ["Blockchain"]),
    ("Smart Contracts", "Self-executing contracts on blockchain", 4, "smartcontract", "#1C1C1C", 25, ["Blockchain"]),
    ("Agile Methodologies", "Iterative approach to project management", 1, "agile", "#2496ED", 5, ["Soft Skills"]),
    ("Scrum", "Framework for agile software development", 1, "scrum", "#009900", 5, ["Soft Skills"]),
    ("Code Review", "Systematic examination of code by peers", 2, "codereview", "#666666", 5, ["Soft Skills"]),
    ("Technical Writing", "Writing technical documentation and specifications", 2, "techwriting", "#333333", 8, ["Soft Skills"]),
    ("System Design", "Designing scalable and maintainable software systems", 4, "systemdesign", "#1E1E1E", 30, ["Soft Skills"]),
    ("Microservices Architecture", "Architectural style for scalable distributed systems", 4, "microservices", "#F89406", 25, ["Soft Skills", "Backend Development"]),
    ("Git", "Distributed version control system", 1, "git", "#F05032", 8, ["Tools & Utilities"]),
    ("C#", "Modern object-oriented language by Microsoft for .NET", 3, "csharp", "#239120", 20, ["Backend Development", "Programming Languages"]),
    ("Go", "Statically typed compiled language by Google for scalable services", 3, "go", "#00ADD8", 20, ["Backend Development", "Programming Languages"]),
    ("Rust", "Systems programming language focused on safety and performance", 4, "rust", "#000000", 25, ["Backend Development", "Programming Languages"]),
    ("Java", "Object-oriented, class-based programming language for enterprise", 3, "java", "#007396", 25, ["Backend Development", "Programming Languages"]),
    ("PHP", "Server-side scripting language for web development", 2, "php", "#777BB4", 15, ["Backend Development", "Programming Languages"]),
    ("Ruby", "Dynamic open-source language focused on simplicity", 2, "ruby", "#CC342D", 15, ["Backend Development", "Programming Languages"]),
    ("Spring Boot", "Java-based framework for microservices and web apps", 3, "spring", "#6DB33F", 20, ["Backend Development"]),
    ("ASP.NET", "Web framework by Microsoft for building dynamic web apps", 3, "dotnet", "#512BD4", 20, ["Backend Development"]),
    ("MariaDB", "Community-developed fork of MySQL", 2, "mariadb", "#003545", 10, ["Databases"]),
    ("Cassandra", "Distributed NoSQL database for handling large data", 4, "cassandra", "#1287B1", 20, ["Databases"]),
    ("Elasticsearch", "Distributed search and analytics engine", 3, "elasticsearch", "#005571", 15, ["Databases"]),
    ("DynamoDB", "AWS's fully managed NoSQL key-value database", 3, "dynamodb", "#4053D6", 15, ["Databases", "Cloud & Infrastructure"]),
    ("Firebase", "Google's platform for building mobile and web apps", 2, "firebase", "#FFCA28", 12, ["Databases", "Cloud & Infrastructure"]),
    ("Supabase", "Open-source Firebase alternative with PostgreSQL", 2, "supabase", "#3ECF8E", 10, ["Databases", "Backend Development"]),
    ("Deno", "Secure runtime for JavaScript and TypeScript with built-in tooling", 2, "deno", "#2F2F2F", 12, ["Web Development", "Backend Development"]),
    ("NestJS", "Progressive Node.js framework for scalable server-side apps", 3, "nestjs", "#E0234E", 20, ["Backend Development"]),
    ("Prisma", "Next-generation ORM for Node.js and TypeScript", 2, "prisma", "#2D3748", 12, ["Backend Development", "Databases"]),
    ("Kafka", "Distributed event streaming platform for real-time data", 4, "kafka", "#231F20", 25, ["DevOps"]),
    ("RabbitMQ", "Message broker for asynchronous and distributed messaging", 3, "rabbitmq", "#FF6600", 15, ["DevOps"]),
    ("Grafana", "Observability platform for metrics dashboards and alerts", 2, "grafana", "#F46800", 10, ["DevOps", "Cloud & Infrastructure"]),
    ("Prometheus", "Systems monitoring and alerting toolkit", 3, "prometheus", "#E6522C", 15, ["DevOps", "Cloud & Infrastructure"]),
    ("Vault", "Secrets management and data protection platform", 3, "vault", "#000000", 15, ["Security", "DevOps"]),
    ("Helm", "Kubernetes package manager for deploying applications", 3, "helm", "#0F1689", 12, ["DevOps"]),
    ("Istio", "Service mesh for secure Kubernetes networking", 4, "istio", "#466BB0", 18, ["DevOps", "Cloud & Infrastructure"]),
    ("Snowflake", "Cloud data warehouse for analytics workloads", 3, "snowflake", "#29B5E8", 18, ["Databases", "Cloud & Infrastructure"]),
    ("dbt", "Data transformation tool for analytics engineering", 2, "dbt", "#FF694B", 12, ["Data Science", "Databases"]),
    ("Airflow", "Platform for programmatic workflow orchestration", 3, "airflow", "#017CEE", 15, ["Data Science"]),
    ("Spark", "Unified analytics engine for large-scale data processing", 4, "spark", "#E25A1C", 25, ["Data Science"]),
    ("Keras", "High-level deep learning API built on TensorFlow", 3, "keras", "#D00000", 15, ["AI & Machine Learning"]),
    ("XGBoost", "Optimized gradient boosting library for ML", 3, "xgboost", "#3465A4", 15, ["AI & Machine Learning", "Data Science"]),
    ("Plotly", "Interactive graphing and data visualization library", 2, "plotly", "#636EFA", 10, ["Data Science"]),
    ("Three.js", "3D graphics library for the web", 3, "threejs", "#000000", 20, ["Web Development"]),
    ("WebGL", "Web API for GPU-accelerated 3D rendering", 3, "webgl", "#990000", 18, ["Web Development"]),
    ("Sass", "CSS preprocessor with variables, nesting, and mixins", 1, "sass", "#CC6699", 8, ["Web Development", "Design"]),
    ("Less", "CSS preprocessor with dynamic stylesheets", 1, "less", "#1D365D", 8, ["Web Development", "Design"]),
    ("Storybook", "UI component development and documentation environment", 2, "storybook", "#FF4785", 12, ["Design", "Web Development"]),
    ("Vitest", "Fast unit testing framework powered by Vite", 2, "vitest", "#FCC72B", 8, ["Testing & QA"]),
    ("Testing Library", "Lightweight DOM testing utilities for user behavior", 2, "testinglibrary", "#E33332", 10, ["Testing & QA"]),
    ("AXIOS", "Promise-based HTTP client for browser and Node.js", 2, "axios", "#5A29E4", 8, ["Web Development", "Backend Development"]),
    ("Zod", "TypeScript-first schema validation library", 2, "zod", "#3068B7", 8, ["Web Development"]),
    ("tRPC", "End-to-end typesafe APIs without schemas", 3, "trpc", "#398CCB", 12, ["Web Development", "Backend Development"]),
    ("Drizzle", "TypeScript ORM for SQL databases with type safety", 2, "drizzle", "#C5F74F", 10, ["Backend Development", "Databases"]),
    ("Redis Pub/Sub", "Redis publish/subscribe messaging pattern", 3, "redispubsub", "#DC382D", 10, ["Databases"]),
    ("gRPC", "High-performance RPC framework over HTTP/2", 3, "grpc", "#244C5A", 15, ["Backend Development"]),
    ("OAuth2", "Authorization framework for delegated access", 3, "oauth2", "#1E1E1E", 12, ["Security"]),
    ("JWT Auth", "JSON Web Token based authentication", 2, "jwtauth", "#000000", 10, ["Security"]),
    ("Rate Limiting", "Techniques to throttle and control API traffic", 2, "ratelimiting", "#6B7280", 8, ["Security", "Backend Development"]),
    ("WebSockets", "Full-duplex real-time communication protocol", 2, "websockets", "#010101", 12, ["Web Development", "Backend Development"]),
    ("Service Workers", "Scripts enabling offline and background web features", 3, "serviceworkers", "#5B5B5B", 12, ["Web Development"]),
    ("PWA", "Progressive Web Apps blending web and native experiences", 2, "pwa", "#5A0FC8", 12, ["Web Development", "Design"]),
    ("WASM", "WebAssembly portable binary instruction format", 4, "wasm", "#654FF0", 18, ["Web Development", "Programming Languages"]),
    ("Bun", "Fast all-in-one JavaScript runtime and toolkit", 2, "bun", "#FBF0DF", 10, ["Backend Development"]),
    ("Electron", "Build cross-platform desktop apps with web tech", 3, "electron", "#9FEAF9", 18, ["Web Development"]),
    ("Capacitor", "Cross-platform native runtime for web apps", 2, "capacitor", "#119EFF", 12, ["Mobile Development"]),
    ("Expo", "Framework and platform for React Native apps", 2, "expo", "#000020", 12, ["Mobile Development"]),
    ("SwiftUI", "Declarative UI framework for Apple platforms", 3, "swiftui", "#F05138", 18, ["Mobile Development"]),
    ("Jetpack Compose", "Modern declarative Android UI toolkit", 3, "jetpackcompose", "#4285F4", 18, ["Mobile Development"]),
    ("KMM", "Kotlin Multiplatform Mobile for shared code", 3, "kmm", "#7F52FF", 18, ["Mobile Development"]),
    ("Go Modules", "Dependency management for Go projects", 2, "gomodules", "#00ADD8", 8, ["Programming Languages", "Backend Development"]),
    ("Rust Macros", "Metaprogramming with Rust macros", 4, "rustmacros", "#000000", 15, ["Programming Languages", "Backend Development"]),
    ("Rust Async", "Asynchronous programming in Rust", 4, "rustasync", "#000000", 18, ["Programming Languages", "Backend Development"]),
    ("SQL Tuning", "Query optimization for relational databases", 3, "sqltuning", "#336791", 15, ["Databases"]),
    ("Indexing", "Database indexing strategies for performance", 2, "indexing", "#336791", 10, ["Databases"]),
    ("GraphQL Subscriptions", "Real-time GraphQL over websockets", 3, "graphqlsubs", "#E10098", 12, ["Web Development", "Backend Development"]),
]

PREREQ_MAP = {
    "JavaScript": ["HTML", "CSS"],
    "TypeScript": ["JavaScript", "HTML", "CSS"],
    "React": ["JavaScript", "TypeScript", "HTML", "CSS"],
    "Vue.js": ["JavaScript", "TypeScript", "HTML", "CSS"],
    "Angular": ["JavaScript", "TypeScript", "HTML", "CSS"],
    "Svelte": ["JavaScript", "HTML", "CSS"],
    "Next.js": ["React", "JavaScript", "TypeScript", "HTML", "CSS"],
    "Nuxt.js": ["Vue.js", "JavaScript", "HTML", "CSS"],
    "Tailwind CSS": ["CSS", "HTML"],
    "Bootstrap": ["CSS", "HTML"],
    "Redux": ["React", "JavaScript", "HTML", "CSS"],
    "GraphQL": ["JavaScript", "REST API Design", "HTML", "CSS"],
    "GraphQL Subscriptions": ["GraphQL", "WebSockets"],
    "Webpack": ["JavaScript", "HTML", "CSS"],
    "Vite": ["JavaScript", "HTML", "CSS"],
    "Node.js": ["JavaScript", "Docker"],
    "Express.js": ["Node.js", "JavaScript", "REST API Design"],
    "FastAPI": ["Python", "REST API Design"],
    "Django": ["Python", "REST API Design"],
    "Flask": ["Python", "REST API Design"],
    "REST API Design": ["JavaScript", "Python"],
    "React Native": ["React", "JavaScript", "TypeScript", "Git"],
    "Flutter": ["JavaScript", "Git"],
    "TensorFlow": ["Python", "NumPy"],
    "PyTorch": ["Python", "NumPy", "TensorFlow"],
    "scikit-learn": ["Python", "NumPy", "Pandas", "TensorFlow"],
    "Pandas": ["Python", "NumPy"],
    "NumPy": ["Python"],
    "LangChain": ["Python", "OpenAI API", "Hugging Face"],
    "OpenAI API": ["Python"],
    "Hugging Face": ["Python", "TensorFlow"],
    "Natural Language Processing": ["Python", "scikit-learn", "TensorFlow"],
    "Computer Vision": ["Python", "TensorFlow", "PyTorch"],
    "Jupyter Notebooks": ["Python"],
    "Matplotlib": ["Python", "Pandas"],
    "Docker": ["Linux"],
    "Kubernetes": ["Docker"],
    "Terraform": ["AWS", "Linux", "Kubernetes"],
    "Ansible": ["Linux", "Kubernetes"],
    "Jenkins": ["Git", "Docker", "Kubernetes"],
    "GitHub Actions": ["Git", "Kubernetes"],
    "GitLab CI": ["Git", "Kubernetes"],
    "AWS": ["Linux", "Kubernetes"],
    "Google Cloud": ["Linux", "Kubernetes"],
    "Azure": ["Linux", "Kubernetes"],
    "Linux": ["Git"],
    "OWASP Top 10": ["Network Security"],
    "Penetration Testing": ["Network Security", "OWASP Top 10"],
    "Cryptography": ["Network Security"],
    "Network Security": ["Linux"],
    "Selenium": ["JavaScript", "Python", "Unit Testing"],
    "Cypress": ["JavaScript", "Unit Testing"],
    "Playwright": ["JavaScript", "Unit Testing"],
    "pytest": ["Python", "Unit Testing"],
    "Jest": ["JavaScript", "Unit Testing"],
    "Solidity": ["JavaScript", "Web3.js", "Git"],
    "Web3.js": ["JavaScript"],
    "Smart Contracts": ["Solidity", "Web3.js", "Git"],
    "Unity": ["C#", "Blender", "Git"],
    "Unreal Engine": ["C#", "Blender", "Git"],
    "Agile Methodologies": ["Scrum"],
    "Code Review": ["Git", "Agile Methodologies"],
    "System Design": ["REST API Design", "Microservices Architecture"],
    "Microservices Architecture": ["Docker", "REST API Design"],
    "Spring Boot": ["Java", "REST API Design"],
    "ASP.NET": ["C#", "REST API Design"],
    "Kotlin": ["Java", "Git"],
    "Android Development": ["Kotlin", "Java", "Git"],
    "iOS Development": ["Swift", "Git"],
    "Swift": ["Git"],
    "Accessibility (a11y)": ["HTML", "CSS", "JavaScript", "UI/UX Design Principles"],
    "Responsive Design": ["HTML", "CSS"],
    "Design Systems": ["Figma", "UI/UX Design Principles", "CSS"],
    "Prototyping": ["Wireframing", "Figma", "CSS"],
    "Wireframing": ["Figma", "CSS"],
    "UI/UX Design Principles": ["Figma", "CSS"],
    "Technical Writing": ["Git", "Agile Methodologies"],
    "Supabase": ["PostgreSQL", "REST API Design"],
    "Firebase": ["JavaScript"],
    "Go": ["Linux"],
    "Rust": ["Linux"],
    "Java": ["Linux"],
    "C#": ["Linux"],
    "PHP": ["Linux"],
    "Ruby": ["Linux"],
    "Redis": ["Linux"],
    "MariaDB": ["MySQL"],
    "Cassandra": ["Linux"],
    "Elasticsearch": ["Linux"],
    "DynamoDB": ["AWS"],
    "Blender": ["Git"],
    "Adobe XD": ["UI/UX Design Principles"],
    "CSS": ["HTML"],
    "Deno": ["JavaScript", "TypeScript"],
    "NestJS": ["Node.js", "TypeScript"],
    "Prisma": ["PostgreSQL", "TypeScript"],
    "Kafka": ["Docker", "Linux"],
    "RabbitMQ": ["Docker", "Linux"],
    "Grafana": ["Prometheus"],
    "Prometheus": ["Linux", "Docker"],
    "Vault": ["Linux", "Docker"],
    "Helm": ["Kubernetes"],
    "Istio": ["Kubernetes"],
    "Snowflake": ["SQL Tuning"],
    "dbt": ["PostgreSQL", "Python"],
    "Airflow": ["Python"],
    "Spark": ["Python"],
    "Keras": ["TensorFlow"],
    "XGBoost": ["Python", "scikit-learn"],
    "Plotly": ["Python"],
    "Three.js": ["JavaScript", "WebGL"],
    "WebGL": ["JavaScript"],
    "Sass": ["CSS"],
    "Less": ["CSS"],
    "Storybook": ["React"],
    "Vitest": ["JavaScript"],
    "Testing Library": ["React", "JavaScript"],
    "AXIOS": ["JavaScript", "Node.js"],
    "Zod": ["TypeScript"],
    "tRPC": ["TypeScript", "React"],
    "Drizzle": ["PostgreSQL", "TypeScript"],
    "Redis Pub/Sub": ["Redis"],
    "gRPC": ["Go", "Docker"],
    "OAuth2": ["REST API Design"],
    "JWT Auth": ["REST API Design"],
    "Rate Limiting": ["REST API Design"],
    "WebSockets": ["JavaScript", "Node.js"],
    "Service Workers": ["JavaScript", "HTML"],
    "PWA": ["Service Workers", "CSS"],
    "WASM": ["JavaScript"],
    "Bun": ["JavaScript"],
    "Electron": ["JavaScript", "React"],
    "Capacitor": ["React Native"],
    "Expo": ["React Native"],
    "SwiftUI": ["Swift"],
    "Jetpack Compose": ["Kotlin"],
    "KMM": ["Kotlin", "Swift"],
    "Go Modules": ["Go"],
    "Rust Macros": ["Rust"],
    "Rust Async": ["Rust"],
    "SQL Tuning": ["PostgreSQL", "MySQL"],
    "Indexing": ["SQL Tuning"],
}

JOB_ROLES = [
    ("Frontend Developer", "Build user interfaces with modern web technologies", "Web Development",
     ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Next.js", "Tailwind CSS", "Redux", "GraphQL", "Webpack", "Responsive Design", "Accessibility (a11y)", "Git", "Jest"]),
    ("Backend Developer", "Build server-side logic and APIs", "Backend Development",
     ["Node.js", "Express.js", "Python", "FastAPI", "Django", "Flask", "PostgreSQL", "MongoDB", "Redis", "Docker", "REST API Design", "GraphQL", "Git", "System Design", "Microservices Architecture"]),
    ("Full Stack Developer", "Build both frontend and backend systems", "Full Stack Development",
     ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Node.js", "Python", "FastAPI", "Express.js", "PostgreSQL", "MongoDB", "Redis", "Docker", "Git", "REST API Design", "GraphQL", "Tailwind CSS", "Next.js", "Jest", "System Design"]),
    ("DevOps Engineer", "Manage infrastructure and deployment pipelines", "DevOps",
     ["Docker", "Kubernetes", "AWS", "Google Cloud", "Azure", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "Git", "Linux", "Python", "System Design"]),
    ("Cloud Architect", "Design cloud infrastructure solutions", "Cloud & Infrastructure",
     ["AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "Terraform", "System Design", "Microservices Architecture", "PostgreSQL", "Redis", "Cassandra", "DynamoDB", "Linux", "Network Security"]),
    ("Site Reliability Engineer", "Ensure system reliability and observability", "DevOps",
     ["Docker", "Kubernetes", "AWS", "Google Cloud", "Terraform", "Ansible", "Linux", "Python", "System Design", "Microservices Architecture", "Git", "Redis"]),
    ("Data Scientist", "Extract insights from data using statistics and ML", "Data Science",
     ["Python", "Pandas", "NumPy", "scikit-learn", "TensorFlow", "PyTorch", "PostgreSQL", "Jupyter Notebooks", "Matplotlib", "Natural Language Processing", "Computer Vision", "Git"]),
    ("Machine Learning Engineer", "Build and deploy ML models at scale", "AI & Machine Learning",
     ["Python", "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "LangChain", "OpenAI API", "Hugging Face", "Natural Language Processing", "Computer Vision", "Docker", "AWS", "Kubernetes", "Git", "FastAPI"]),
    ("AI Engineer", "Build AI-powered applications and agents", "AI & Machine Learning",
     ["Python", "LangChain", "OpenAI API", "Hugging Face", "TensorFlow", "PyTorch", "Natural Language Processing", "FastAPI", "Docker", "AWS", "PostgreSQL", "Redis", "Git", "System Design"]),
    ("Mobile Developer", "Build cross-platform and native mobile applications", "Mobile Development",
     ["React Native", "Flutter", "Swift", "Kotlin", "iOS Development", "Android Development", "JavaScript", "TypeScript", "React", "Git", "Firebase", "REST API Design", "GraphQL"]),
    ("iOS Developer", "Build applications for Apple's iOS platform", "Mobile Development",
     ["Swift", "iOS Development", "Kotlin", "React Native", "Flutter", "Git", "Firebase", "REST API Design", "GraphQL", "TypeScript"]),
    ("Android Developer", "Build applications for the Android platform", "Mobile Development",
     ["Kotlin", "Android Development", "Java", "Flutter", "React Native", "Git", "Firebase", "REST API Design", "GraphQL"]),
    ("UI/UX Designer", "Design user interfaces and experiences", "Design",
     ["Figma", "Adobe XD", "UI/UX Design Principles", "Wireframing", "Prototyping", "Design Systems", "Accessibility (a11y)", "Responsive Design", "HTML", "CSS"]),
    ("Product Designer", "Design products from concept to execution", "Design",
     ["Figma", "UI/UX Design Principles", "Prototyping", "Design Systems", "Wireframing", "Adobe XD", "Accessibility (a11y)", "Responsive Design", "Agile Methodologies", "Scrum", "Technical Writing"]),
    ("QA Engineer", "Ensure software quality through testing", "Testing & QA",
     ["Jest", "Cypress", "Playwright", "Selenium", "pytest", "Unit Testing", "JavaScript", "TypeScript", "Python", "Git", "Agile Methodologies", "Scrum"]),
    ("Test Automation Engineer", "Build automated testing frameworks", "Testing & QA",
     ["Selenium", "Cypress", "Playwright", "pytest", "Jest", "Unit Testing", "JavaScript", "Python", "Docker", "Jenkins", "Git", "GitHub Actions"]),
    ("Security Engineer", "Protect systems from security threats", "Security",
     ["OWASP Top 10", "Penetration Testing", "Cryptography", "Network Security", "Python", "Linux", "Docker", "Kubernetes", "AWS", "Git"]),
    ("Penetration Tester", "Identify vulnerabilities through ethical hacking", "Security",
     ["Penetration Testing", "OWASP Top 10", "Network Security", "Cryptography", "Linux", "Python", "JavaScript", "Docker", "Git"]),
    ("Data Engineer", "Build and maintain data pipelines and infrastructure", "Data Science",
     ["Python", "PostgreSQL", "MongoDB", "Cassandra", "Elasticsearch", "Docker", "AWS", "Terraform", "Git", "Linux"]),
    ("Data Analyst", "Analyze data to drive business decisions", "Data Science",
     ["PostgreSQL", "Python", "Pandas", "NumPy", "Jupyter Notebooks", "Matplotlib", "scikit-learn"]),
    ("Game Developer", "Build interactive games and experiences", "Game Development",
     ["Unity", "Unreal Engine", "Blender", "C#", "Python", "Git", "System Design"]),
    ("Blockchain Developer", "Build decentralized applications on blockchain", "Blockchain",
     ["Solidity", "Web3.js", "Smart Contracts", "JavaScript", "TypeScript", "Node.js", "Python", "Git", "REST API Design"]),
    ("Python Developer", "Build applications using the Python ecosystem", "Backend Development",
     ["Python", "FastAPI", "Django", "Flask", "PostgreSQL", "Docker", "Git", "pytest", "REST API Design", "Pandas", "NumPy"]),
    ("JavaScript/Node.js Developer", "Build apps with JavaScript throughout the stack", "Backend Development",
     ["JavaScript", "TypeScript", "Node.js", "Express.js", "React", "Next.js", "PostgreSQL", "MongoDB", "Redis", "Docker", "Git", "Jest", "REST API Design", "GraphQL"]),
    ("Solutions Architect", "Design end-to-end technical solutions", "Soft Skills",
     ["System Design", "Microservices Architecture", "AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "REST API Design", "GraphQL", "PostgreSQL", "Redis", "Python", "JavaScript", "Git"]),
]

RESOURCES = [
    ("MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Web", "documentation", True, True, "Mozilla"),
    ("React Documentation", "https://react.dev/", "documentation", True, True, "React Team"),
    ("Next.js Documentation", "https://nextjs.org/docs", "documentation", True, True, "Vercel"),
    ("Tailwind CSS Documentation", "https://tailwindcss.com/docs", "documentation", True, True, "Tailwind Labs"),
    ("TypeScript Handbook", "https://www.typescriptlang.org/docs/", "documentation", True, True, "Microsoft"),
    ("Python Official Documentation", "https://docs.python.org/3/", "documentation", True, True, "Python Software Foundation"),
    ("FastAPI Documentation", "https://fastapi.tiangolo.com/", "documentation", True, True, "Sebastián Ramírez"),
    ("Django Documentation", "https://docs.djangoproject.com/", "documentation", True, True, "Django Software Foundation"),
    ("PostgreSQL Documentation", "https://www.postgresql.org/docs/", "documentation", True, True, "PostgreSQL Global Development Group"),
    ("Docker Documentation", "https://docs.docker.com/", "documentation", True, True, "Docker Inc"),
    ("Kubernetes Documentation", "https://kubernetes.io/docs/home/", "documentation", True, True, "CNCF"),
    ("AWS Documentation", "https://docs.aws.amazon.com/", "documentation", True, True, "Amazon Web Services"),
    ("Git Documentation", "https://git-scm.com/doc", "documentation", True, True, "Git Project"),
    ("Node.js Documentation", "https://nodejs.org/en/docs/", "documentation", True, True, "Node.js Foundation"),
    ("Express.js Guide", "https://expressjs.com/en/guide/routing.html", "documentation", True, True, "Express.js Team"),
    ("MongoDB Documentation", "https://www.mongodb.com/docs/", "documentation", True, True, "MongoDB Inc"),
    ("Redis Documentation", "https://redis.io/docs/latest/", "documentation", True, True, "Redis Ltd"),
    ("Vue.js Documentation", "https://vuejs.org/guide/introduction.html", "documentation", True, True, "Vue Team"),
    ("Angular Documentation", "https://angular.io/docs", "documentation", True, True, "Google"),
    ("Figma Learn Design", "https://help.figma.com/", "documentation", True, True, "Figma"),
    ("TensorFlow Documentation", "https://www.tensorflow.org/learn", "documentation", True, True, "Google"),
    ("PyTorch Documentation", "https://pytorch.org/docs/stable/", "documentation", True, True, "Meta"),
    ("scikit-learn Documentation", "https://scikit-learn.org/stable/documentation.html", "documentation", True, True, "scikit-learn Team"),
    ("Pandas Documentation", "https://pandas.pydata.org/docs/", "documentation", True, True, "NumFOCUS"),
    ("NumPy Documentation", "https://numpy.org/doc/stable/", "documentation", True, True, "NumFOCUS"),
    ("LangChain Documentation", "https://python.langchain.com/docs/", "documentation", True, True, "LangChain Inc"),
    ("OpenAI API Documentation", "https://platform.openai.com/docs/", "documentation", True, True, "OpenAI"),
    ("Hugging Face Documentation", "https://huggingface.co/docs", "documentation", True, True, "Hugging Face"),
    ("Jest Documentation", "https://jestjs.io/docs/getting-started", "documentation", True, True, "Jest Team"),
    ("Cypress Documentation", "https://docs.cypress.io/", "documentation", True, True, "Cypress.io"),
    ("Playwright Documentation", "https://playwright.dev/docs/intro", "documentation", True, True, "Microsoft"),
    ("pytest Documentation", "https://docs.pytest.org/", "documentation", True, True, "pytest Team"),
    ("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "documentation", True, True, "OWASP"),
    ("React Native Documentation", "https://reactnative.dev/docs/getting-started", "documentation", True, True, "Meta"),
    ("Flutter Documentation", "https://docs.flutter.dev/", "documentation", True, True, "Google"),
    ("Swift Documentation", "https://www.swift.org/documentation/", "documentation", True, True, "Apple"),
    ("Kotlin Documentation", "https://kotlinlang.org/docs/home.html", "documentation", True, True, "JetBrains"),
    ("Unity Learn", "https://learn.unity.com/", "course", True, True, "Unity Technologies"),
    ("Solidity Documentation", "https://docs.soliditylang.org/", "documentation", True, True, "Solidity Team"),
    ("GraphQL Official Guide", "https://graphql.org/learn/", "documentation", True, True, "GraphQL Foundation"),
    ("Terraform Documentation", "https://developer.hashicorp.com/terraform/docs", "documentation", True, True, "HashiCorp"),
    ("GitHub Actions Documentation", "https://docs.github.com/en/actions", "documentation", True, True, "GitHub"),
    ("SQL Tutorial - W3Schools", "https://www.w3schools.com/sql/", "article", True, False, "W3Schools"),
    ("JavaScript.info", "https://javascript.info/", "article", True, False, "Ilya Kantor"),
    ("Eloquent JavaScript", "https://eloquentjavascript.net/", "book", True, False, "Marijn Haverbeke"),
    ("You Don't Know JS", "https://github.com/getify/You-Dont-Know-JS", "book", True, False, "Kyle Simpson"),
    ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com/", "book", True, False, "Al Sweigart"),
    ("Pro Git Book", "https://git-scm.com/book/en/v2", "book", True, True, "Scott Chacon"),
    ("System Design Primer", "https://github.com/donnemartin/system-design-primer", "article", True, False, "Donne Martin"),
    ("freeCodeCamp Responsive Web Design", "https://www.freecodecamp.org/learn/responsive-web-design/", "course", True, False, "freeCodeCamp"),
    ("The Odin Project", "https://www.theodinproject.com/", "course", True, False, "The Odin Project"),
    ("Scrum Guide", "https://scrumguides.org/", "documentation", True, True, "Ken Schwaber & Jeff Sutherland"),
    ("Agile Alliance", "https://www.agilealliance.org/", "article", True, True, "Agile Alliance"),
    ("Google Tech Writing", "https://developers.google.com/tech-writing", "course", True, True, "Google"),
    ("CS50 by Harvard", "https://cs50.harvard.edu/", "course", True, False, "Harvard University"),
    ("Stanford ML Course", "https://www.coursera.org/learn/machine-learning", "course", True, False, "Andrew Ng"),
    ("Fast.ai Deep Learning", "https://course.fast.ai/", "course", True, False, "fast.ai"),
    ("Flutter Codelabs", "https://docs.flutter.dev/codelabs", "course", True, True, "Google"),
    ("Android Kotlin Fundamentals", "https://developer.android.com/courses/kotlin-fundamentals/course", "course", True, True, "Google"),
    ("PortSwigger Web Security", "https://portswigger.net/web-security", "course", True, True, "PortSwigger"),
    ("CSS-Tricks Guide", "https://css-tricks.com/guides/", "article", True, False, "CSS-Tricks"),
    ("Web.dev by Google", "https://web.dev/learn/", "course", True, True, "Google"),
    ("Flexbox Froggy", "https://flexboxfroggy.com/", "interactive", True, False, "Codepip"),
    ("SQLZoo", "https://sqlzoo.net/", "interactive", True, False, "SQLZoo"),
    ("Learn Git Branching", "https://learngitbranching.js.org/", "interactive", True, False, "Peter Cottle"),
    ("Linux Journey", "https://linuxjourney.com/", "course", True, False, "Linux Journey"),
    ("CryptoZombies", "https://cryptozombies.io/", "interactive", True, False, "Loom Network"),
    ("TryHackMe", "https://tryhackme.com/", "interactive", True, False, "TryHackMe"),
    ("Codecademy Learn HTML", "https://www.codecademy.com/learn/learn-html", "interactive", True, False, "Codecademy"),
    ("Codecademy Learn CSS", "https://www.codecademy.com/learn/learn-css", "interactive", True, False, "Codecademy"),
    ("Frontend Mentor", "https://www.frontendmentor.io/", "interactive", True, False, "Frontend Mentor"),
    ("Supabase Documentation", "https://supabase.com/docs", "documentation", True, True, "Supabase"),
    ("Firebase Documentation", "https://firebase.google.com/docs", "documentation", True, True, "Google"),
    ("AWS Training", "https://www.aws.training/", "course", True, True, "Amazon Web Services"),
    ("Google Cloud Skills Boost", "https://www.cloudskillsboost.google/", "course", True, True, "Google"),
    ("Go by Example", "https://gobyexample.com/", "article", True, False, "Mark McGranaghan"),
    ("Rust Book", "https://doc.rust-lang.org/book/", "book", True, True, "Rust Team"),
    ("C# Documentation", "https://learn.microsoft.com/en-us/dotnet/csharp/", "documentation", True, True, "Microsoft"),
    ("Spring Boot Reference", "https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/", "documentation", True, True, "VMware"),
    ("ASP.NET Core Docs", "https://learn.microsoft.com/en-us/aspnet/core/", "documentation", True, True, "Microsoft"),
    ("Elasticsearch Guide", "https://www.elastic.co/guide/en/elasticsearch/reference/current/", "documentation", True, True, "Elastic"),
    ("iOS Documentation", "https://developer.apple.com/develop/", "documentation", True, True, "Apple"),
    ("Android Documentation", "https://developer.android.com/docs", "documentation", True, True, "Google"),
    ("Docker Curriculum", "https://docker-curriculum.com/", "interactive", True, False, "Prakhar Srivastav"),
    ("Kubernetes the Hard Way", "https://github.com/kelseyhightower/kubernetes-the-hard-way", "interactive", True, False, "Kelsey Hightower"),
    ("PostgreSQL Tutorial", "https://www.postgresqltutorial.com/", "article", True, False, "PostgreSQL Tutorial"),
    ("MongoDB University", "https://learn.mongodb.com/", "course", True, True, "MongoDB Inc"),
    ("Deno Manual", "https://deno.com/manual", "documentation", True, True, "Deno Land"),
    ("NestJS Documentation", "https://docs.nestjs.com/", "documentation", True, True, "NestJS Team"),
    ("Prisma Docs", "https://www.prisma.io/docs", "documentation", True, True, "Prisma"),
    ("Kafka Documentation", "https://kafka.apache.org/documentation/", "documentation", True, True, "Apache"),
    ("RabbitMQ Tutorials", "https://www.rabbitmq.com/tutorials", "documentation", True, True, "VMware"),
    ("Grafana Docs", "https://grafana.com/docs/", "documentation", True, True, "Grafana Labs"),
    ("Prometheus Docs", "https://prometheus.io/docs/", "documentation", True, True, "CNCF"),
    ("Vault Documentation", "https://developer.hashicorp.com/vault/docs", "documentation", True, True, "HashiCorp"),
    ("Helm Docs", "https://helm.sh/docs/", "documentation", True, True, "CNCF"),
    ("Istio Docs", "https://istio.io/latest/docs/", "documentation", True, True, "Istio"),
    ("Snowflake Docs", "https://docs.snowflake.com/", "documentation", True, True, "Snowflake Inc"),
    ("dbt Documentation", "https://docs.getdbt.com/docs/introduction", "documentation", True, True, "dbt Labs"),
    ("Airflow Docs", "https://airflow.apache.org/docs/", "documentation", True, True, "Apache"),
    ("Spark Documentation", "https://spark.apache.org/docs/latest/", "documentation", True, True, "Apache"),
    ("Keras Documentation", "https://keras.io/", "documentation", True, True, "Keras Team"),
    ("XGBoost Docs", "https://xgboost.readthedocs.io/", "documentation", True, True, "XGBoost Contributors"),
    ("Plotly Docs", "https://plotly.com/python/", "documentation", True, True, "Plotly"),
    ("Three.js Docs", "https://threejs.org/docs/", "documentation", True, True, "Three.js Authors"),
    ("WebGL Fundamentals", "https://webglfundamentals.org/", "article", True, False, "Greggman"),
    ("Sass Documentation", "https://sass-lang.com/documentation", "documentation", True, True, "Sass Team"),
    ("Less Docs", "https://lesscss.org/", "documentation", True, True, "Less Team"),
    ("Storybook Docs", "https://storybook.js.org/docs", "documentation", True, True, "Storybook Team"),
    ("Vitest Documentation", "https://vitest.dev/", "documentation", True, True, "Vitest Team"),
    ("Testing Library Docs", "https://testing-library.com/docs/", "documentation", True, True, "Testing Library"),
    ("Axios Documentation", "https://axios-http.com/docs/intro", "documentation", True, True, "Axios Team"),
    ("Zod Documentation", "https://zod.dev/", "documentation", True, True, "Zod Contributors"),
    ("tRPC Documentation", "https://trpc.io/docs", "documentation", True, True, "tRPC Team"),
    ("Drizzle ORM Docs", "https://orm.drizzle.team/docs", "documentation", True, True, "Drizzle Team"),
    ("gRPC Documentation", "https://grpc.io/docs/", "documentation", True, True, "CNCF"),
    ("OAuth2 RFC", "https://oauth.net/2/", "documentation", True, True, "OAuth.net"),
    ("JWT Introduction", "https://jwt.io/introduction", "article", True, True, "Auth0"),
    ("WebSockets MDN", "https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API", "documentation", True, True, "Mozilla"),
    ("Service Worker API MDN", "https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API", "documentation", True, True, "Mozilla"),
    ("PWA Guides", "https://web.dev/learn/pwa/", "course", True, True, "Google"),
    ("WebAssembly Docs", "https://webassembly.org/docs/", "documentation", True, True, "W3C"),
    ("Bun Documentation", "https://bun.sh/docs", "documentation", True, True, "Oven"),
    ("Electron Docs", "https://www.electronjs.org/docs/latest", "documentation", True, True, "OpenJS"),
    ("Capacitor Docs", "https://capacitorjs.com/docs", "documentation", True, True, "Ionic"),
    ("Expo Docs", "https://docs.expo.dev/", "documentation", True, True, "Expo"),
    ("SwiftUI Tutorials", "https://developer.apple.com/tutorials/swiftui", "course", True, True, "Apple"),
    ("Jetpack Compose Docs", "https://developer.android.com/jetpack/compose/documentation", "documentation", True, True, "Google"),
    ("KMM Documentation", "https://www.jetbrains.com/help/kotlin-multiplatform/", "documentation", True, True, "JetBrains"),
    ("Go Modules Reference", "https://go.dev/ref/mod", "documentation", True, True, "Go Team"),
    ("Rust Macros Book", "https://doc.rust-lang.org/reference/macros.html", "documentation", True, True, "Rust Team"),
    ("Rust Async Book", "https://rust-lang.github.io/async-book/", "book", True, True, "Rust Team"),
    ("Use The Index, Luke", "https://use-the-index-luke.com/", "article", True, True, "Markus Winand"),
    ("GraphQL Subscriptions Docs", "https://graphql.org/learn/subscriptions/", "documentation", True, True, "GraphQL Foundation"),
    ("وثائق MDN بالعربية", "https://developer.mozilla.org/ar/", "documentation", True, True, "Mozilla"),
    ("توثيق React بالعربية", "https://ar.react.dev/", "documentation", True, True, "React Team"),
    ("دليل تايلويند العربي", "https://tailwindcss.com/docs", "documentation", True, True, "Tailwind Labs"),
    ("تعلم JavaScript بالعربية", "https://javascript.info/", "article", True, False, "Ilya Kantor"),
    ("دورة بايثون مجانية", "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "course", True, False, "freeCodeCamp"),
    ("وثائق Docker بالعربية", "https://docs.docker.com/", "documentation", True, True, "Docker Inc"),
    ("مدونة البرمجة العربية", "https://www.example.com/ar/blog", "article", True, False, "Arabic Dev Hub"),
    ("دورة تطوير الويب العربي", "https://www.example.com/ar/webdev", "course", True, False, "Arabic Academy"),
    ("وثائق Git بالعربية", "https://git-scm.com/book/ar/v2", "book", True, True, "Git Project"),
    ("دليل Kubernetes العربي", "https://kubernetes.io/ar/docs/home/", "documentation", True, True, "CNCF"),
]

# Path ownership remapped from seed_v2: Full Stack now belongs to demo
# (matching the old profile_skill_targets), so demo owns one path.
PATHS = [
    {
        "title": "Frontend Developer Learning Path",
        "description": "A comprehensive path to become a Frontend Developer.",
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Tailwind CSS", "Next.js", "Git"],
        "steps": [
            (1, "HTML Fundamentals", "Learn semantic HTML5 markup and structure.", "HTML"),
            (2, "CSS Styling & Layout", "Master Flexbox, Grid, responsive design.", "CSS"),
            (3, "JavaScript Core Concepts", "Closures, promises, async/await, ES6+.", "JavaScript"),
            (4, "TypeScript Mastery", "Interfaces, types, generics.", "TypeScript"),
            (5, "React Fundamentals", "Components, hooks, state management.", "React"),
            (6, "Tailwind CSS & Styling", "Utility-first CSS, responsive designs.", "Tailwind CSS"),
            (7, "Next.js & Full-Stack Frontend", "SSR, SSG, API routes.", "Next.js"),
            (8, "Git & Version Control", "Branching, merging, workflows.", "Git"),
        ],
        "user": "veteran",
    },
    {
        "title": "Backend Developer Learning Path",
        "description": "Complete path to becoming a Backend Developer.",
        "skills": ["Node.js", "Express.js", "Python", "PostgreSQL", "MongoDB", "Redis", "Docker", "Git", "REST API Design", "GraphQL"],
        "steps": [
            (1, "Python for Backend", "Python fundamentals for backend development.", "Python"),
            (2, "Node.js Runtime", "Event loop, streams, npm.", "Node.js"),
            (3, "Express.js Framework", "Routing, middleware, auth.", "Express.js"),
            (4, "SQL & Relational Databases", "SQL queries, joins, indexing with PostgreSQL.", "PostgreSQL"),
            (5, "MongoDB & NoSQL", "CRUD, aggregation, indexing.", "MongoDB"),
            (6, "REST API Design", "RESTful API best practices.", "REST API Design"),
            (7, "GraphQL APIs", "Schema design and resolvers.", "GraphQL"),
            (8, "Docker & Containerization", "Containerize applications.", "Docker"),
            (9, "Git & Collaboration", "Branching strategies and CI/CD.", "Git"),
        ],
        "user": "veteran",
    },
    {
        "title": "Full Stack Developer Learning Path",
        "description": "Become a Full Stack Developer across frontend, backend, and DevOps.",
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Node.js", "Python", "Express.js", "PostgreSQL", "MongoDB", "Docker", "Git", "REST API Design", "Next.js"],
        "steps": [
            (1, "Frontend Foundations", "HTML, CSS, JavaScript, TypeScript.", "HTML"),
            (2, "React & Modern Frontend", "React hooks, context, Next.js.", "React"),
            (3, "Backend with Node.js & Express", "RESTful APIs and server-side apps.", "Node.js"),
            (4, "Python Backend & APIs", "APIs with FastAPI.", "Python"),
            (5, "Databases & Storage", "PostgreSQL, MongoDB, Redis.", "PostgreSQL"),
            (6, "DevOps & Deployment", "Docker and cloud deployment.", "Docker"),
            (7, "Full Stack Project", "Build and deploy a complete app.", "Next.js"),
        ],
        "user": "demo",
    },
    {
        "title": "DevOps Engineer Learning Path",
        "description": "Master DevOps: containers, CI/CD, cloud infrastructure.",
        "skills": ["Linux", "Git", "Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "GitHub Actions", "Python"],
        "steps": [
            (1, "Linux Fundamentals", "Command-line, shell scripting.", "Linux"),
            (2, "Git & Version Control", "Advanced Git workflows.", "Git"),
            (3, "Docker & Containers", "Dockerfiles, multi-container apps.", "Docker"),
            (4, "Kubernetes Orchestration", "Pods, services, deployments.", "Kubernetes"),
            (5, "Cloud Infrastructure (AWS)", "Deploy on AWS.", "AWS"),
            (6, "CI/CD Pipelines", "Jenkins and GitHub Actions.", "Jenkins"),
        ],
        "user": "admin",
    },
    {
        "title": "Data Scientist Learning Path",
        "description": "Become a Data Scientist: Python, ML, data visualization.",
        "skills": ["Python", "PostgreSQL", "Pandas", "NumPy", "scikit-learn", "TensorFlow", "Jupyter Notebooks", "Matplotlib"],
        "steps": [
            (1, "Python for Data Science", "Python fundamentals for data analysis.", "Python"),
            (2, "Data Manipulation with Pandas", "Clean and transform data.", "Pandas"),
            (3, "Numerical Computing with NumPy", "Array operations.", "NumPy"),
            (4, "Machine Learning with scikit-learn", "Regression, classification.", "scikit-learn"),
            (5, "Deep Learning with TensorFlow", "Neural networks.", "TensorFlow"),
        ],
        "user": "editor",
    },
    {
        "title": "Modern Web Frontend Path",
        "description": "Advanced frontend engineering with modern tooling and testing.",
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "Sass", "React", "Next.js", "Redux", "Storybook", "Tailwind CSS", "Vitest", "Testing Library"],
        "steps": [
            (1, "HTML Fundamentals", "Semantic markup and structure.", "HTML"),
            (2, "CSS Styling & Layout", "Flexbox, Grid, responsive design.", "CSS"),
            (3, "JavaScript Core", "Closures, async, ES6 modules.", "JavaScript"),
            (4, "TypeScript Mastery", "Types, generics, interfaces.", "TypeScript"),
            (5, "Sass Preprocessing", "Variables, nesting, mixins.", "Sass"),
            (6, "React Fundamentals", "Components, hooks, state.", "React"),
            (7, "Next.js Framework", "SSR, routing, API routes.", "Next.js"),
            (8, "State with Redux", "Predictable state management.", "Redux"),
            (9, "Storybook Components", "Isolated component development.", "Storybook"),
            (10, "Tailwind CSS", "Utility-first styling.", "Tailwind CSS"),
            (11, "Unit Testing with Vitest", "Fast unit tests.", "Vitest"),
            (12, "Component Testing", "Behavior with Testing Library.", "Testing Library"),
        ],
        "user": "learner1",
    },
    {
        "title": "Backend with Node & TypeScript Path",
        "description": "Build scalable APIs with Node.js, TypeScript, and GraphQL.",
        "skills": ["JavaScript", "TypeScript", "Node.js", "Express.js", "NestJS", "AXIOS", "REST API Design", "GraphQL", "WebSockets", "JWT Auth", "OAuth2", "Rate Limiting"],
        "steps": [
            (1, "JavaScript Core", "Language fundamentals.", "JavaScript"),
            (2, "TypeScript", "Typed JavaScript.", "TypeScript"),
            (3, "Node.js Runtime", "Runtime and modules.", "Node.js"),
            (4, "Express.js", "Routing and middleware.", "Express.js"),
            (5, "NestJS Framework", "Structured server apps.", "NestJS"),
            (6, "HTTP with AXIOS", "Client requests.", "AXIOS"),
            (7, "REST API Design", "Resource design.", "REST API Design"),
            (8, "GraphQL APIs", "Schema and resolvers.", "GraphQL"),
            (9, "WebSockets", "Real-time communication.", "WebSockets"),
            (10, "JWT Authentication", "Token auth.", "JWT Auth"),
            (11, "OAuth2", "Delegated authorization.", "OAuth2"),
            (12, "Rate Limiting", "Traffic control.", "Rate Limiting"),
        ],
        "user": "learner2",
    },
    {
        "title": "Cloud Native & DevOps Path",
        "description": "Operate cloud-native infrastructure with Kubernetes and observability.",
        "skills": ["Linux", "Git", "Docker", "Kubernetes", "Helm", "Istio", "Prometheus", "Grafana", "Terraform", "AWS", "Ansible", "Jenkins"],
        "steps": [
            (1, "Linux Fundamentals", "Shell and permissions.", "Linux"),
            (2, "Git & Version Control", "Workflows.", "Git"),
            (3, "Docker & Containers", "Image building.", "Docker"),
            (4, "Kubernetes Orchestration", "Pods and services.", "Kubernetes"),
            (5, "Helm Packaging", "Chart management.", "Helm"),
            (6, "Istio Service Mesh", "Secure networking.", "Istio"),
            (7, "Prometheus Monitoring", "Metrics and alerts.", "Prometheus"),
            (8, "Grafana Dashboards", "Visualization.", "Grafana"),
            (9, "Terraform IaC", "Infrastructure as code.", "Terraform"),
            (10, "AWS Cloud", "Managed services.", "AWS"),
            (11, "Ansible Automation", "Configuration management.", "Ansible"),
            (12, "Jenkins Pipelines", "CI/CD.", "Jenkins"),
        ],
        "user": "learner3",
    },
    {
        "title": "Data Engineering Path",
        "description": "Pipeline and analytics engineering with SQL and Spark.",
        "skills": ["Python", "SQL Tuning", "PostgreSQL", "Indexing", "MySQL", "MariaDB", "Snowflake", "dbt", "Airflow", "Spark", "Kafka", "RabbitMQ"],
        "steps": [
            (1, "Python for Engineering", "Scripting and data.", "Python"),
            (2, "SQL Tuning", "Query optimization.", "SQL Tuning"),
            (3, "PostgreSQL", "Relational storage.", "PostgreSQL"),
            (4, "Indexing", "Performance indexing.", "Indexing"),
            (5, "MySQL", "Alternate RDBMS.", "MySQL"),
            (6, "MariaDB", "Fork compatibility.", "MariaDB"),
            (7, "Snowflake", "Cloud warehouse.", "Snowflake"),
            (8, "dbt Transforms", "Analytics engineering.", "dbt"),
            (9, "Airflow Orchestration", "Workflow scheduling.", "Airflow"),
            (10, "Spark Processing", "Big data engine.", "Spark"),
            (11, "Kafka Streaming", "Event streaming.", "Kafka"),
            (12, "RabbitMQ Messaging", "Queue based messaging.", "RabbitMQ"),
        ],
        "user": "learner1",
    },
    {
        "title": "AI & ML Engineering Path",
        "description": "Deep learning, classic ML, and LLM application building.",
        "skills": ["Python", "NumPy", "Pandas", "Matplotlib", "scikit-learn", "TensorFlow", "Keras", "PyTorch", "Plotly", "XGBoost", "Natural Language Processing", "Hugging Face", "LangChain", "OpenAI API"],
        "steps": [
            (1, "Python Foundations", "Core language.", "Python"),
            (2, "NumPy", "Array computing.", "NumPy"),
            (3, "Pandas", "Data manipulation.", "Pandas"),
            (4, "Matplotlib", "Visualization.", "Matplotlib"),
            (5, "scikit-learn", "Classic ML.", "scikit-learn"),
            (6, "TensorFlow", "Deep learning base.", "TensorFlow"),
            (7, "Keras", "High-level models.", "Keras"),
            (8, "PyTorch", "Dynamic graphs.", "PyTorch"),
            (9, "Plotly", "Interactive charts.", "Plotly"),
            (10, "XGBoost", "Gradient boosting.", "XGBoost"),
            (11, "NLP", "Language models.", "Natural Language Processing"),
            (12, "Hugging Face", "Transformer hub.", "Hugging Face"),
            (13, "LangChain", "LLM apps.", "LangChain"),
            (14, "OpenAI API", "Model integration.", "OpenAI API"),
        ],
        "user": "learner2",
    },
    {
        "title": "Mobile Cross-Platform Path",
        "description": "Build mobile apps across React Native, iOS, and Android.",
        "skills": ["JavaScript", "TypeScript", "React", "React Native", "Expo", "Capacitor", "Swift", "SwiftUI", "Kotlin", "Jetpack Compose", "Flutter", "Android Development"],
        "steps": [
            (1, "JavaScript Core", "Language basics.", "JavaScript"),
            (2, "TypeScript", "Typed scripts.", "TypeScript"),
            (3, "React", "Component model.", "React"),
            (4, "React Native", "Cross-platform mobile.", "React Native"),
            (5, "Expo Tooling", "RN platform.", "Expo"),
            (6, "Capacitor", "Web to native.", "Capacitor"),
            (7, "Swift", "Apple language.", "Swift"),
            (8, "SwiftUI", "Apple UI.", "SwiftUI"),
            (9, "Kotlin", "JVM language.", "Kotlin"),
            (10, "Jetpack Compose", "Android UI.", "Jetpack Compose"),
            (11, "Flutter", "Dart-based UI.", "Flutter"),
            (12, "Android Development", "Platform APIs.", "Android Development"),
        ],
        "user": "learner3",
    },
    {
        "title": "Security & API Path",
        "description": "Secure APIs and infrastructure with modern practices.",
        "skills": ["Linux", "Git", "Network Security", "OWASP Top 10", "Cryptography", "Penetration Testing", "REST API Design", "JWT Auth", "OAuth2", "Rate Limiting", "Vault", "WebSockets"],
        "steps": [
            (1, "Linux Fundamentals", "Hardening basics.", "Linux"),
            (2, "Git & Version Control", "Secure workflows.", "Git"),
            (3, "Network Security", "Infrastructure defense.", "Network Security"),
            (4, "OWASP Top 10", "Web risks.", "OWASP Top 10"),
            (5, "Cryptography", "Encryption primitives.", "Cryptography"),
            (6, "Penetration Testing", "Ethical hacking.", "Penetration Testing"),
            (7, "REST API Design", "Safe APIs.", "REST API Design"),
            (8, "JWT Authentication", "Token auth.", "JWT Auth"),
            (9, "OAuth2", "Delegated access.", "OAuth2"),
            (10, "Rate Limiting", "Abuse prevention.", "Rate Limiting"),
            (11, "Vault Secrets", "Secret management.", "Vault"),
            (12, "WebSockets", "Secure real-time.", "WebSockets"),
        ],
        "user": "learner1",
    },
]

# Scored attempts (user_key, skill_name, score) — feed assessment_results
# and assessment-derived user_skills proficiency levels.
ATTEMPT_PLAN = [
    ("veteran", "HTML", 85), ("veteran", "CSS", 92), ("veteran", "JavaScript", 78),
    ("veteran", "PostgreSQL", 88), ("veteran", "Docker", 77),
    ("demo", "Python", 88), ("demo", "Docker", 65), ("demo", "Git", 90),
    ("demo", "TypeScript", 71),
    ("student2", "React", 73), ("student2", "TypeScript", 81),
    ("student2", "Python", 74), ("student2", "HTML", 60),
    ("admin", "System Design", 95), ("admin", "Kubernetes", 82),
    ("editor", "Figma", 70),
]

# Completion plan: (user_key, path_title, completed_steps, in_progress_step)
PROGRESS_PLAN = [
    ("veteran", "Frontend Developer Learning Path", 3, 4),
    ("veteran", "Backend Developer Learning Path", 4, 5),
    ("demo", "Full Stack Developer Learning Path", 3, None),
    ("admin", "DevOps Engineer Learning Path", 2, None),
    ("editor", "Data Scientist Learning Path", 2, None),
]

# Activity feed rows (user_key, category, action, entity_type, entity_id, data)
ACTIVITY_LOG = [
    ("admin", "auth", "login", "user", "session", {"method": "password"}),
    ("veteran", "auth", "login", "user", "session", {"method": "password"}),
    ("veteran", "auth", "password_reset_requested", "user", "session", {"email": "veteran@skillsynth.io"}),
    ("veteran", "learning", "path_created", "path", "Frontend Developer Learning Path", {"title": "Frontend Developer Learning Path"}),
    ("veteran", "learning", "path_created", "path", "Backend Developer Learning Path", {"title": "Backend Developer Learning Path"}),
    ("veteran", "learning", "step_completed", "step", "HTML Fundamentals", {"step": 1}),
    ("veteran", "learning", "step_completed", "step", "CSS Styling & Layout", {"step": 2}),
    ("veteran", "learning", "step_completed", "step", "JavaScript Core Concepts", {"step": 3}),
    ("veteran", "learning", "assessment_completed", "assessment", "HTML Assessment", {"score": 80}),
    ("veteran", "learning", "assessment_completed", "assessment", "CSS Assessment", {"score": 60}),
    ("demo", "learning", "path_created", "path", "Full Stack Developer Learning Path", {"title": "Full Stack Developer Learning Path"}),
    ("admin", "learning", "path_created", "path", "DevOps Engineer Learning Path", {"title": "DevOps Engineer Learning Path"}),
    ("editor", "learning", "path_created", "path", "Data Scientist Learning Path", {"title": "Data Scientist Learning Path"}),
    ("admin", "learning", "skill_updated", "skill", "TypeScript", {"field": "difficulty"}),
    ("admin", "audit", "create", "user", "user", {"email": "admin@skillsynth.io"}),
    ("admin", "audit", "update", "skill", "TypeScript", {"old": 2, "new": 3}),
    ("admin", "system", "notification_sent", "system", "maintenance", {"title": "Database maintenance tonight"}),
    ("admin", "auth", "logout", "user", "session", {}),
    ("demo", "learning", "step_completed", "step", "Frontend Foundations", {"step": 1}),
    ("demo", "learning", "assessment_completed", "assessment", "Python Assessment", {"score": 88}),
    ("admin", "learning", "step_completed", "step", "Linux Fundamentals", {"step": 1}),
    ("editor", "learning", "step_completed", "step", "Python for Data Science", {"step": 1}),
    ("editor", "learning", "step_completed", "step", "Data Manipulation with Pandas", {"step": 2}),
    ("admin", "system", "backup_created", "system", "backup", {"path": "skillsynth_backup.db"}),
    ("admin", "system", "config_updated", "system", "config", {"key": "session_timeout"}),
    ("veteran", "learning", "step_completed", "step", "Python for Backend", {"step": 1}),
]

# ──────────────────────────────────────────────────────────────────────
# Seed helpers
# ──────────────────────────────────────────────────────────────────────

def _seed_users(db):
    """Insert the eight canonical users with bcrypt-hashed passwords."""
    users = {}
    for email, password, full_name, is_admin in USERS:
        user = User(email=email, hashed_password=hash_password(password),
                    full_name=full_name, is_admin=is_admin)
        db.add(user)
        db.flush()
        users[email.split("@")[0]] = user
    return users


def _seed_categories(db):
    """Insert the 16 top-level categories; returns {name: Category}."""
    cat_map = {}
    for name in CATEGORIES:
        category = Category(name=name)
        db.add(category)
        db.flush()
        cat_map[name] = category
    return cat_map


def _seed_skills(db, cat_map):
    """Insert 152 skills with enriched topics; returns name/id maps."""
    skill_by_name, skill_by_id = {}, {}
    for name, desc, diff, icon, color, hours, cats in SKILLS:
        category_id = cat_map[cats[0]].id if cats else None
        topics = TOPICS.get(name) or ([name] + [c for c in cats if c != name])
        skill = Skill(name=name, description=desc, difficulty_level=diff,
                      icon=icon, color=color, estimated_hours=hours,
                      category_id=category_id, topics=topics)
        db.add(skill)
        db.flush()
        skill_by_name[name] = skill
        skill_by_id[skill.id] = skill
    return skill_by_name, skill_by_id


def _seed_prerequisites(db, skill_by_name):
    """Insert prerequisite edges for skills present in the catalog."""
    count = 0
    for skill_name, prereq_names in PREREQ_MAP.items():
        skill = skill_by_name.get(skill_name)
        if not skill:
            continue
        for prereq_name in prereq_names:
            prereq = skill_by_name.get(prereq_name)
            if prereq:
                db.add(SkillPrerequisite(skill_id=skill.id,
                                         prerequisite_id=prereq.id))
                count += 1
    db.flush()
    return count


def _seed_job_roles(db, skill_by_name):
    """Insert 25 job roles and their job_role_skills mappings."""
    count = 0
    for title, desc, field, skills_list in JOB_ROLES:
        role = JobRole(title=title, description=desc, career_field=field)
        db.add(role)
        db.flush()
        for skill_name in skills_list:
            skill = skill_by_name.get(skill_name)
            if skill:
                db.add(JobRoleSkill(job_role_id=role.id, skill_id=skill.id))
                count += 1
    db.flush()
    return count


def _seed_resources(db):
    """Insert 142 resources, tagging Arabic titles with language='ar'."""
    def _is_arabic(title):
        return any("\u0600" <= ch <= "\u06FF" for ch in title)

    for title, url, rtype, is_free, is_official, author in RESOURCES:
        db.add(Resource(title=title, url=url, type=rtype,
                         language="ar" if _is_arabic(title) else "en",
                         is_free=is_free, is_official=is_official,
                         author_or_platform=author))
    db.flush()
    return len(RESOURCES)


def _fallback_questions(skill_name):
    """Four deterministic questions for skills without bank entries."""
    return [
        {"question": f"What is {skill_name} primarily used for?",
         "options": ["Building applications", "Data analysis",
                     "Infrastructure", "Development"], "correct": 0},
        {"question": f"Key feature of {skill_name}?",
         "options": ["Performance", "Scalability", "Flexibility",
                     "All of the above"], "correct": 3},
        {"question": f"Which practice best fits {skill_name}?",
         "options": ["Ad-hoc scripting", "Structured design",
                     "Manual testing", "None of the above"], "correct": 1},
        {"question": f"Where would you apply {skill_name}?",
         "options": ["Production systems", "Local only", "Never",
                     "Prototypes only"], "correct": 0},
    ]

def _seed_assessments(db, skill_by_name):
    """Insert one assessment per skill, splitting questions into rows."""
    assessment_by_skill = {}
    for skill_name, skill in skill_by_name.items():
        assessment = Assessment(skill_id=skill.id,
                                title=f"{skill_name} Assessment",
                                pass_score=70)
        db.add(assessment)
        db.flush()
        questions = QUESTION_BANK.get(skill_name) or _fallback_questions(skill_name)
        for position, q in enumerate(questions):
            db.add(AssessmentQuestion(
                assessment_id=assessment.id, position=position,
                prompt=q["question"], options=q["options"],
                correct_index=q["correct"]))
        assessment_by_skill[skill_name] = assessment
    db.flush()
    return assessment_by_skill


def _seed_paths(db, users, skill_by_name):
    """Insert 12 learning paths with ordered topo-safe steps; maps titles."""
    path_map = {}
    for pd in PATHS:
        owner = users[pd["user"]]
        path = Path(user_id=owner.id, title=pd["title"],
                    description=pd["description"],
                    target_role=pd["title"].replace(" Learning Path", ""),
                    status="active",
                    total_estimated_hours=len(pd["steps"]) * 8,
                    total_estimated_weeks=len(pd["steps"]))
        db.add(path)
        db.flush()
        for num, title, content, skill_name in pd["steps"]:
            skill = skill_by_name.get(skill_name)
            db.add(PathStep(path_id=path.id, position=num, title=title,
                            description=content, estimated_hours=8,
                            skill_id=skill.id if skill else None,
                            learning_objectives=[]))
        path_map[pd["title"]] = path
    db.flush()
    return path_map


def _seed_step_progress(db, path_map, users, now):
    """Merged step_progress: completed + in-progress rows across learners."""
    count = 0
    day = 0
    for user_key, title, completed_n, current_n in PROGRESS_PLAN:
        user = users.get(user_key)
        if not user or title not in path_map:
            continue
        steps = (db.query(PathStep)
                   .filter(PathStep.path_id == path_map[title].id)
                   .order_by(PathStep.position).all())
        for i, step in enumerate(steps[:completed_n]):
            day += 2
            done_at = now - timedelta(days=day, hours=(i * 3) % 24)
            db.add(StepProgress(user_id=user.id, step_id=step.id,
                                completed_at=done_at, score=75 + (i * 5) % 21))
            count += 1
        if current_n is not None and current_n <= len(steps):
            db.add(StepProgress(user_id=user.id,
                                step_id=steps[current_n - 1].id))
            count += 1
    db.flush()
    return count


def _seed_user_skills(db, users, skill_by_name, skill_by_id):
    """Build user_skills from path steps + assessment-derived levels.

    A deterministic subset (skills with rich topics and difficulty >= 3) gets
    a non-empty weak_points list drawn from the skill's topics, so the
    current-topic-to-master feature has real seed data.
    """
    levels = {}
    for path in db.query(Path).all():
        for step in db.query(PathStep).filter(PathStep.path_id == path.id).all():
            skill = skill_by_id.get(step.skill_id)
            if skill:
                level = max(1, min(5, skill.difficulty_level or 1))
                levels.setdefault((path.user_id, skill.id), level)
    for uname, skill_name, score in ATTEMPT_PLAN:
        user = users.get(uname)
        skill = skill_by_name.get(skill_name)
        if user and skill:
            levels[(user.id, skill.id)] = max(1, min(5, round(score / 100 * 5)))
    for (user_id, skill_id), level in levels.items():
        skill = skill_by_id.get(skill_id)
        topics = skill.topics or [] if skill else []
        if skill and len(topics) >= 3 and (skill.difficulty_level or 0) >= 3:
            weak_points = [topics[1], topics[2]]
        else:
            weak_points = []
        db.add(UserSkill(user_id=user_id, skill_id=skill_id,
                         proficiency_level=level, weak_points=weak_points))
    db.flush()
    return len(levels)


def _seed_assessment_results(db, users, assessment_by_skill, now):
    """Insert scored attempts with pass/fail flags."""
    count = 0
    for i, (uname, skill_name, score) in enumerate(ATTEMPT_PLAN):
        assessment = assessment_by_skill.get(skill_name)
        user = users.get(uname)
        if not assessment or not user:
            continue
        db.add(AssessmentResult(
            user_id=user.id, assessment_id=assessment.id, score=score,
            passed=score >= (assessment.pass_score or 60),
            completed_at=now - timedelta(days=(len(ATTEMPT_PLAN) - i) * 3)))
        count += 1
    db.flush()
    return count


def _seed_activity_log(db, users, now):
    """Insert activity rows across audit/auth/system/learning categories."""
    count = 0
    for i, (user_key, category, action, etype, eid, data) in enumerate(ACTIVITY_LOG):
        user = users.get(user_key)
        db.add(ActivityLog(
            user_id=user.id if user else None, category=category,
            action=action, entity_type=etype, entity_id=eid, data=data,
            ip_address="127.0.0.1", created_at=now - timedelta(days=i)))
        count += 1
    db.flush()
    return count


def _print_counts(db):
    """Print per-table row counts (including zeros) plus the total."""
    total = 0
    for table in Base.metadata.sorted_tables:
        count = db.execute(text(f'SELECT COUNT(*) FROM "{table.name}"')).scalar()
        total += count
        marker = "" if count else "   <- empty"
        print(f"  {table.name:32s} {count:>5}{marker}")
    print(f"  {'TOTAL':32s} {total:>5}")
    return total


def kahn_order(skills, edges):
    """Topologically order skills from (skill_id, prerequisite_id) edges.

    Implements Kahn's algorithm. `skills` is the iterable of Skill objects.
    Returns a list of skill names in topological order. Raises SystemExit if
    a cycle is detected in the prerequisite DAG.
    """
    id_to_name = {s.id: s.name for s in skills}
    nodes = set(id_to_name.keys())
    adjacency = {n: [] for n in nodes}
    in_degree = {n: 0 for n in nodes}
    for skill_id, prereq_id in edges:
        if prereq_id in adjacency and skill_id in in_degree:
            adjacency[prereq_id].append(skill_id)
            in_degree[skill_id] += 1
    queue = sorted([n for n in nodes if in_degree[n] == 0])
    order = []
    while queue:
        current = queue.pop(0)
        order.append(current)
        for nxt in adjacency[current]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)
                queue.sort()
    if len(order) != len(nodes):
        sys.exit("CYCLE DETECTED in skill prerequisite DAG (kahn_order)")
    return [id_to_name[n] for n in order]


def seed(engine=None, session_factory=None):
    """Drop/create, insert all 15 tables, run the FK gate, print counts.

    Accepts an explicit engine/session factory (used by tests/conftest.py
    against an isolated temp DB) or falls back to the bound dev engine.
    Also validates the global prerequisite DAG via kahn_order.
    """
    import backend.database as database
    eng = engine or database.engine
    sf = session_factory or database.SessionLocal

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=eng)
    print("Creating all tables...")
    Base.metadata.create_all(bind=eng)

    db = sf()
    try:
        now = datetime.now(UTC)
        users = _seed_users(db)
        cat_map = _seed_categories(db)
        skill_by_name, skill_by_id = _seed_skills(db, cat_map)
        _seed_prerequisites(db, skill_by_name)
        _seed_job_roles(db, skill_by_name)
        _seed_resources(db)
        assessment_by_skill = _seed_assessments(db, skill_by_name)
        path_map = _seed_paths(db, users, skill_by_name)
        _seed_step_progress(db, path_map, users, now)
        _seed_user_skills(db, users, skill_by_name, skill_by_id)
        _seed_assessment_results(db, users, assessment_by_skill, now)
        _seed_activity_log(db, users, now)

        # Kahn integrity: build edges from SkillPrerequisite rows and validate.
        edges = [(sp.skill_id, sp.prerequisite_id)
                 for sp in db.query(SkillPrerequisite).all()]
        order = kahn_order(db.query(Skill).all(), edges)
        print("\n" + "=" * 50)
        print("KAHN TOPOLOGICAL ORDER (skill DAG)")
        print("=" * 50)
        print(", ".join(order))

        db.commit()

        violations = db.execute(text("PRAGMA foreign_key_check")).fetchall()
        if violations:
            print(f"\nFOREIGN KEY VIOLATIONS ({len(violations)}):")
            for violation in violations[:20]:
                print(f"  {tuple(violation)}")
            sys.exit(1)

        print("\n" + "=" * 50)
        print("SEED COMPLETE — TABLE COUNTS")
        print("=" * 50)
        _print_counts(db)
        print("FOREIGN KEY CHECK: OK")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
