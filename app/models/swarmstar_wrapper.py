from typing import Dict, Any

from swarmstar.models import SwarmNode, SwarmState

class SwarmstarWrapper:
    @staticmethod
    def get_current_swarm_state_representation(swarm_id: str) -> Dict[str, Any]:
        swarm_state = SwarmState.get(swarm_id)
        root_node_id = swarm_state[0]
        root_node = SwarmNode.get(root_node_id)
        swarm_state_representation = SwarmstarWrapper._convert_node_to_d3_tree_node_recursive(root_node)
        return swarm_state_representation

    @staticmethod
    def _convert_node_to_d3_tree_node_recursive(node: SwarmNode):
        is_leaf_node = len(node.children_ids) == 0
        is_terminated = not node.alive
        if is_terminated: status = "terminated"
        elif is_leaf_node: status = "active"
        else: status = "waiting"
        
        node_representation = {
            "name": node.name,
            "attributes": {
                "directive": node.message,
                "node_id": node.id,
                "status": status
            }
        }
        
        if not is_leaf_node:
            node_representation["children"] = []
            for child_id in node.children_ids:
                child_node = SwarmNode.get(child_id)
                child_representation = SwarmstarWrapper._convert_node_to_d3_tree_node_recursive(child_node)
                node_representation["children"].append(child_representation)
        return node_representation
