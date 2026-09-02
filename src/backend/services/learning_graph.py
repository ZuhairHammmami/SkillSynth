"""Learning graph — knowledge-graph payload and topological sort.

Pure graph utilities called by learning_service.generate_path and
the learning router. No serialization; depends only on catalog_repository.
"""

from collections import defaultdict, deque

from backend.repositories import catalog_repository


def build_graph(db) -> dict:
    """Knowledge-graph payload (nodes/edges/categories) for
    GET /learning/graph; node decoration comes from catalog counts."""
    counts = catalog_repository.count_skill_resources(db)
    categories = catalog_repository.get_all_categories(db)
    nodes = [{
        "id": s.id, "name": s.name, "difficulty": s.difficulty_level or 1,
        "icon": s.icon, "color": s.color,
        "category_ids": [s.category_id] if s.category_id else [],
        "resource_count": counts.get(s.id, 0),
    } for s in catalog_repository.get_all_skills(db)]
    edges = [{"source": p, "target": sid, "type": "prerequisite"}
             for sid, prereqs in
             catalog_repository.get_prerequisite_graph(db).items()
             for p in prereqs]
    return {"nodes": nodes, "edges": edges,
            "categories": [{"id": c.id, "name": c.name} for c in categories]}


def topological_sort(db) -> list[int]:
    """Kahn topo-sort over all skills; deterministic id tie-break."""
    return [s.id for s in _order_by_prereqs(
        db, catalog_repository.get_all_skills(db))]


def _order_by_prereqs(db, skill_rows: list) -> list:
    """Topo-order a skill subset so prerequisites come first."""
    graph = catalog_repository.get_prerequisite_graph(db)
    ids = {s.id for s in skill_rows}
    by_id = {s.id: s for s in skill_rows}
    indeg = {sid: len([p for p in graph.get(sid, []) if p in ids]) for sid in ids}
    dependents: dict[int, list[int]] = defaultdict(list)
    for sid in ids:
        for prereq in graph.get(sid, []):
            if prereq in ids:
                dependents[prereq].append(sid)
    queue = deque(sorted(sid for sid, deg in indeg.items() if deg == 0))
    ordered = []
    while queue:
        sid = queue.popleft()
        ordered.append(by_id[sid])
        for dep in sorted(dependents[sid]):
            indeg[dep] -= 1
            if indeg[dep] == 0:
                queue.append(dep)
    ordered.extend(by_id[sid] for sid in sorted(ids - {s.id for s in ordered}))
    return ordered
