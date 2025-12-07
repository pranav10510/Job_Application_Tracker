"""
Company Research Agent
Autonomously researches companies and compiles comprehensive reports
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from langchain.prompts import ChatPromptTemplate
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CompanyResearchAgent(BaseAgent):
    """Agent for automated company research"""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        super().__init__(model_name=model_name, temperature=0.3)
        
        # Register research tools
        self.register_tool(
            "web_search",
            self.web_search,
            "Search the web for company information"
        )
        self.register_tool(
            "website_scraper",
            self.scrape_website,
            "Extract content from company website"
        )
        self.register_tool(
            "news_search",
            self.search_news,
            "Find recent news about company"
        )
        self.register_tool(
            "salary_lookup",
            self.lookup_salary,
            "Get salary data for position"
        )
        self.register_tool(
            "culture_analyzer",
            self.analyze_culture,
            "Analyze company culture from reviews"
        )
        self.register_tool(
            "report_generator",
            self.generate_report,
            "Compile findings into structured report"
        )
        
        logger.info("CompanyResearchAgent initialized")
    
    def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search web for information
        (In production, integrate with Google/Bing API)
        """
        logger.info(f"Searching web: {query}")
        
        # Placeholder - integrate with actual search API
        # Using DuckDuckGo or Google Custom Search
        try:
            # Simulated search results
            results = [
                {
                    'title': f'Result for {query}',
                    'url': f'https://example.com/search/{query.replace(" ", "-")}',
                    'snippet': f'Information about {query}...',
                    'source': 'web'
                }
            ]
            
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape company website for information"""
        logger.info(f"Scraping website: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information
            title = soup.find('title')
            description = soup.find('meta', attrs={'name': 'description'})
            
            # Get main text content
            paragraphs = soup.find_all('p')
            text_content = ' '.join([p.get_text() for p in paragraphs[:10]])
            
            result = {
                'url': url,
                'title': title.get_text() if title else '',
                'description': description['content'] if description else '',
                'content_preview': text_content[:500],
                'scraped_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully scraped {url}")
            return result
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }
    
    def search_news(self, company: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search for recent company news"""
        logger.info(f"Searching news for: {company}")
        
        # Placeholder - integrate with News API or Google News
        query = f"{company} news recent"
        results = self.web_search(query, num_results=5)
        
        # Filter and format as news
        news = []
        for result in results:
            news.append({
                'title': result['title'],
                'url': result['url'],
                'summary': result['snippet'],
                'source': 'news',
                'date': datetime.now().isoformat()
            })
        
        logger.info(f"Found {len(news)} news articles")
        return news
    
    def lookup_salary(self, company: str, position: str, 
                     location: Optional[str] = None) -> Dict[str, Any]:
        """Look up salary information"""
        logger.info(f"Looking up salary: {position} at {company}")
        
        # Placeholder - integrate with Glassdoor/Levels.fyi API
        # For now, use AI to estimate based on general knowledge
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a salary research expert.
            Provide estimated salary range based on company, position, and location.
            
            Return JSON:
            {{
                "min": 80000,
                "max": 120000,
                "median": 100000,
                "currency": "USD",
                "confidence": "medium",
                "sources": ["glassdoor", "levels.fyi"]
            }}
            """),
            ("human", "Company: {company}\nPosition: {position}\nLocation: {location}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "company": company,
            "position": position,
            "location": location or "United States"
        })
        
        try:
            salary_data = json.loads(response.content)
            logger.info(f"Salary range: ${salary_data.get('min')}-${salary_data.get('max')}")
            return salary_data
        except json.JSONDecodeError:
            logger.warning("Failed to parse salary data")
            return {
                "min": 0,
                "max": 0,
                "median": 0,
                "currency": "USD",
                "confidence": "low",
                "error": "Could not determine salary"
            }
    
    def analyze_culture(self, company: str) -> Dict[str, Any]:
        """Analyze company culture from reviews and data"""
        logger.info(f"Analyzing culture: {company}")
        
        # Search for reviews
        query = f"{company} glassdoor reviews culture"
        results = self.web_search(query, num_results=3)
        
        # Use AI to summarize culture insights
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a company culture analyst.
            Based on the search results, provide culture insights.
            
            Return JSON:
            {{
                "work_life_balance": "good/average/poor",
                "management": "supportive/mixed/challenging",
                "growth_opportunities": "excellent/good/limited",
                "culture_keywords": ["innovative", "fast-paced"],
                "pros": ["..."],
                "cons": ["..."],
                "overall_rating": 3.8
            }}
            """),
            ("human", "Company: {company}\nSearch results: {results}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "company": company,
            "results": json.dumps(results)
        })
        
        try:
            culture_data = json.loads(response.content)
            logger.info(f"Culture analysis complete: {culture_data.get('overall_rating')}/5")
            return culture_data
        except json.JSONDecodeError:
            logger.warning("Failed to parse culture data")
            return {
                "work_life_balance": "unknown",
                "management": "unknown",
                "growth_opportunities": "unknown",
                "culture_keywords": [],
                "pros": [],
                "cons": [],
                "overall_rating": 0
            }
    
    def generate_report(self, research_data: Dict[str, Any]) -> str:
        """Generate comprehensive research report"""
        logger.info("Generating research report...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research report writer.
            Create a comprehensive, professional report from the research data.
            
            Format:
            # Company Research Report: [Company]
            
            ## Overview
            [Summary]
            
            ## Recent News
            [Key developments]
            
            ## Compensation
            [Salary insights]
            
            ## Culture & Work Environment
            [Culture analysis]
            
            ## Recommendations
            [Interview prep suggestions]
            """),
            ("human", "Research data: {data}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"data": json.dumps(research_data, indent=2)})
        
        report = response.content
        logger.info("Report generated")
        return report
    
    def research(self, company: str, position: str = None, 
                location: str = None) -> Dict[str, Any]:
        """
        Run complete research workflow
        
        Args:
            company: Company name
            position: Job position (optional)
            location: Location (optional)
        """
        task = f"Research {company}" + (f" for {position}" if position else "")
        
        # Create custom initial state
        initial_state = self.create_initial_state(task)
        initial_state['research_params'] = {
            'company': company,
            'position': position,
            'location': location
        }
        
        result = self.run(task, research_params={
            'company': company,
            'position': position,
            'location': location
        })
        
        return result
    
    # Override think node for research-specific planning
    def think_node(self, state: AgentState) -> AgentState:
        """Create research-specific plan"""
        logger.info("Planning research workflow...")
        
        params = state.get('research_params', {})
        company = params.get('company', 'Unknown')
        position = params.get('position')
        
        # Create comprehensive research plan
        plan = [
            f"Search web for {company} overview",
            f"Scrape {company} official website",
            f"Search recent news about {company}",
            f"Analyze {company} culture and reviews"
        ]
        
        if position:
            plan.append(f"Lookup salary data for {position}")
        
        plan.append("Compile findings into report")
        
        state['plan'] = plan
        state['status'] = "executing"
        
        state['messages'].append({
            'role': 'assistant',
            'content': f"Research plan created with {len(plan)} steps",
            'timestamp': datetime.now().isoformat()
        })
        
        return state
    
    def approve_and_execute(self, state: AgentState) -> Dict[str, Any]:
        """Compile and return research report"""
        logger.info("Compiling final research report...")
        
        # Extract all research data
        research_data = {
            'company': state.get('research_params', {}).get('company'),
            'position': state.get('research_params', {}).get('position'),
            'findings': {}
        }
        
        for obs in state.get('observations', []):
            tool = obs.get('tool')
            result = obs.get('result')
            
            if tool and result:
                research_data['findings'][tool] = result
        
        # Generate final report
        report = self.generate_report(research_data)
        
        return {
            'status': 'completed',
            'report': report,
            'data': research_data,
            'timestamp': datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    # Test research agent
    agent = CompanyResearchAgent()
    
    print("Running Company Research Agent...")
    result = agent.research(
        company="Google",
        position="Software Engineer",
        location="Mountain View, CA"
    )
    
    print("\n=== Research Result ===")
    print(f"Status: {result.get('status')}")
    print(f"Steps completed: {len(result.get('observations', []))}")
    
    # Show observations
    print("\n=== Research Steps ===")
    for i, obs in enumerate(result.get('observations', []), 1):
        tool = obs.get('tool', 'unknown')
        print(f"{i}. {tool}: {obs.get('step')}")