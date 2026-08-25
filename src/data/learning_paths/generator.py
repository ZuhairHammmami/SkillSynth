from .db_connector import fetch_skills_for_job_role, fetch_resources_for_skill, fetch_prerequisites_for_skills, fetch_role_skill_config

PREREQ_FALLBACK = {
    'html': [], 'css': ['html'], 'javascript': ['html', 'css'],
    'typescript': ['javascript'], 'react': ['javascript', 'css'],
    'vue_js': ['javascript', 'css'], 'angular': ['typescript', 'javascript'],
    'svelte': ['javascript', 'css'],
    'next_js': ['react', 'javascript'], 'nuxt_js': ['vue_js', 'javascript'],
    'tailwind_css': ['css'], 'bootstrap': ['css'], 'jquery': ['javascript', 'css'],
    'redux': ['react', 'javascript'], 'webpack': ['javascript', 'node_js'],
    'vite': ['javascript', 'node_js'],
    'node_js': ['javascript'], 'express_js': ['node_js', 'javascript'],
    'python': [], 'fastapi': ['python'], 'django': ['python'], 'flask': ['python'],
    'spring_boot': ['java'], 'asp_net': ['c#'],
    'rest_api_design': ['javascript', 'python'], 'graphql': ['rest_api_design', 'javascript'],
    'sql': [], 'postgresql': ['sql'], 'mysql': ['sql'], 'sqlite': ['sql'],
    'mariadb': ['sql'], 'mongodb': [], 'redis': [], 'cassandra': [], 'dynamodb': [],
    'elasticsearch': [], 'neo4j': [], 'firebase': ['javascript'], 'supabase': ['sql'],
    'docker': ['linux'], 'kubernetes': ['docker'],
    'aws': ['linux'], 'google_cloud': ['linux'], 'azure': ['linux'],
    'terraform': ['aws', 'docker'], 'ansible': ['linux', 'python'],
    'jenkins': ['git', 'docker'], 'github_actions': ['git'], 'gitlab_ci': ['git'],
    'git': [], 'linux': [], 'nginx': ['linux', 'docker'],
    'prometheus': ['linux', 'docker'], 'grafana': ['linux', 'prometheus'],
    'react_native': ['react', 'javascript'], 'flutter': [], 'swift': [],
    'ios_development': ['swift'], 'android_development': ['kotlin', 'java'],
    'ionic': ['angular', 'react', 'javascript'], 'xamarin': ['c#'],
    'pandas': ['python', 'numpy'], 'numpy': ['python'],
    'tensorflow': ['python', 'numpy'], 'pytorch': ['python', 'numpy'],
    'scikit_learn': ['python', 'numpy', 'pandas'],
    'langchain': ['python', 'openai_api'], 'openai_api': ['python'],
    'hugging_face': ['python', 'tensorflow'],
    'natural_language_processing': ['python', 'tensorflow', 'scikit_learn'],
    'computer_vision': ['python', 'tensorflow', 'numpy'],
    'jupyter_notebooks': ['python'], 'matplotlib': ['python', 'numpy'],
    'figma': [], 'adobe_xd': [], 'sketch': [], 'photoshop': [], 'illustrator': [],
    'ui_ux_design_principles': [], 'wireframing': ['ui_ux_design_principles'],
    'prototyping': ['wireframing', 'ui_ux_design_principles'],
    'design_systems': ['ui_ux_design_principles'],
    'accessibility_a11y': ['html', 'css'], 'responsive_design': ['css', 'html'],
    'jest': ['javascript', 'node_js'], 'cypress': ['javascript', 'node_js'],
    'playwright': ['javascript', 'node_js'], 'selenium': ['python', 'javascript'],
    'pytest': ['python'], 'mocha': ['javascript', 'node_js'],
    'unit_testing': ['javascript', 'python'], 'integration_testing': ['unit_testing'],
    'tdd': ['unit_testing', 'integration_testing'],
    'owasp_top_10': ['linux', 'python'],
    'penetration_testing': ['owasp_top_10', 'linux', 'python'],
    'cryptography': ['python'],
    'authentication_&_authorization': ['rest_api_design'],
    'network_security': ['linux'],
    'unity': ['c#'], 'unreal_engine': ['c++_for_games'],
    'blender': [], 'c++_for_games': [],
    'solidity': ['javascript', 'typescript'], 'web3_js': ['javascript'],
    'smart_contracts': ['solidity', 'web3_js'],
    'agile_methodologies': [], 'scrum': ['agile_methodologies'],
    'code_review': ['git'], 'technical_writing': [],
    'system_design': ['rest_api_design', 'microservices_architecture'],
    'api_design': ['rest_api_design'],
    'microservices_architecture': ['docker', 'system_design'],
    'java': [], 'go': [], 'rust': [], 'c#': [], 'php': [], 'ruby': [],
    'scala': [], 'kotlin': [], 'c++': [],
}

STEP_TITLES = {
    "html": "Build Your First Web Skeleton (HTML)",
    "css": "Bring Your Web to Life with Style (CSS)",
    "javascript": "Add Brains to Your Project (JavaScript)",
    "typescript": "Write Safer Code with TypeScript",
    "react": "Master Modern UI with React",
    "vue_js": "Build Reactive Interfaces with Vue.js",
    "angular": "Enterprise Architecture with Angular",
    "svelte": "Build Fast with Svelte",
    "next_js": "Full-Stack React with Next.js",
    "nuxt_js": "Universal Vue with Nuxt.js",
    "tailwind_css": "Utility-First CSS with Tailwind",
    "bootstrap": "Rapid UI with Bootstrap",
    "jquery": "DOM Manipulation with jQuery",
    "redux": "State Management with Redux",
    "webpack": "Module Bundling with Webpack",
    "vite": "Next-Gen Build Tooling with Vite",
    "node_js": "Server-Side JavaScript with Node.js",
    "express_js": "Build APIs with Express.js",
    "python": "Unlock the Power of Python",
    "fastapi": "Modern APIs with FastAPI",
    "django": "Full-Stack Web with Django",
    "flask": "Lightweight Web with Flask",
    "spring_boot": "Java Enterprise with Spring Boot",
    "asp_net": "Cross-Platform with ASP.NET",
    "rest_api_design": "Design RESTful APIs",
    "graphql": "Query Languages with GraphQL",
    "sql": "Speak the Language of Data (SQL)",
    "postgresql": "Advanced PostgreSQL",
    "mysql": "MySQL for Data-Driven Apps",
    "sqlite": "Embedded Databases with SQLite",
    "mariadb": "Open-Source with MariaDB",
    "mongodb": "Document Databases with MongoDB",
    "redis": "In-Memory Data with Redis",
    "cassandra": "Scalable NoSQL with Cassandra",
    "dynamodb": "AWS NoSQL with DynamoDB",
    "elasticsearch": "Search & Analytics with Elasticsearch",
    "neo4j": "Graph Databases with Neo4j",
    "firebase": "Serverless with Firebase",
    "supabase": "Open-Source Backend with Supabase",
    "docker": "Containerization with Docker",
    "kubernetes": "Orchestration with Kubernetes",
    "aws": "Cloud Infrastructure with AWS",
    "google_cloud": "Cloud with Google Cloud Platform",
    "azure": "Cloud with Microsoft Azure",
    "terraform": "Infrastructure as Code with Terraform",
    "ansible": "Automation with Ansible",
    "jenkins": "CI/CD with Jenkins",
    "github_actions": "CI/CD with GitHub Actions",
    "gitlab_ci": "CI/CD with GitLab CI",
    "git": "Version Control with Git",
    "linux": "Linux Fundamentals",
    "nginx": "Web Serving with NGINX",
    "prometheus": "Monitoring with Prometheus",
    "grafana": "Visualization with Grafana",
    "react_native": "Mobile Apps with React Native",
    "flutter": "Cross-Platform with Flutter",
    "swift": "iOS Development with Swift",
    "ios_development": "iOS App Development",
    "android_development": "Android App Development",
    "ionic": "Hybrid Mobile with Ionic",
    "xamarin": "Mobile with Xamarin",
    "pandas": "Data Analysis with Pandas",
    "numpy": "Numerical Computing with NumPy",
    "tensorflow": "Deep Learning with TensorFlow",
    "pytorch": "Deep Learning with PyTorch",
    "scikit_learn": "Machine Learning with scikit-learn",
    "langchain": "LLM Apps with LangChain",
    "openai_api": "AI Integration with OpenAI API",
    "hugging_face": "NLP with Hugging Face",
    "natural_language_processing": "Natural Language Processing",
    "computer_vision": "Computer Vision",
    "jupyter_notebooks": "Interactive Notebooks with Jupyter",
    "matplotlib": "Data Visualization with Matplotlib",
    "figma": "Design with Figma",
    "adobe_xd": "Design with Adobe XD",
    "sketch": "Design with Sketch",
    "photoshop": "Image Editing with Photoshop",
    "illustrator": "Vector Design with Illustrator",
    "ui_ux_design_principles": "UI/UX Design Principles",
    "wireframing": "Wireframing & Prototyping",
    "prototyping": "Interactive Prototyping",
    "design_systems": "Design Systems",
    "accessibility_a11y": "Web Accessibility (a11y)",
    "responsive_design": "Responsive Web Design",
    "jest": "Testing with Jest",
    "cypress": "E2E Testing with Cypress",
    "playwright": "E2E Testing with Playwright",
    "selenium": "Automated Testing with Selenium",
    "pytest": "Testing with pytest",
    "mocha": "Testing with Mocha",
    "unit_testing": "Unit Testing Fundamentals",
    "integration_testing": "Integration Testing",
    "tdd": "Test-Driven Development",
    "owasp_top_10": "Web Security: OWASP Top 10",
    "penetration_testing": "Penetration Testing",
    "cryptography": "Cryptography Fundamentals",
    "authentication_&_authorization": "Auth & Authorization",
    "network_security": "Network Security",
    "unity": "Game Dev with Unity",
    "unreal_engine": "Game Dev with Unreal Engine",
    "blender": "3D Modeling with Blender",
    "c++_for_games": "C++ for Game Development",
    "solidity": "Smart Contracts with Solidity",
    "web3_js": "Web3.js for DApps",
    "smart_contracts": "Smart Contract Development",
    "agile_methodologies": "Agile Methodologies",
    "scrum": "Scrum Framework",
    "code_review": "Code Review Best Practices",
    "technical_writing": "Technical Writing",
    "system_design": "System Design",
    "api_design": "API Design",
    "microservices_architecture": "Microservices Architecture",
    "java": "Java Programming",
    "go": "Go Programming",
    "rust": "Rust Programming",
    "c#": "C# Programming",
    "php": "PHP Web Development",
    "ruby": "Ruby Programming",
    "kotlin": "Kotlin Programming",
    "scala": "Scala Programming",
}

STEP_DESCRIPTIONS = {
    "html": "Learn semantic HTML5 structure, accessibility best practices, and SEO-friendly markup to build solid web foundations.",
    "css": "Master CSS layouts (Flexbox, Grid), responsive design, animations, and modern styling techniques for beautiful interfaces.",
    "javascript": "Deep dive into ES6+, async/await, closures, promises, and DOM manipulation to build interactive web applications.",
    "typescript": "Add static typing to JavaScript with interfaces, generics, and advanced TypeScript features for safer code.",
    "react": "Build component-based UIs with hooks, state management, and performance optimization using the React ecosystem.",
    "vue_js": "Build reactive user interfaces with Vue 3's Composition API, directives, and component architecture.",
    "angular": "Enterprise-scale applications with Angular's TypeScript-first approach, dependency injection, and RxJS.",
    "python": "Learn Python fundamentals, OOP, decorators, generators, and standard library mastery for versatile programming.",
    "sql": "Master SELECT queries, JOINs, aggregations, subqueries, and database design principles for effective data management.",
    "git": "Version control workflows, branching strategies, collaboration, and CI/CD integration using Git.",
    "docker": "Containerize applications with Docker for consistent development, testing, and deployment environments.",
    "node_js": "Build server-side applications with Node.js runtime, npm ecosystem, and asynchronous programming patterns.",
    "express_js": "Create RESTful APIs and web applications with Express.js middleware and routing architecture.",
    "fastapi": "Build high-performance APIs with FastAPI's async support, automatic docs, and Pydantic validation.",
    "postgresql": "Advanced PostgreSQL features including indexing, query optimization, window functions, and full-text search.",
    "mongodb": "Work with MongoDB's document model, aggregation pipeline, indexing, and replication for scalable NoSQL solutions.",
    "redis": "Leverage Redis for caching, session management, real-time data, and message queuing in high-performance apps.",
    "rest_api_design": "Design RESTful APIs following best practices for resource naming, status codes, pagination, and versioning.",
    "graphql": "Build flexible GraphQL APIs with schema design, resolvers, queries, mutations, and subscriptions.",
    "aws": "Master AWS core services including EC2, S3, Lambda, RDS, and VPC for cloud infrastructure management.",
    "kubernetes": "Orchestrate containers with Kubernetes covering pods, services, deployments, and cluster management.",
    "terraform": "Implement Infrastructure as Code with Terraform for multi-cloud resource provisioning and management.",
}

DIFFICULTY_LABELS = {0: "beginner", 1: "beginner", 2: "intermediate", 3: "intermediate", 4: "advanced", 5: "advanced"}


def _normalize(name):
    return name.lower().replace(' ', '_').replace('.', '_').replace('-', '_').replace('(', '').replace(')', '').replace('&', 'and').replace("'", '')


def topological_sort(skill_keys, prereq_map):
    graph = {key: [] for key in skill_keys}
    in_degree = {key: 0 for key in skill_keys}

    for key in skill_keys:
        for prereq in prereq_map.get(key, []):
            if prereq in skill_keys:
                graph[prereq].append(key)
                in_degree[key] += 1

    queue = [key for key, deg in in_degree.items() if deg == 0]
    sorted_keys = []

    while queue:
        key = queue.pop(0)
        sorted_keys.append(key)
        for neighbor in graph[key]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    remaining = [k for k in skill_keys if k not in sorted_keys]
    sorted_keys.extend(remaining)
    return sorted_keys


def select_resources(available_resources, preferences, count=4):
    lang = preferences.get("language", "en")
    lang_resources = [r for r in available_resources if r.get('language') == lang]
    if not lang_resources:
        lang_resources = [r for r in available_resources if r.get('language') == 'en']
    if not lang_resources:
        lang_resources = available_resources

    fmt = preferences.get("format", "any")
    if fmt != "any":
        fmt_resources = [r for r in lang_resources if r.get('type') == fmt]
        if fmt_resources:
            lang_resources = fmt_resources

    is_free_pref = preferences.get("is_free", True)
    if is_free_pref:
        free_resources = [r for r in lang_resources if r.get('is_free')]
        if free_resources:
            lang_resources = free_resources

    official = sorted([r for r in lang_resources if r.get('is_official')],
                      key=lambda r: (0 if r.get('type') in ('course', 'documentation') else 1))
    courses = sorted([r for r in lang_resources if not r.get('is_official')],
                     key=lambda r: (0 if r.get('type') in ('course', 'tutorial', 'video') else 1))

    main_resource = None
    additional_resources = []

    if official:
        main_resource = official[0]
        additional_resources = [r for r in official[1:] + courses][:count - 1]
    elif courses:
        main_resource = courses[0]
        additional_resources = courses[1:count]
    elif lang_resources:
        main_resource = lang_resources[0]
        additional_resources = lang_resources[1:count]

    return main_resource, additional_resources


def format_resource(r):
    if not r:
        return None
    return {
        "title": r.get('title', 'Untitled'),
        "url": r.get('url', ''),
        "type": r.get('type', 'article'),
        "is_free": r.get('is_free', True),
        "is_official": r.get('is_official', False),
        "author_or_platform": r.get('author_or_platform', ''),
    }


def generate_path(profile, goal, weekly_hours, preferences):
    skills_from_db = fetch_skills_for_job_role(goal)
    if not skills_from_db:
        return {"error": f"I couldn't find a career path for '{goal}'."}

    role_configs = fetch_role_skill_config(goal)
    config_by_skill_id = {c['skill_id']: c for c in role_configs}

    all_skill_ids = [s['id'] for s in skills_from_db]
    prereq_rows = fetch_prerequisites_for_skills(all_skill_ids)

    skill_keys_info = {}

    for s in skills_from_db:
        name = _normalize(s['name'])
        # Profile keys use skill_name.lower() from assessor; match both forms
        profile_key = s['name'].lower()
        skill_level = profile.get(name, profile.get(profile_key, -1))
        if skill_level >= 5:
            continue
        skill_keys_info[name] = {
            'id': s['id'],
            'name': s['name'],
            'difficulty_level': s.get('difficulty_level', 1),
            'user_level': skill_level if skill_level >= 0 else 0,
        }

    if not skill_keys_info:
        return {"error": "You already have advanced proficiency in all skills for this role."}

    # Build prereq map: for each skill key, list its prerequisite keys (if they're in our set)
    prereqs_for_topo = {}
    for key in skill_keys_info:
        prereqs_for_topo[key] = []

    for sid, prereqs in prereq_rows.items():
        source_key = None
        for k, v in skill_keys_info.items():
            if v['id'] == sid:
                source_key = k
                break
        if not source_key:
            continue
        for p in prereqs:
            p_key = _normalize(p['name'])
            if p_key in skill_keys_info and p_key not in prereqs_for_topo[source_key]:
                prereqs_for_topo[source_key].append(p_key)

    # Merge with fallback map for any relationships the DB doesn't have
    for key in skill_keys_info:
        db_prereqs = prereqs_for_topo.get(key, [])
        fallback_prereqs = PREREQ_FALLBACK.get(key, [])
        combined = list(set(db_prereqs + [p for p in fallback_prereqs if p in skill_keys_info]))
        prereqs_for_topo[key] = combined

    sorted_keys = topological_sort(list(skill_keys_info.keys()), prereqs_for_topo)

    # Compute dependency depth for each skill (longest path from a root)
    depth = {k: 0 for k in sorted_keys}
    for k in sorted_keys:
        for p in prereqs_for_topo.get(k, []):
            if p in depth:
                depth[k] = max(depth[k], depth[p] + 1)

    # Sort by depth first (respecting prereqs), then by config order as tiebreaker
    config_by_key = {}
    for c in role_configs:
        c_key = _normalize(c['skill_name'])
        config_by_key[c_key] = c

    order_sort_key = {k: config_by_key.get(k, {}).get('order', 999) for k in sorted_keys}
    sorted_keys.sort(key=lambda k: (depth.get(k, 0), order_sort_key.get(k, 999)))

    path_steps = []
    total_estimated_hours = 0

    for i, skill_key in enumerate(sorted_keys):
        info = skill_keys_info[skill_key]
        skill_id = info['id']
        user_level = info['user_level']

        config = config_by_key.get(skill_key, {})
        est_hours = config.get('estimated_hours', 20)

        difficulty_label = DIFFICULTY_LABELS.get(user_level, "beginner")

        step_title = STEP_TITLES.get(skill_key, f"Master {info['name']}")
        step_desc = STEP_DESCRIPTIONS.get(skill_key, f"Learn {info['name']} with focused study covering key concepts and best practices.")

        prefix_map = {"beginner": "Getting Started: ", "intermediate": "Building Proficiency: ", "advanced": "Advanced: "}
        prefix = prefix_map.get(difficulty_label, "")
        step_title_full = f"Step {i + 1}: {prefix}{step_title}"

        available_resources = fetch_resources_for_skill(skill_id)
        main_resource, additional_resources = select_resources(available_resources, preferences)

        total_estimated_hours += est_hours

        path_steps.append({
            "index": i + 1,
            "title": step_title_full,
            "description": step_desc,
            "skill_name": info['name'],
            "skill_key": skill_key,
            "estimated_hours": est_hours,
            "difficulty_level": info['difficulty_level'],
            "difficulty_label": difficulty_label,
            "user_skill_level": user_level,
            "main_resource": format_resource(main_resource),
            "additional_resources": [format_resource(r) for r in additional_resources if r]
        })

    total_weeks = round(total_estimated_hours / weekly_hours) if weekly_hours > 0 else 0
    if total_weeks < 1:
        total_weeks = 1

    goal_title = goal.replace("_", " ").title()
    intro_message = (
        f"Welcome to your personalized journey to becoming a {goal_title}! "
        f"This {total_weeks}-week path is tailored to your current skill level and learning preferences. "
        f"Each step builds on the previous one for a structured learning experience."
    )

    return {
        "path_title": f"Your Custom Path to Becoming a {goal_title}",
        "intro_message": intro_message,
        "estimated_weeks": total_weeks,
        "total_estimated_hours": total_estimated_hours,
        "steps": path_steps,
        "metadata": {"method": "prerequisite-aware-dag-v2", "skill_count": len(sorted_keys)}
    }
