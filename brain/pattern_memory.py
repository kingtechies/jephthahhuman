"""
Jephthah Pattern Memory
Stores and learns patterns for content generation without API

This allows Jephthah to:
- Store successful sentence patterns
- Learn article/proposal/email templates
- Generate new content from patterns
- Improve patterns based on success
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from config.settings import DATA_DIR

Base = declarative_base()


class SentencePattern(Base):
    """A reusable sentence structure"""
    __tablename__ = "sentence_patterns"
    
    id = Column(Integer, primary_key=True)
    pattern = Column(Text)  # Template with {PLACEHOLDERS}
    pattern_type = Column(String(50), index=True)  # intro, body, conclusion, hook, cta
    category = Column(String(100), index=True)  # tech, business, freelancing, general
    tone = Column(String(50))  # professional, casual, persuasive, informative
    success_score = Column(Float, default=0.5)  # 0-1 how successful this pattern is
    usage_count = Column(Integer, default=0)
    source = Column(String(255))  # Where learned from
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ArticleTemplate(Base):
    """A learned article structure"""
    __tablename__ = "article_templates"
    
    id = Column(Integer, primary_key=True)
    title_pattern = Column(Text)  # Title template
    structure = Column(JSON)  # List of paragraph types/patterns
    topic_category = Column(String(100), index=True)  # technology, programming, ai, business
    word_count_target = Column(Integer, default=500)
    success_score = Column(Float, default=0.5)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProposalTemplate(Base):
    """A learned job proposal structure"""
    __tablename__ = "proposal_templates"
    
    id = Column(Integer, primary_key=True)
    opening = Column(Text)  # Opening hook
    experience_section = Column(Text)  # How to mention experience
    approach_section = Column(Text)  # How to describe approach
    closing = Column(Text)  # Call to action
    job_type = Column(String(100), index=True)  # web_dev, python, ai, mobile
    success_score = Column(Float, default=0.5)  # Based on win rate
    usage_count = Column(Integer, default=0)
    wins = Column(Integer, default=0)  # Jobs won using this template
    created_at = Column(DateTime, default=datetime.utcnow)


class EmailPattern(Base):
    """A learned email pattern"""
    __tablename__ = "email_patterns"
    
    id = Column(Integer, primary_key=True)
    subject_pattern = Column(Text)
    greeting = Column(Text)
    body_structure = Column(JSON)  # List of paragraph patterns
    closing = Column(Text)
    email_type = Column(String(100), index=True)  # cold_email, follow_up, reply, thank_you
    success_score = Column(Float, default=0.5)
    response_rate = Column(Float, default=0.0)  # Percentage that got responses
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PatternMemory:
    """
    Pattern-based memory for generating content without API.
    Learns from successful outputs and improves over time.
    """
    
    def __init__(self):
        db_path = DATA_DIR / "patterns.db"
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize with base patterns if empty
        self._init_base_patterns()
        logger.info(f"Pattern Memory initialized at {db_path}")
    
    def _init_base_patterns(self):
        """Initialize with fundamental patterns if database is empty"""
        session = self.Session()
        try:
            if session.query(SentencePattern).count() == 0:
                base_patterns = [
                    # INTRO patterns
                    ("In today's fast-paced {INDUSTRY} landscape, {TOPIC} has become essential.", "intro", "general", "professional"),
                    ("Are you struggling with {PROBLEM}? You're not alone.", "intro", "general", "persuasive"),
                    ("Let me share what I've learned about {TOPIC} in my journey as a developer.", "intro", "tech", "casual"),
                    ("The future of {TOPIC} is here, and it's changing everything.", "intro", "tech", "professional"),
                    ("{TOPIC} is not just a buzzword—it's a fundamental shift in how we work.", "intro", "business", "professional"),
                    
                    # BODY patterns
                    ("One of the key benefits of {TOPIC} is {BENEFIT}.", "body", "general", "informative"),
                    ("When I first started with {TOPIC}, I made the mistake of {MISTAKE}. Here's what I learned.", "body", "general", "casual"),
                    ("According to my experience, {CLAIM} because {REASON}.", "body", "general", "professional"),
                    ("The most important thing to understand about {TOPIC} is {KEY_POINT}.", "body", "general", "informative"),
                    ("What sets {TOPIC} apart from alternatives is {DIFFERENTIATOR}.", "body", "tech", "professional"),
                    
                    # CONCLUSION patterns
                    ("In conclusion, {TOPIC} offers tremendous value for {AUDIENCE}.", "conclusion", "general", "professional"),
                    ("Ready to get started? Here's my recommendation: {RECOMMENDATION}.", "conclusion", "general", "persuasive"),
                    ("The bottom line is simple: {SUMMARY}.", "conclusion", "general", "casual"),
                    ("Moving forward, {TOPIC} will continue to evolve, and staying ahead means {ACTION}.", "conclusion", "tech", "professional"),
                    
                    # HOOK patterns
                    ("What if I told you that {SURPRISING_FACT}?", "hook", "general", "persuasive"),
                    ("90% of people get {TOPIC} wrong. Here's why.", "hook", "general", "casual"),
                    ("I've spent {TIME_PERIOD} mastering {TOPIC}, and this is what matters.", "hook", "general", "professional"),
                    
                    # CTA patterns
                    ("Let's connect and discuss how {TOPIC} can help your business.", "cta", "business", "professional"),
                    ("Follow me for more insights on {TOPIC}.", "cta", "general", "casual"),
                    ("Questions? Drop a comment below or DM me.", "cta", "general", "casual"),
                ]
                
                for pattern, ptype, category, tone in base_patterns:
                    p = SentencePattern(
                        pattern=pattern,
                        pattern_type=ptype,
                        category=category,
                        tone=tone,
                        source="base"
                    )
                    session.add(p)
                
                session.commit()
                logger.info(f"Initialized {len(base_patterns)} base sentence patterns")
            
            # Initialize proposal templates
            if session.query(ProposalTemplate).count() == 0:
                base_proposals = [
                    {
                        "opening": "Hi! I read your job description carefully and I'm excited about this opportunity. {JOB_SPECIFIC_HOOK}",
                        "experience_section": "I have {YEARS} years of experience in {SKILLS}. Recently, I {RECENT_PROJECT}.",
                        "approach_section": "For your project, I would start by {FIRST_STEP}, then {SECOND_STEP}. My approach ensures {BENEFIT}.",
                        "closing": "I'd love to discuss this further. When would be a good time to chat?",
                        "job_type": "general"
                    },
                    {
                        "opening": "Your project caught my attention because {SPECIFIC_REASON}. I can help you achieve {GOAL}.",
                        "experience_section": "My background includes {EXPERIENCE}. I've successfully completed similar projects like {EXAMPLE}.",
                        "approach_section": "Here's how I would approach this: {DETAILED_APPROACH}",
                        "closing": "Ready to start immediately. Let's discuss the details!",
                        "job_type": "web_dev"
                    },
                    {
                        "opening": "I specialize in {SPECIALTY} and this is exactly what you need for {PROJECT_GOAL}.",
                        "experience_section": "With my expertise in {TECH_STACK}, I've helped clients {ACHIEVEMENT}.",
                        "approach_section": "I'll deliver {DELIVERABLE} within {TIMELINE}. My process includes {PROCESS}.",
                        "closing": "Let's make this happen. Available to start today.",
                        "job_type": "python"
                    }
                ]
                
                for template in base_proposals:
                    p = ProposalTemplate(**template)
                    session.add(p)
                
                session.commit()
                logger.info(f"Initialized {len(base_proposals)} proposal templates")
            
            # Initialize email patterns
            if session.query(EmailPattern).count() == 0:
                base_emails = [
                    {
                        "subject_pattern": "{BENEFIT} for your {BUSINESS_TYPE}",
                        "greeting": "Hi {NAME},",
                        "body_structure": [
                            "I noticed {OBSERVATION_ABOUT_COMPANY}.",
                            "I help businesses like yours {VALUE_PROPOSITION}.",
                            "Recently, I helped {SIMILAR_CLIENT} achieve {RESULT}."
                        ],
                        "closing": "Would you be open to a quick chat this week?\n\nBest,\nJephthah",
                        "email_type": "cold_email"
                    },
                    {
                        "subject_pattern": "Following up on {TOPIC}",
                        "greeting": "Hi {NAME},",
                        "body_structure": [
                            "I wanted to follow up on my previous message about {TOPIC}.",
                            "I understand you're busy, so I'll keep this brief.",
                            "{NEW_VALUE_ADD}"
                        ],
                        "closing": "Happy to answer any questions.\n\nCheers,\nJephthah",
                        "email_type": "follow_up"
                    }
                ]
                
                for template in base_emails:
                    body_json = json.dumps(template.pop("body_structure"))
                    template["body_structure"] = body_json
                    e = EmailPattern(**template)
                    e.body_structure = json.loads(body_json)  # Store as JSON
                    session.add(e)
                
                session.commit()
                logger.info(f"Initialized {len(base_emails)} email patterns")
                
        finally:
            session.close()
    
    # === SENTENCE PATTERNS ===
    
    def add_sentence_pattern(self, pattern: str, pattern_type: str, 
                            category: str = "general", tone: str = "professional",
                            source: str = "learned") -> int:
        """Add a new sentence pattern"""
        session = self.Session()
        try:
            p = SentencePattern(
                pattern=pattern,
                pattern_type=pattern_type,
                category=category,
                tone=tone,
                source=source
            )
            session.add(p)
            session.commit()
            return p.id
        finally:
            session.close()
    
    def get_patterns(self, pattern_type: str = None, category: str = None,
                    tone: str = None, limit: int = 10) -> List[SentencePattern]:
        """Get sentence patterns with optional filters"""
        session = self.Session()
        try:
            query = session.query(SentencePattern)
            if pattern_type:
                query = query.filter_by(pattern_type=pattern_type)
            if category:
                query = query.filter_by(category=category)
            if tone:
                query = query.filter_by(tone=tone)
            
            return query.order_by(SentencePattern.success_score.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_random_pattern(self, pattern_type: str, category: str = None) -> Optional[str]:
        """Get a random pattern of a specific type"""
        patterns = self.get_patterns(pattern_type=pattern_type, category=category, limit=20)
        if patterns:
            # Weight by success score
            weights = [p.success_score for p in patterns]
            selected = random.choices(patterns, weights=weights, k=1)[0]
            
            # Update usage count
            session = self.Session()
            try:
                p = session.query(SentencePattern).filter_by(id=selected.id).first()
                if p:
                    p.usage_count += 1
                    session.commit()
            finally:
                session.close()
            
            return selected.pattern
        return None
    
    def update_pattern_success(self, pattern_id: int, success: bool):
        """Update pattern success score based on outcome"""
        session = self.Session()
        try:
            p = session.query(SentencePattern).filter_by(id=pattern_id).first()
            if p:
                if success:
                    p.success_score = min(1.0, p.success_score + 0.05)
                else:
                    p.success_score = max(0.1, p.success_score - 0.03)
                session.commit()
        finally:
            session.close()
    
    # === PROPOSAL TEMPLATES ===
    
    def get_proposal_template(self, job_type: str = "general") -> Optional[ProposalTemplate]:
        """Get best proposal template for job type"""
        session = self.Session()
        try:
            template = session.query(ProposalTemplate).filter_by(
                job_type=job_type
            ).order_by(ProposalTemplate.success_score.desc()).first()
            
            if not template:
                template = session.query(ProposalTemplate).filter_by(
                    job_type="general"
                ).first()
            
            if template:
                template.usage_count += 1
                session.commit()
            
            return template
        finally:
            session.close()
    
    def record_proposal_win(self, template_id: int):
        """Record that a proposal won a job"""
        session = self.Session()
        try:
            t = session.query(ProposalTemplate).filter_by(id=template_id).first()
            if t:
                t.wins += 1
                t.success_score = min(1.0, t.success_score + 0.1)
                session.commit()
        finally:
            session.close()
    
    # === EMAIL PATTERNS ===
    
    def get_email_pattern(self, email_type: str) -> Optional[EmailPattern]:
        """Get best email pattern for type"""
        session = self.Session()
        try:
            pattern = session.query(EmailPattern).filter_by(
                email_type=email_type
            ).order_by(EmailPattern.success_score.desc()).first()
            
            if pattern:
                pattern.usage_count += 1
                session.commit()
            
            return pattern
        finally:
            session.close()
    
    def record_email_response(self, pattern_id: int, got_response: bool):
        """Record email response for pattern improvement"""
        session = self.Session()
        try:
            p = session.query(EmailPattern).filter_by(id=pattern_id).first()
            if p:
                total = p.usage_count or 1
                current_responses = int(p.response_rate * total)
                if got_response:
                    current_responses += 1
                    p.success_score = min(1.0, p.success_score + 0.1)
                p.response_rate = current_responses / (total + 1)
                session.commit()
        finally:
            session.close()
    
    # === LEARNING FROM CONTENT ===
    
    def learn_from_article(self, article_text: str, source: str = "web"):
        """Extract and store patterns from an article"""
        sentences = article_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 200:
                continue
            
            # Detect pattern type by position and keywords
            if any(w in sentence.lower() for w in ['introduction', 'welcome', 'today', 'let me']):
                pattern_type = "intro"
            elif any(w in sentence.lower() for w in ['conclusion', 'finally', 'in summary', 'bottom line']):
                pattern_type = "conclusion"
            elif any(w in sentence.lower() for w in ['connect', 'follow', 'subscribe', 'contact']):
                pattern_type = "cta"
            else:
                pattern_type = "body"
            
            # Generalize the sentence into a pattern
            generalized = self._generalize_sentence(sentence)
            if generalized:
                self.add_sentence_pattern(
                    pattern=generalized,
                    pattern_type=pattern_type,
                    category="general",
                    source=source
                )
    
    def _generalize_sentence(self, sentence: str) -> Optional[str]:
        """Convert a specific sentence into a reusable pattern"""
        import re
        
        # Replace specific numbers with placeholder
        pattern = re.sub(r'\d+', '{NUMBER}', sentence)
        
        # Replace specific technologies with placeholder
        tech_terms = ['python', 'javascript', 'react', 'nodejs', 'django', 'flask', 'ai', 'ml']
        for tech in tech_terms:
            pattern = re.sub(rf'\b{tech}\b', '{TECHNOLOGY}', pattern, flags=re.IGNORECASE)
        
        # Replace URLs
        pattern = re.sub(r'https?://\S+', '{URL}', pattern)
        
        # Only return if it has at least one placeholder
        if '{' in pattern:
            return pattern
        return None
    
    # === STATISTICS ===
    
    def get_stats(self) -> Dict:
        """Get pattern memory statistics"""
        session = self.Session()
        try:
            return {
                "sentence_patterns": session.query(SentencePattern).count(),
                "article_templates": session.query(ArticleTemplate).count(),
                "proposal_templates": session.query(ProposalTemplate).count(),
                "email_patterns": session.query(EmailPattern).count(),
                "best_patterns": [
                    p.pattern[:50] + "..." for p in session.query(SentencePattern).order_by(
                        SentencePattern.success_score.desc()
                    ).limit(5).all()
                ]
            }
        finally:
            session.close()


# Global pattern memory instance
pattern_memory = PatternMemory()
