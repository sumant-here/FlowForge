from collections import defaultdict, deque
from typing import Dict, List, Any, Set, Tuple
from app.core.exceptions import WorkflowCyclicError

class DAGEngine:
    @staticmethod
    def validate_and_sort(definition: Dict[str, Any]) -> List[List[str]]:
        """
        Validates DAG for cycles using Kahn's algorithm and computes parallel execution levels (layers).
        Returns a list of node ID lists, where each list contains nodes that can run concurrently in parallel.
        """
        nodes = definition.get("nodes", [])
        edges = definition.get("edges", [])
        
        node_ids = {n["id"] if isinstance(n, dict) else n.id for n in nodes}
        in_degree = {nid: 0 for nid in node_ids}
        adj_list = defaultdict(list)
        
        for e in edges:
            src = e["source"] if isinstance(e, dict) else e.source
            tgt = e["target"] if isinstance(e, dict) else e.target
            if src in node_ids and tgt in node_ids:
                adj_list[src].append(tgt)
                in_degree[tgt] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        layers: List[List[str]] = []
        processed_count = 0
        
        while queue:
            current_layer = []
            layer_size = len(queue)
            for _ in range(layer_size):
                curr = queue.popleft()
                current_layer.append(curr)
                processed_count += 1
                for neighbor in adj_list[curr]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            layers.append(current_layer)

        if processed_count != len(node_ids):
            # Cyclic dependency found
            unresolved = [nid for nid, deg in in_degree.items() if deg > 0]
            raise WorkflowCyclicError(unresolved)

        return layers

    @staticmethod
    def get_ready_nodes(
        definition: Dict[str, Any],
        completed_node_states: Dict[str, Dict[str, Any]] # node_id -> {"status": "SUCCEEDED", "output": {...}}
    ) -> List[str]:
        """Determines which child nodes have all prerequisite parent conditions fulfilled."""
        nodes = definition.get("nodes", [])
        edges = definition.get("edges", [])
        
        node_map = {n["id"] if isinstance(n, dict) else n.id: n for n in nodes}
        parents_map = defaultdict(list)
        
        for e in edges:
            src = e["source"] if isinstance(e, dict) else e.source
            tgt = e["target"] if isinstance(e, dict) else e.target
            cond = e.get("condition", "success") if isinstance(e, dict) else getattr(e, "condition", "success")
            parents_map[tgt].append((src, cond))

        ready = []
        for nid in node_map:
            if nid in completed_node_states:
                continue # Already executed
            
            parents = parents_map.get(nid, [])
            if not parents:
                ready.append(nid)
                continue
            
            all_satisfied = True
            for parent_id, condition in parents:
                if parent_id not in completed_node_states:
                    all_satisfied = False
                    break
                
                parent_info = completed_node_states[parent_id]
                p_status = parent_info.get("status")
                
                if condition == "success" and p_status != "SUCCEEDED":
                    all_satisfied = False
                    break
                elif condition == "failure" and p_status != "FAILED":
                    all_satisfied = False
                    break
                elif condition == "always" and p_status not in ("SUCCEEDED", "FAILED"):
                    all_satisfied = False
                    break

            if all_satisfied:
                ready.append(nid)

        return ready
