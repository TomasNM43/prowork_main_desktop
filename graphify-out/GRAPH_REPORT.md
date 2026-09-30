# Graph Report - Pro_Work-main  (2026-08-29)

## Corpus Check
- Corpus is ~29,129 words - fits in a single context window. You may not need a graph.

## Summary
- 201 nodes · 346 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Graphify Platform Workflows
- Main GUI Session Control
- User Permissions Metadata
- Activity Tracking Models
- Justification Break Handling
- Login and Logging
- Runtime Dependencies
- Graph Query Navigation
- Activity Dialog
- Camera Capture Thread
- Commission Dialog
- Streaming Server

## God Nodes (most connected - your core abstractions)
1. `GUI` - 38 edges
2. `solicitud()` - 27 edges
3. `Justificaciones` - 17 edges
4. `Graphify` - 16 edges
5. `Tracker` - 12 edges
6. `Lista` - 12 edges
7. `Python Runtime Dependencies` - 11 edges
8. `Programa` - 10 edges
9. `Tiempo` - 10 edges
10. `Camara` - 9 edges

## Surprising Connections (you probably didn't know these)
- `PRO_WORK` --conceptually_related_to--> `Python Runtime Dependencies`  [INFERRED]
  README.md → requirements.txt
- `GUI` --uses--> `Camara`  [INFERRED]
  App/GUI.py → App/Camara.py
- `GUI` --uses--> `Actividades`  [INFERRED]
  App/GUI.py → App/Dialogs/Actividades.py
- `GUI` --uses--> `Comision`  [INFERRED]
  App/GUI.py → App/Dialogs/Comision.py
- `GUI` --uses--> `Justificaciones`  [INFERRED]
  App/GUI.py → App/Dialogs/Justificaciones.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Full Pipeline** — app__github_skills__copilot_skills_graphify_skill_file_detection, app__github_skills__copilot_skills_graphify_skill_structural_extraction, app__github_skills__copilot_skills_graphify_skill_semantic_extraction, app__github_skills__copilot_skills_graphify_skill_graph_build, app__github_skills__copilot_skills_graphify_skill_graph_health_check, app__github_skills__copilot_skills_graphify_skill_community_labeling, app__github_skills__copilot_skills_graphify_skill_manifest_and_cost_tracking [EXTRACTED 1.00]
- **Graph Query Feedback Loop** — app__github_skills__copilot_skills_graphify_references_query_constrained_query_expansion, app__github_skills__copilot_skills_graphify_references_query_breadth_first_traversal, app__github_skills__copilot_skills_graphify_references_query_depth_first_traversal, app__github_skills__copilot_skills_graphify_references_query_save_result_feedback, app__github_skills__copilot_skills_graphify_references_query_work_memory_reflection [INFERRED 0.95]
- **Graph Export Ecosystem** — app__github_skills__copilot_skills_graphify_references_exports_wiki_export, app__github_skills__copilot_skills_graphify_references_exports_neo4j_export, app__github_skills__copilot_skills_graphify_references_exports_falkordb_export, app__github_skills__copilot_skills_graphify_references_exports_svg_export, app__github_skills__copilot_skills_graphify_references_exports_graphml_export, app__github_skills__copilot_skills_graphify_references_exports_mcp_graph_server [EXTRACTED 1.00]

## Communities (15 total, 3 thin omitted)

### Community 0 - "Graphify Platform Workflows"
Cohesion: 0.07
Nodes (42): Folder Watcher, Semantic Update Flag, URL Ingestion, URL Ingestion and Folder Watch, FalkorDB Export, Graph Exports, GraphML Export, MCP Graph Server (+34 more)

### Community 1 - "Main GUI Session Control"
Cohesion: 0.12
Nodes (3): GUI, QCloseEvent, QMainWindow

### Community 2 - "User Permissions Metadata"
Cohesion: 0.16
Nodes (9): Manager, iniciar_polling_permisos(), _loop_polling(), _mostrar_dialogo(), _Senales, solicitud(), Usuario, array (+1 more)

### Community 3 - "Activity Tracking Models"
Cohesion: 0.15
Nodes (5): QThread, Tracker, Lista, Programa, Tiempo

### Community 4 - "Justification Break Handling"
Cohesion: 0.17
Nodes (3): Justificaciones, QDialog, QDateTime

### Community 5 - "Login and Logging"
Cohesion: 0.19
Nodes (8): get_logger(), AppLogger — Logging centralizado para ProWork. Escribe en ~/prowork.log y…, Inicializa el sistema de logging. Llamar UNA sola vez desde main.py., Devuelve un logger con el nombre dado (usar __name__ del módulo)., setup_logging(), Login, QDialog, Logger

### Community 6 - "Runtime Dependencies"
Cohesion: 0.17
Nodes (12): PRO_WORK, Face Recognition, Flask, NumPy, OpenCV Python, Oracle Database Drivers, Pillow, PyAutoGUI (+4 more)

### Community 7 - "Graph Query Navigation"
Cohesion: 0.36
Nodes (8): Breadth-First Traversal, Constrained Query Expansion, Depth-First Traversal, Graph Query, Node Explanation, Saved Query Result Feedback, Shortest Path Query, Work Memory Reflection

### Community 11 - "Streaming Server"
Cohesion: 0.40
Nodes (3): _generar(), stream(), route

## Knowledge Gaps
- **26 isolated node(s):** `Semantic Extraction Cache`, `Hyperedge Extraction`, `Semantic Similarity Edges`, `Shortest Path Query`, `Node Explanation` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GUI` connect `Main GUI Session Control` to `User Permissions Metadata`, `Activity Tracking Models`, `Justification Break Handling`, `Login and Logging`, `Activity Dialog`, `Camera Capture Thread`, `Commission Dialog`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `Tracker` connect `Activity Tracking Models` to `Main GUI Session Control`, `User Permissions Metadata`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `solicitud()` connect `User Permissions Metadata` to `Activity Dialog`, `Main GUI Session Control`, `Justification Break Handling`, `Login and Logging`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `GUI` (e.g. with `Camara` and `Actividades`) actually correct?**
  _`GUI` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Tracker` (e.g. with `GUI` and `Lista`) actually correct?**
  _`Tracker` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Semantic Extraction Cache`, `Hyperedge Extraction`, `Semantic Similarity Edges` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Graphify Platform Workflows` be split into smaller, more focused modules?**
  _Cohesion score 0.07084785133565621 - nodes in this community are weakly interconnected._