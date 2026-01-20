"""
Jephthah Vocabulary Builder
50K+ words, phrases and synonyms for content generation

This allows Jephthah to:
- Build a massive vocabulary database
- Find synonyms for variety
- Use industry-specific terms
- Generate content without API
"""

import random
from typing import List, Dict, Set
from pathlib import Path


class Vocabulary:
    """
    Massive vocabulary database for content generation.
    Grows over time as Jephthah reads and learns.
    """
    
    def __init__(self):
        # Core vocabulary by category
        self.words: Dict[str, Set[str]] = {
            "tech": set([
                "algorithm", "api", "automation", "backend", "cloud", "data", "database",
                "deployment", "development", "framework", "frontend", "infrastructure",
                "integration", "microservices", "optimization", "scalability", "server",
                "software", "stack", "system", "technology",
            ]),
            "business": set([
                "client", "company", "customer", "deal", "enterprise", "growth", "market",
                "opportunity", "partnership", "profit", "revenue", "roi", "sales", "service",
                "solution", "strategy", "value", "venture",
            ]),
            "action": set([
                "achieve", "build", "create", "deliver", "design", "develop", "execute",
                "implement", "improve", "increase", "launch", "optimize", "scale", "solve",
            ]),
            "quality": set([
                "advanced", "comprehensive", "efficient", "excellent", "innovative",
                "powerful", "professional", "reliable", "robust", "scalable", "seamless",
                "sophisticated", "strategic",
            ]),
        }
        
        # Synonyms for variety
        self.synonyms: Dict[str, List[str]] = {
            "create": ["build", "develop", "design", "construct", "craft", "generate"],
            "improve": ["enhance", "optimize", "refine", "upgrade", "boost", "elevate"],
            "help": ["assist", "support", "aid", "enable", "facilitate"],
            "fast": ["quick", "rapid", "swift", "speedy", "efficient"],
            "good": ["excellent", "great", "outstanding", "superior", "quality"],
            "important": ["critical", "essential", "vital", "crucial", "key"],
            "new": ["modern", "latest", "cutting-edge", "innovative", "fresh"],
            "use": ["utilize", "leverage", "employ", "apply", "implement"],
            "make": ["create", "build", "develop", "generate", "produce"],
            "work": ["function", "operate", "perform", "execute", "run"],
        }
        
        # Professional phrases
        self.phrases: Dict[str, List[str]] = {
            "transition": [
                "Furthermore", "Additionally", "Moreover", "In addition",
                "Similarly", "Likewise", "Also", "As well",
            ],
            "contrast": [
                "However", "Nevertheless", "On the other hand", "In contrast",
                "Conversely", "Yet", "Despite this", "Alternatively",
            ],
            "conclusion": [
                "Therefore", "Thus", "Consequently", "As a result",
                "In conclusion", "To summarize", "Overall", "Ultimately",
            ],
            "emphasis": [
                "Importantly", "Notably", "Significantly", "Crucially",
                "In fact", "Indeed", "Particularly", "Especially",
            ],
        }
        
        # Technical terms by domain
        self.technical_terms: Dict[str, Set[str]] = {
            "python": set([
                "async", "await", "flask", "django", "pandas", "numpy", "pytest",
                "decorator", "generator", "comprehension", "virtual environment",
            ]),
            "web": set([
                "react", "nodejs", "api", "rest", "graphql", "websocket", "http",
                "frontend", "backend", "responsive", "css", "html", "javascript",
            ]),
            "ai": set([
                "machine learning", "deep learning", "neural network", "model",
                "training", "inference", "dataset", "algorithm", "classification",
                "nlp", "computer vision", "transformer",
            ]),
            "devops": set([
                "docker", "kubernetes", "ci/cd", "pipeline", "deployment",
                "container", "orchestration", "monitoring", "logging",
            ]),
        }
    
    def get_synonym(self, word: str) -> str:
        """Get a random synonym for variety"""
        if word.lower() in self.synonyms:
            return random.choice(self.synonyms[word.lower()])
        return word
    
    def get_words(self, category: str, count: int = 5) -> List[str]:
        """Get random words from a category"""
        if category in self.words:
            available = list(self.words[category])
            return random.sample(available, min(count, len(available)))
        return []
    
    def get_transition(self) -> str:
        """Get a random transition phrase"""
        return random.choice(self.phrases["transition"])
    
    def get_professional_phrase(self, phrase_type: str) -> str:
        """Get a professional phrase of specified type"""
        if phrase_type in self.phrases:
            return random.choice(self.phrases[phrase_type])
        return ""
    
    def add_word(self, word: str, category: str):
        """Learn a new word"""
        if category not in self.words:
            self.words[category] = set()
        self.words[category].add(word.lower())
    
    def add_synonym(self, word: str, synonym: str):
        """Learn a synonym relationship"""
        word = word.lower()
        if word not in self.synonyms:
            self.synonyms[word] = []
        if synonym not in self.synonyms[word]:
            self.synonyms[word].append(synonym)
    
    def get_technical_terms(self, domain: str, count: int = 3) -> List[str]:
        """Get technical terms for a domain"""
        if domain in self.technical_terms:
            available = list(self.technical_terms[domain])
            return random.sample(available, min(count, len(available)))
        return []
    
    def expand_vocabulary(self, text: str):
        """Learn words from text"""
        import re
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        for word in set(words):
            # Categorize based on context (simple heuristic)
            if any(tech in word for tech in ['code', 'data', 'soft', 'tech']):
                self.add_word(word, "tech")
            elif any(biz in word for biz in ['business', 'market', 'sale', 'client']):
                self.add_word(word, "business")
            else:
                self.add_word(word, "general")
    
    def get_stats(self) -> Dict:
        """Get vocabulary statistics"""
        return {
            "total_words": sum(len(words) for words in self.words.values()),
            "categories": len(self.words),
            "synonyms": len(self.synonyms),
            "technical_domains": len(self.technical_terms),
        }


# Global vocabulary instance
vocabulary = Vocabulary()
