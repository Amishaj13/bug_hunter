"""
Code Parser Agent - Analyzes C++ code structure
"""


from typing import Dict, Any
import json



class CodeParserAgent(BaseAgent):
    """Agent specialized in parsing and analyzing C++ code structure"""
    
    def __init__(self):
        system_prompt = """You are a C++ code analysis expert. Your role is to:
            1. Parse C++ code and identify its structure
            2. Extract functions, variables, and control flow
            3. Identify line-by-line code elements
            4. Detect potential problem areas

            Provide detailed, structured analysis in JSON format."""
        
        super().__init__(
            name="CodeParserAgent",
            system_prompt=system_prompt
        )
    
    def parse_code(self, code: str, context: str = "") -> Dict[str, Any]:
       
        template = """Analyze the following C++ code snippet and provide a structured analysis.

                Code:
                ```cpp
                {code}
                ```

                Context: {context}

                Provide your analysis in the following JSON format:
                {{
                    "functions": ["list of function names"],
                    "variables": ["list of variable names"],
                    "line_count": number,
                    "complexity": "low/medium/high",
                    "potential_issues": ["list of potential problem areas"],
                    "code_summary": "brief summary of what the code does"
                }}

                Return ONLY the JSON, no additional text."""
        
        try:
            response = self.invoke_with_template(
                template,
                code=code,
                context=context or "No additional context provided"
            )
            
            # Parse JSON response
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed = json.loads(response)
            logger.info(f"Successfully parsed code structure")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return basic structure
            return {
                "functions": [],
                "variables": [],
                "line_count": len(code.split('\n')),
                "complexity": "unknown",
                "potential_issues": [],
                "code_summary": "Unable to parse code structure"
            }
        except Exception as e:
            logger.error(f"Error parsing code: {e}")
            raise
    
    def identify_code_patterns(self, code: str) -> Dict[str, Any]:
                    
                    template = """Identify C++ patterns and idioms in this code:

                            ```cpp
                            {code}
                            ```

                            List any patterns you recognize (e.g., RAII, smart pointers, iterators, etc.)
                            Also note any anti-patterns or code smells.

                            Provide a concise analysis."""
                    
                    try:
                        response = self.invoke_with_template(template, code=code)
                        return {"patterns_analysis": response}
                    except Exception as e:
                        logger.error(f"Error identifying patterns: {e}")
                        return {"patterns_analysis": "Unable to identify patterns"}

# Global instance
code_parser_agent = CodeParserAgent()
