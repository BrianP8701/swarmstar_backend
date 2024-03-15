from typing import List, Dict, Any

from swarmstar.models import *
from swarmstar import Swarmstar



class SwarmstarWrapper:
    @staticmethod
    def get_swarm_config(swarm_id: str) -> SwarmConfig:
        return SwarmConfig.get_swarm_config(swarm_id)

    @staticmethod
    def get_swarm_state(swarm_id: str) -> List[str]:
        return SwarmState.get_swarm_state(swarm_id)

    @staticmethod
    def get_swarm_history(swarm_id: str) -> List[str]:
        return SwarmHistory.get_swarm_history(swarm_id)

    @staticmethod
    def get_swarm_operation(swarm_operation_id: str) -> SwarmOperation:
        return SwarmOperation.get_swarm_operation(swarm_operation_id)

    @staticmethod
    def get_swarm_node(node_id: str) -> SwarmNode:
        return SwarmNode.get_swarm_node(node_id)

    @staticmethod
    def add_swarm_node(node: SwarmNode) -> None:
        SwarmNode.insert_swarm_node(node)

    @staticmethod
    def add_swarm_operation(operation: SwarmOperation) -> None:
        SwarmOperation.insert_swarm_operation(operation)

    @staticmethod
    def add_swarm_operation_id_to_swarm_history(swarm_id: str, operation_id: str) -> None:
        SwarmHistory.add_swarm_operation_id_to_swarm_history(swarm_id, operation_id)

    @staticmethod
    def add_swarm_config(swarm_config: SwarmConfig) -> None:
        SwarmConfig.add_swarm_config(swarm_config)

    @staticmethod
    def delete_swarmstar_space(swarm_id: str) -> None:
        Swarmstar.delete_swarmstar_space(swarm_id)

    @staticmethod
    def get_current_swarm_state_representation(swarm_id: str) -> Dict[str, Any]:
        swarm_state = SwarmstarWrapper.get_swarm_state(swarm_id)
        root_node_id = swarm_state[0]
        root_node = SwarmstarWrapper.get_swarm_node(root_node_id)
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
                child_node = SwarmstarWrapper.get_swarm_node(child_id)
                child_representation = SwarmstarWrapper._convert_node_to_d3_tree_node_recursive(child_node)
                node_representation["children"].append(child_representation)
        return node_representation

    @staticmethod
    def add_swarm_state(swarm_id: str, node_ids: List[str]):
        SwarmState.add_swarm_state(swarm_id, node_ids)

    @staticmethod
    def add_swarm_history(swarm_id: str, operation_ids: List[str]):
        SwarmHistory.add_swarm_history(swarm_id, operation_ids)
