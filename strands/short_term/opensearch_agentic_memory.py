import requests
from typing import Dict, Optional, Any


class OpenSearchAgenticMemory:
    def __init__(self, cluster_url: str, username: str, password: str,
                 memory_container_id: str = None,
                 memory_container_name: str = "Strands agent memory container",
                 memory_container_description: str = "default"):
        self.memory_container_id = memory_container_id
        self.memory_container_name = memory_container_name
        self.base_url = cluster_url
        self.auth = (username, password)
        self.headers = {"Content-Type": "application/json"}

        if memory_container_id is None:
            default_container_id = self.get_memory_container(memory_container_name)
            if default_container_id is None:
                self.create_memory_container(memory_container_name, memory_container_description, memory_container_name)
            else:
                print("Find memory container with id '{}' by name '{}'".format(default_container_id, memory_container_name))
                self.memory_container_id = default_container_id


    def get_memory_container(self, name: str) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/_search"
        body = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "name.keyword": name
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "created_time": {
                        "order": "asc"
                    }
                }
            ],
            "size": 1
        }

        response = self._make_request("GET", url, json=body)
        first_hit = self._get_first_hit(response)
        if first_hit is None:
            return None
        return first_hit['_id']

    def create_memory_container(self, name: str, description: str, index_prefix: str,
                                embedding_model_id: Optional[str] = None,
                                llm_id: Optional[str] = None) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/_create"
        body = {
            "name": name,
            "description": description,
            "configuration": {
                "index_prefix": index_prefix,
                "use_system_index": False,
                "disable_session": False
            }
        }

        response = self._make_request("POST", url, json=body)
        self.memory_container_id = response['memory_container_id']
        print("Created memory container with id '{}'".format(self.memory_container_id))
        return response

    def create_session(self, session_id: str, metadata: Dict[str, Any], agents: Dict[str, Any] = None) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/sessions"
        body = {
            "session_id": session_id,
        }
        if metadata:
            body["metadata"] = metadata
        if agents:
            body["agents"] = agents

        return self._make_request("POST", url, json=body)

    def update_session(self, session_id: str, metadata: Dict[str, Any], agents: Dict[str, Any]) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/sessions/{session_id}"
        body = {
            "name": session_id,
        }
        if metadata:
            body["metadata"] = metadata
        if agents:
            body["agents"] = agents

        return self._make_request("PUT", url, json=body)

    def get_session(self, session_id: str) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/sessions/{session_id}"
        return self._make_request("GET", url)

    def delete_session(self, session_id: str) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/sessions/{session_id}"

        return self._make_request("DELETE", url)

    def add_message(self, session_id: str, agent_id: str, message: Dict[str, Any]) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories"
        body = {
            "namespace": {
                "session_id": session_id,
                "agent_id": agent_id,
            },
            "infer": False,
            "memory_type": "conversational",
        }
        if "message" in message:
            body["messages"] = [
                message['message']
            ]
            message.pop('message', None)
        if "message_id" in message:
            body["message_id"] = message['message_id']
            message.pop('message_id', None)
        message = {k: v for k, v in message.items() if v is not None}
        if message:
            body['metadata'] = message

        return self._make_request("POST", url, json=body)

    def search_session(self, session_id: str) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/sessions/_search"
        body = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "namespace.session_id": session_id
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "message_id": {
                        "order": "asc"
                    }
                }
            ],
            "size": 1
        }

        response = self._make_request("GET", url, json=body)
        messages: list[Dict[str, Any]] = []
        search_response = self._get_hits(response)
        if search_response:
            for doc in search_response:
                messages.append(self._parse_message_from_source(doc['_source']))
            return messages
        return None

    def list_message(self, session_id: str, agent_id: str, limit: Optional[int] = None, offset: int = 0) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/working/_search"
        body = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "namespace.session_id": session_id
                            }
                        },
                        {
                            "term": {
                                "namespace.agent_id": agent_id
                            }
                        },
                        {
                            "term": {
                                "namespace_size": 2
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "message_id": {
                        "order": "asc"
                    }
                }
            ]
        }

        if limit:
            body['size'] = limit
        if offset:
            body['from'] = offset

        response = self._make_request("GET", url, json=body)
        messages: list[Dict[str, Any]] = []
        search_response = self._get_hits(response)
        if search_response:
            for doc in search_response:
                messages.append(self._parse_message_from_source(doc['_source']))
            return messages
        return None

    def get_message(self, session_id: str, agent_id:str, message_id: int) -> Dict:
        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/working/_search"
        body = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "namespace.session_id": session_id
                            }
                        },
                        {
                            "term": {
                                "namespace.agent_id": agent_id
                            }
                        },
                        {
                            "term": {
                                "namespace_size": 2
                            }
                        },
                        {
                            "term": {
                                "message_id": message_id
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "created_time": {
                        "order": "desc"
                    }
                }
            ]
        }

        response = self._make_request("GET", url, json=body)
        result = self._parse_message_from_source(response)
        return result

    def update_message(self, session_id: str, message_id: int, new_message:Dict[str, Any]) -> Dict:
        message_doc = self.get_message(session_id, message_id)

        if message_doc is None:
            return None


        message_doc_id = message_doc['_id']
        message_source = message_doc['_source']

        created_at = message_source['metadata']['created_at']
        new_message['created_at'] = created_at

        if "message" in new_message:
            message_source["messages"] = [
                new_message['message']
            ]
            new_message.pop('message', None)
        if new_message:
            message_source['metadata'] = new_message

        url = f"{self.base_url}/_plugins/_ml/memory_containers/{self.memory_container_id}/memories/working/{message_doc_id}"

        response = self._make_request("PUT", url, json=message_source)
        return response

    def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=self.headers,
                verify=False,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if '404' in str(e):
                return None
            error_details = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = f" - Response: {e.response.text}"
                except:
                    pass
            raise Exception(f"API request failed: {str(e)}{error_details}")

    def _parse_message_from_source(self, response: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "message": response['messages'][0],
            "message_id": response['message_id']
        }
        result.update(response['metadata'])
        return result

    def _get_hits(self, response: Dict[str, Any]) -> Optional[list[Dict[str, Any]]]:
        try:
            # Check if response exists and is a dict
            if not response or not isinstance(response, dict):
                return None

            # Navigate through the nested structure safely
            hits = response.get('hits', {})
            if not hits or not isinstance(hits, dict):
                return None

            hits_array = hits.get('hits', [])
            if not hits_array or not isinstance(hits_array, list):
                return None

            return hits_array

        except Exception as e:
            print(f"Error occurred while extracting _source: {str(e)}")
            return None

    def _get_first_hit(self, response: Dict[str, Any]) -> Optional[str]:
        try:
            # Check if response exists and is a dict
            if not response or not isinstance(response, dict):
                return None

            # Navigate through the nested structure safely
            hits = response.get('hits', {})
            if not hits or not isinstance(hits, dict):
                return None

            hits_array = hits.get('hits', [])
            if not hits_array or not isinstance(hits_array, list):
                return None

            # Get the first hit
            first_hit = hits_array[0] if hits_array else None
            if not first_hit or not isinstance(first_hit, dict):
                return None

            # Return the _source
            return first_hit #.get('_source')

        except Exception as e:
            print(f"Error occurred while extracting _source: {str(e)}")
            return None