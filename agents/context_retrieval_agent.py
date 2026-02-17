"""
Context Retrieval Agent - Retrieves relevant documentation using MCP server
"""

from mcp_client.client import mcp_client

from typing import List, Dict, Any
logger = setup_logger(__name__)

class ContextRetrievalAgent(BaseAgent):
    """Agent specialized in retrieving relevant context from documentation"""
    
    def __init__(self):
        system_prompt = """You are a documentation retrieval expert. Your role is to:
                1. Formulate effective search queries for bug documentation
                2. Retrieve relevant information from the manual of known bugs
                3. Synthesize retrieved information into useful context
                4. Identify the most relevant documentation for specific bugs"""
                        
        super().__init__(
            name="ContextRetrievalAgent",
            system_prompt=system_prompt
        )
        
        self.mcp_client = mcp_client
    
    def retrieve_bug_context(
        self,
        code: str,
        bug_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a detected bug
        
        Args:
            code: Code snippet with bug
            bug_info: Information about detected bug
            
        Returns:
            Dictionary with retrieved context
        """
        # Generate search queries
        queries = self._generate_search_queries(code, bug_info)
        
        # Search documents using MCP server
        all_results = []
        for query in queries:
            try:
                results = self.mcp_client.search_documents_sync(query)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error searching documents: {e}")
        
        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        
        # Synthesize context
        context = self._synthesize_context(unique_results)
        
        return {
            "retrieved_documents": unique_results[:5],  # Top 5
            "synthesized_context": context,
            "total_documents_found": len(unique_results)
        }
    
    def _generate_search_queries(
        self,
        code: str,
        bug_info: Dict[str, Any]
    ) -> List[str]:
        """
        Generate effective search queries
        
        Args:
            code: Code snippet
            bug_info: Bug information
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Extract bug type if available
        bugs_found = bug_info.get('bugs_found', [])
        if bugs_found:
            for bug in bugs_found[:3]:  # Top 3 bugs
                bug_type = bug.get('bug_type', '')
                description = bug.get('description', '')
                
                if bug_type:
                    queries.append(f"C++ {bug_type}")
                    queries.append(f"{bug_type} bug example")
                
                if description:
                    # Extract key terms from description
                    queries.append(description[:100])
        
        # Add generic query
        queries.append("C++ common bugs")
        
        # Extract keywords from code
        template = """Extract 2-3 key technical terms from this code that would be useful for searching bug documentation:

Code:
{code}

Return only the terms, comma-separated."""
        
        try:
            terms = self.invoke_with_template(template, code=code[:500])
            queries.append(terms.strip())
        except Exception as e:
            logger.warning(f"Failed to extract search terms: {e}")
        
        return queries[:5]  # Limit to 5 queries
    
    def _deduplicate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate documents
        
        Args:
            results: List of search results
            
        Returns:
            Deduplicated results sorted by score
        """
        seen_texts = set()
        unique = []
        
        for result in results:
            text = result.get('text', '')
            text_hash = hash(text[:200])  # Hash first 200 chars
            
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique.append(result)
        
        # Sort by score (descending)
        unique.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return unique
    
    def _synthesize_context(
        self,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesize retrieved documents into coherent context
        
        Args:
            results: Retrieved documents
            
        Returns:
            Synthesized context string
        """
        if not results:
            return "No relevant documentation found."
        
        # Take top 3 most relevant documents
        top_docs = results[:3]
        
        context_parts = []
        for i, doc in enumerate(top_docs, 1):
            text = doc.get('text', '')
            score = doc.get('score', 0)
            context_parts.append(f"[Document {i}, relevance: {score:.2f}]\n{text[:300]}...")
        
        return "\n\n".join(context_parts)

# Global instance
context_retrieval_agent = ContextRetrievalAgent()
