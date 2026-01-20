"""
Jephthah Content Engine
Generate articles, proposals, emails WITHOUT OpenAI API

This is the BRAIN - combines:
- Knowledge Graph (what Jephthah knows)
- Pattern Memory (how to structure content)
- Vocabulary (words to use)

Result: Self-sufficient content generation!
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

from loguru import logger

from brain.knowledge_graph import knowledge_graph
from brain.pattern_memory import pattern_memory
from brain.vocabulary import vocabulary


class ContentEngine:
    """
    Pure memory-based content generation.
    NO API CALLS NEEDED AFTER SUFFICIENT LEARNING!
    """
    
    def __init__(self):
        self.articles_generated = 0
        self.proposals_generated = 0
        self.emails_generated = 0
        logger.info("Content Engine initialized - 100% autonomous mode")
    
    # === ARTICLE GENERATION ===
    
    def generate_article(self, topic: str, word_count: int = 500) -> Dict:
        """Generate a complete article from memory"""
        logger.info(f"Generating article about: {topic}")
        
        # Get knowledge about the topic
        knowledge = knowledge_graph.get_knowledge_about(topic, depth=2)
        
        # Generate title
        title = self._generate_title(topic, knowledge)
        
        # Generate intro
        intro = self._generate_intro(topic, knowledge)
        
        # Generate body paragraphs
        paragraphs = []
        target_paragraphs = max(3, word_count // 150)
        
        for i in range(target_paragraphs):
            paragraph = self._generate_paragraph(topic, knowledge, i)
            if paragraph:
                paragraphs.append(paragraph)
        
        # Generate conclusion
        conclusion = self._generate_conclusion(topic, knowledge)
        
        # Assemble article
        article = f"{title}\n\n{intro}\n\n" + "\n\n".join(paragraphs) + f"\n\n{conclusion}"
        
        self.articles_generated += 1
        
        return {
            "title": title,
            "content": article,
            "word_count": len(article.split()),
            "topic": topic,
            "generated_at": datetime.utcnow().isoformat(),
            "used_api": False  # PURE MEMORY!
        }
    
    def _generate_title(self, topic: str, knowledge: Dict) -> str:
        """Generate article title"""
        templates = [
            f"The Ultimate Guide to {topic.title()}",
            f"Everything You Need to Know About {topic.title()}",
            f"{topic.title()}: A Comprehensive Overview",
            f"Mastering {topic.title()} in {random.randint(2026, 2027)}",
            f"Why {topic.title()} Matters for Your Business",
            f"{topic.title()} Explained: From Basics to Advanced",
        ]
        return random.choice(templates)
    
    def _generate_intro(self, topic: str, knowledge: Dict) -> str:
        """Generate introduction paragraph"""
        # Get intro pattern
        pattern = pattern_memory.get_random_pattern("intro", category="general")
        
        if pattern:
            # Fill placeholders
            intro = pattern.replace("{TOPIC}", topic)
            intro = intro.replace("{INDUSTRY}", random.choice(["tech", "business", "digital"]))
            intro = intro.replace("{PROBLEM}", f"understanding {topic}")
        else:
            # Fallback
            intro = f"In today's rapidly evolving landscape, {topic} has become increasingly important. "
            intro += f"Understanding {topic} can give you a competitive advantage. "
            intro += f"Let me share everything I've learned about {topic}."
        
        return intro
    
    def _generate_paragraph(self, topic: str, knowledge: Dict, index: int) -> str:
        """Generate a body paragraph"""
        paragraphs = []
        
        # Get body pattern
        pattern = pattern_memory.get_random_pattern("body", category="general")
        
        if pattern and knowledge.get("facts"):
            # Use facts from knowledge graph
            facts = knowledge["facts"][:3]
            for fact in facts:
                text = pattern.replace("{TOPIC}", topic)
                text = text.replace("{BENEFIT}", fact.get("value", "improved efficiency"))
                text = text.replace("{KEY_POINT}", fact.get("value", "core principles"))
                paragraphs.append(text)
        
        # Use related topics
        if knowledge.get("related_topics") and index < len(knowledge["related_topics"]):
            related = knowledge["related_topics"][index]
            text = f"One important aspect of {topic} is {related['name']}. "
            if related.get("description"):
                text += f"{related['description'][:100]}. "
            text += f"This {related.get('relationship', 'relates to')} {topic} in significant ways."
            paragraphs.append(text)
        
        # Fallback to general statements
        if not paragraphs:
            transition = vocabulary.get_transition()
            statement = f"{transition}, when working with {topic}, it's essential to understand the fundamentals. "
            statement += f"The key to success with {topic} is consistent practice and continuous learning."
            paragraphs.append(statement)
        
        return " ".join(paragraphs)
    
    def _generate_conclusion(self, topic: str, knowledge: Dict) -> str:
        """Generate conclusion paragraph"""
        pattern = pattern_memory.get_random_pattern("conclusion", category="general")
        
        if pattern:
            conclusion = pattern.replace("{TOPIC}", topic)
            conclusion = conclusion.replace("{AUDIENCE}", "developers and businesses")
            conclusion = conclusion.replace("{SUMMARY}", f"{topic} is a game-changer")
            conclusion = conclusion.replace("{RECOMMENDATION}", f"start learning {topic} today")
            conclusion = conclusion.replace("{ACTION}", "staying informed and practicing regularly")
        else:
            conclusion = f"In summary, {topic} represents a significant opportunity for growth. "
            conclusion += f"By mastering {topic}, you position yourself ahead of the curve. "
            conclusion += f"Start applying these concepts today and see the results for yourself."
        
        # Add CTA
        cta = pattern_memory.get_random_pattern("cta", category="general")
        if cta:
            conclusion += f" {cta.replace('{TOPIC}', topic)}"
        
        return conclusion
    
    # === PROPOSAL GENERATION ===
    
    def generate_proposal(self, job_description: str, job_type: str = "general") -> Dict:
        """Generate job proposal from memory"""
        logger.info(f"Generating proposal for {job_type} job")
        
        # Get proposal template
        template = pattern_memory.get_proposal_template(job_type)
        
        if not template:
            return self._fallback_proposal(job_description)
        
        # Extract key info from job description
        skills = self._extract_skills(job_description)
        
        # Fill template
        proposal = template.opening.replace("{JOB_SPECIFIC_HOOK}", f"the {job_type} requirements align perfectly with my expertise")
        proposal += "\n\n" + template.experience_section.replace("{YEARS}", "3+")
        proposal = proposal.replace("{SKILLS}", ", ".join(skills[:3]))
        proposal = proposal.replace("{RECENT_PROJECT}", f"delivered a {job_type} solution for a client")
        
        proposal += "\n\n" + template.approach_section.replace("{FIRST_STEP}", "analyzing requirements")
        proposal = proposal.replace("{SECOND_STEP}", "building a robust solution")
        proposal = proposal.replace("{BENEFIT}", "timely delivery and quality")
        
        proposal += "\n\n" + template.closing
        
        self.proposals_generated += 1
        
        return {
            "proposal": proposal,
            "job_type": job_type,
            "template_id": template.id,
            "generated_at": datetime.utcnow().isoformat(),
            "used_api": False
        }
    
    def _extract_skills(self, job_description: str) -> List[str]:
        """Extract skills from job description"""
        common_skills = ["Python", "JavaScript", "React", "Node.js", "Django", "Flask",
                        "AWS", "Docker", "API", "Database", "Git", "Agile"]
        
        found_skills = []
        job_lower = job_description.lower()
        
        for skill in common_skills:
            if skill.lower() in job_lower:
                found_skills.append(skill)
        
        return found_skills or ["web development", "software engineering", "problem solving"]
    
    def _fallback_proposal(self, job_description: str) -> Dict:
        """Fallback proposal when no template"""
        proposal = "Hi! I'm excited about this opportunity.\n\n"
        proposal += "I have extensive experience in software development and have successfully completed similar projects. "
        proposal += "I can deliver high-quality work within your timeline.\n\n"
        proposal += "Let's discuss the details. I'm ready to start immediately!"
        
        return {
            "proposal": proposal,
            "job_type": "general",
            "generated_at": datetime.utcnow().isoformat(),
            "used_api": False
        }
    
    # === EMAIL GENERATION ===
    
    def generate_email(self, email_type: str, context: Dict = None) -> Dict:
        """Generate email from memory"""
        logger.info(f"Generating {email_type} email")
        
        context = context or {}
        
        # Get email pattern
        pattern = pattern_memory.get_email_pattern(email_type)
        
        if not pattern:
            return self._fallback_email(email_type, context)
        
        # Generate subject
        subject = pattern.subject_pattern.replace("{BENEFIT}", context.get("benefit", "growth"))
        subject = subject.replace("{BUSINESS_TYPE}", context.get("business_type", "company"))
        subject = subject.replace("{TOPIC}", context.get("topic", "collaboration"))
        
        # Generate body
        body = pattern.greeting.replace("{NAME}", context.get("name", "there")) + "\n\n"
        
        # Add body paragraphs
        if isinstance(pattern.body_structure, list):
            for para_template in pattern.body_structure:
                para = para_template.replace("{OBSERVATION_ABOUT_COMPANY}", 
                                            context.get("observation", "your impressive work"))
                para = para.replace("{VALUE_PROPOSITION}", 
                                   context.get("value", "achieve your goals faster"))
                para = para.replace("{SIMILAR_CLIENT}", context.get("client", "a recent client"))
                para = para.replace("{RESULT}", context.get("result", "20% growth"))
                para = para.replace("{TOPIC}", context.get("topic", "this opportunity"))
                para = para.replace("{NEW_VALUE_ADD}", 
                                   context.get("value_add", "I have new insights to share"))
                body += para + "\n\n"
        
        # Add closing
        body += pattern.closing
        
        self.emails_generated += 1
        
        return {
            "subject": subject,
            "body": body,
            "email_type": email_type,
            "pattern_id": pattern.id,
            "generated_at": datetime.utcnow().isoformat(),
            "used_api": False
        }
    
    def _fallback_email(self, email_type: str, context: Dict) -> Dict:
        """Fallback email when no pattern"""
        if email_type == "cold_email":
            subject = "Quick question"
            body = f"Hi {context.get('name', 'there')},\n\n"
            body += "I came across your company and was impressed. "
            body += "I'd love to discuss how I can help.\n\n"
            body += "Best,\nJephthah"
        else:
            subject = "Following up"
            body = f"Hi {context.get('name', 'there')},\n\n"
            body += "I wanted to follow up on my previous message.\n\n"
            body += "Thanks,\nJephthah"
        
        return {
            "subject": subject,
            "body": body,
            "email_type": email_type,
            "generated_at": datetime.utcnow().isoformat(),
            "used_api": False
        }
    
    # === LEARNING & IMPROVEMENT ===
    
    def learn_from_success(self, content_type: str, item_id: int, success: bool):
        """Learn from successful/failed content"""
        if content_type == "article":
            # Would update article template success scores
            pass
        elif content_type == "proposal":
            if success:
                pattern_memory.record_proposal_win(item_id)
        elif content_type == "email":
            pattern_memory.record_email_response(item_id, success)
        
        logger.info(f"Learned from {content_type}: {' success' if success else 'failure'}")
    
    def get_stats(self) -> Dict:
        """Get content generation statistics"""
        kg_stats = knowledge_graph.get_stats()
        pm_stats = pattern_memory.get_stats()
        vocab_stats = vocabulary.get_stats()
        
        return {
            "articles_generated": self.articles_generated,
            "proposals_generated": self.proposals_generated,
            "emails_generated": self.emails_generated,
            "knowledge": kg_stats,
            "patterns": pm_stats,
            "vocabulary": vocab_stats,
            "api_dependent": False,  # NO MORE API NEEDED!
        }


# Global content engine instance
content_engine = ContentEngine()
